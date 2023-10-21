import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def main():
    st.title("Fantasy Football Weekly Summary Generator")
    
    # Instructions in the main section
    st.write("""
    ## Instructions:
    1. Select your league type from the sidebar.
    2. Fill out the required fields based on your league selection.
    3. Hit "Generate AI Summary" to get your weekly summary.
    """)
    
    # Sidebar Form
    with st.sidebar.form(key='my_form'):
        st.header("Input Form")
        league_type = st.selectbox("Select League Type", ["Select", "ESPN", "Yahoo"])
        
        # Initializing Session State variables
        if 'user_data' not in st.session_state:
            st.session_state['user_data'] = {}
        
        if league_type == "ESPN":
            st.session_state.user_data['LeagueID'] = st.text_input("LeagueID")
            st.session_state.user_data['WSID'] = st.text_input("WSID")
            st.session_state.user_data['ESPN2_Id'] = st.text_input("ESPN2_Id")
        elif league_type == "Yahoo":
            st.session_state.user_data['LeagueID'] = st.text_input("LeagueID")
        
        st.session_state.user_data['Character Description'] = st.text_input("Character Description")
        st.session_state.user_data['Trash Talk Level'] = st.slider("Trash Talk Level", 1, 10)
        
        submit_button = st.form_submit_button(label='Generate AI Summary')

        # Ensure to handle the case when the form is submitted without all required fields filled.
        if submit_button and all(field in st.session_state.user_data for field in ['LeagueID', 'Character Description', 'Trash Talk Level']):
            # Add your backend logic here to fetch the summary based on st.session_state.user_data
            pass

if __name__ == "__main__":
    main()
