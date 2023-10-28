import streamlit as st
import requests
import json
import tempfile
from requests.auth import HTTPBasicAuth
import time
import os
import shutil

# Client_ID and Secret from https://developer.yahoo.com/apps/
cid = st.secrets["YAHOO_CLIENT_ID"]
cse = st.secrets["YAHOO_CLIENT_SECRET"]

def authenticate_yahoo():
    # Ensure that the Client ID and Secret are set
    if cid is None or cse is None:
        st.error("Client ID or Client Secret is not set. Please set the YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET environment variables.")
        return None, None

    # URL for st button with Client ID in query string
    redirect_uri = "oob"
    auth_page = f'https://api.login.yahoo.com/oauth2/request_auth?client_id={cid}&redirect_uri={redirect_uri}&response_type=code'

    # Initialize session state variables
    if 'auth_code' not in st.session_state:
        st.session_state['auth_code'] = ''
    if 'access_token' not in st.session_state:
        st.session_state['access_token'] = ''
    if 'refresh_token' not in st.session_state:
        st.session_state['refresh_token'] = ''

    # Show instructions and get authorization code from user
    st.write("1. Click the link below to authenticate with Yahoo and get the authorization code.")
    st.write(f"[Authenticate with Yahoo]({auth_page})")
    st.write("2. Paste the authorization code here:")
    auth_code = st.text_input("Authorization Code")
    if auth_code:
        st.session_state['auth_code'] = auth_code
        st.success('Authorization code received!')

    # Get the token using authorization code
    if st.session_state['auth_code'] and not st.session_state['access_token']:
        basic = HTTPBasicAuth(cid, cse)
        _data = {
            'redirect_uri': redirect_uri,
            'code': st.session_state['auth_code'],
            'grant_type': 'authorization_code'
        }
        try:
            r = requests.post('https://api.login.yahoo.com/oauth2/get_token', data=_data, auth=basic)
            r.raise_for_status()  # Will raise an exception for HTTP errors
            token_data = r.json()
            st.session_state['access_token'] = token_data.get('access_token', '')
            st.session_state['refresh_token'] = token_data.get('refresh_token', '')
            st.success('Access token received!')
        except requests.exceptions.HTTPError as err:
            st.error(f"HTTP error occurred: {err}")
            return None, None
        except Exception as err:
            st.error(f"An error occurred: {err}")
            return None, None

    # Create a temporary directory to store the token and private files
    if st.session_state['access_token']:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define the paths to the token and private files
            token_file_path = temp_dir + "/token.json"
            private_file_path = temp_dir + "/private.json"

            # Create the token file with all necessary details
            token_data = {
                "access_token": st.session_state['access_token'],
                "consumer_key": cid,
                "consumer_secret": cse,
                "guid": None,
                "refresh_token": st.session_state['refresh_token'],
                "expires_in": 3600, 
                "token_time": time.time(),
                "token_type": "bearer"
            }
            with open(token_file_path, 'w') as f:
                json.dump(token_data, f)

            # Create the private file with consumer key and secret
            private_data = {
                "consumer_key": cid,
                "consumer_secret": cse,
            }
            with open(private_file_path, 'w') as f:
                json.dump(private_data, f)

            return temp_dir, st.session_state['access_token'], st.session_state['refresh_token']
        
    return None, None


def cleanup_temp_dir(temp_dir):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        st.info("Temporary directory cleaned up successfully.")
    else:
        st.warning("Temporary directory not found.")