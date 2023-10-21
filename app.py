import streamlit as st
import openai
import clipboard
from streamlit.logger import get_logger
from utils import summary_generator


LOGGER = get_logger(__name__)


def on_copy_click(text):
    st.session_state.copied.append(text)
    clipboard.copy(text)


def main():
    st.title("Fantasy Football Weekly Summary Generator")

    st.write("""
    ## Instructions:
    1. Select your league type from the sidebar.
    2. Fill out the required fields based on your league selection.
    3. Hit "Generate AI Summary" to get your weekly summary.
    """)

    with st.sidebar:
        st.header("Input Form")
        league_type = st.selectbox("Select League Type", ["Select", "ESPN", "Yahoo"], key='league_type')

    if league_type != "Select":
        with st.sidebar.form(key='my_form'):
            if league_type == "ESPN":
                st.text_input("LeagueID", key='LeagueID')
                st.text_input("SWID", key='SWID')
                st.text_input("ESPN2_Id", key='ESPN2_Id')
            elif league_type == "Yahoo":
                st.text_input("LeagueID", key='LeagueID')
            
            st.text_input("Character Description", key='Character Description')
            st.slider("Trash Talk Level", 1, 10, key='Trash Talk Level')
            submit_button = st.form_submit_button(label='Generate AI Summary')

    
        # Handling form 
        if submit_button:
            if league_type == "ESPN":
                required_fields = ['LeagueID', 'SWID', 'ESPN2_Id', 'Character Description', 'Trash Talk Level']
            else:
                required_fields = ['LeagueID', 'Character Description', 'Trash Talk Level']
            
            if all(st.session_state.get(field, None) for field in required_fields):
                league_id = st.session_state.get('LeagueID', 'Not provided')
                character_description = st.session_state.get('Character Description', 'Not provided')
                trash_talk_level = st.session_state.get('Trash Talk Level', 'Not provided')
                swid = st.session_state.get('SWID', 'Not provided')
                espn2 = st.session_state.get('ESPN2_Id', 'Not provided')
                
                st.write(f'League Type: {league_type}')
                st.write(f'LeagueID: {league_id}')
                st.write(f'SWID: {swid}')
                st.write(f'ESPN2_Id: {espn2}')
                st.write(f'Character Description: {character_description}')
                st.write(f'Trash Talk Level: {trash_talk_level}')

                # Fetch open ai key
                openai_api_key=st.secrets["openai_api_key"]
                openai.api_key=openai_api_key

                summary, debug_info = summary_generator.get_espn_league_summary(
                    league_id, espn2, swid 
                )

                st.write(f'ESPN Summary: {summary}')
                st.write(f'Debug Info: {debug_info}')

                gpt4_summary_stream = summary_generator.generate_gpt4_summary_streaming(
                    summary, character_description, trash_talk_level
                )

                with st.chat_message("Commish"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in gpt4_summary_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    if len(st.session_state.copied) > 5:
                        st.session_state.copied.pop(0)
                    st.button("📋", on_click=on_copy_click, args=(full_response,))



    

if __name__ == "__main__":
    main()


