import streamlit as st
import openai
from streamlit.logger import get_logger
from utils import summary_generator
from utils.helper import check_availability
from utils.yahoo_auth import authenticate_yahoo, cleanup_temp_dir
import traceback

LOGGER = get_logger(__name__)


st.set_page_config(
    page_title="Commish.ai",
    page_icon="🏈",
    layout="centered",
    initial_sidebar_state="expanded"
)

def main():
    st.write("""
    ## Instructions:

    1. **Select your league type** from the sidebar.
    2. **Fill out the required fields** based on your league selection:
    - **ESPN**:
        - *League ID*: [Find it here](https://support.espn.com/hc/en-us/articles/360045432432-League-ID).
        - *SWID and ESPN_S2*: Use this [Chrome extension](https://chrome.google.com/webstore/detail/espn-private-league-key-a/bakealnpgdijapoiibbgdbogehhmaopn) or follow [manual steps](https://www.gamedaybot.com/help/espn_s2-and-swid/).
    - **Yahoo**:
        - *League ID*: Navigate to Yahoo Fantasy Sports → Click your league → Mouse over **League**, click **Settings**. The League ID number is listed first.
    - **Sleeper**:
        - *League ID*: [Find it here](https://support.sleeper.com/en/articles/4121798-how-do-i-find-my-league-id). 
    3. **Hit "🤖 Generate AI Summary"** to get your weekly summary.
    """)


    with st.sidebar:
        st.sidebar.image('logo.png', use_column_width=True)
        is_available, today = check_availability()
        if is_available:
            st.success(f"Today is {today}. The most recent week is completed and a recap is available.")
        else:
            st.warning(
                "Recaps are best generated between Tuesday 4am EST and Thursday 7pm EST. "
                "Please come back during this time for the most accurate recap."
            )
        league_type = st.selectbox("Select League Type", ["Select", "ESPN", "Yahoo", "Sleeper"], key='league_type')

    if league_type != "Select":
        with st.sidebar.form(key='my_form'):
            if league_type == "ESPN":
                st.text_input("LeagueID", key='LeagueID')
                st.text_input("SWID", key='SWID')
                st.text_input("ESPN_S2", key='ESPN2_Id')
            elif league_type == "Yahoo":
                st.text_input("LeagueID", key='LeagueID')
            elif league_type == "Sleeper":
                st.text_input("LeagueID", key='LeagueID')
            
            st.text_input("Character Description", key='Character Description', placeholder="Dwight Schrute", help= "Describe a persona for the AI to adopt. E.g. 'Dwight Schrute' or 'A very drunk Captain Jack Sparrow'")
            st.slider("Trash Talk Level", 1, 10, key='Trash Talk Level', value=5, help="Scale of 1 to 10, where 1 is friendly banter and 10 is more extreme trash talk")
            submit_button = st.form_submit_button(label='🤖 Generate AI Summary')

    
        # Handling form 
        if submit_button:
            try:
                progress = st.progress(0)
                progress.text('Starting...')
                
                required_fields = ['LeagueID', 'Character Description', 'Trash Talk Level']
                if league_type == "ESPN":
                    required_fields.extend(['SWID', 'ESPN2_Id'])
                
                # Input validation
                progress.text('Validating credentials...')
                progress.progress(5)
                for field in required_fields:
                    value = st.session_state.get(field, None)
                    if not value:
                        st.error(f"{field} is required.")
                        return  # Stop execution if any required field is empty
                
                league_id = st.session_state.get('LeagueID', 'Not provided')
                character_description = st.session_state.get('Character Description', 'Not provided')
                trash_talk_level = st.session_state.get('Trash Talk Level', 'Not provided')
                swid = st.session_state.get('SWID', 'Not provided')
                espn2 = st.session_state.get('ESPN2_Id', 'Not provided')
                
                # Fetch open ai key
                openai_api_key = st.secrets["openai_api_key"]
                openai.api_key = openai_api_key

                # Moderate the character description
                progress.text('Validating character...')
                progress.progress(15)
                if not summary_generator.moderate_text(character_description):
                    st.error("The character description contains inappropriate content. Please try again.")
                    return  # Stop execution if moderation fails
                
                # Fetching league summary
                progress.text('Fetching league summary...')
                progress.progress(30)
                if league_type == "ESPN":
                    summary, debug_info = summary_generator.get_espn_league_summary(
                        league_id, espn2, swid 
                    )
                elif league_type == "Yahoo":
                    # auth_directory = "auth"
                    auth_directory, access_token, refresh_token = authenticate_yahoo()
                    # summary = summary_generator.get_yahoo_league_summary(
                    #     league_id, auth_directory
                    # )
                    if auth_directory:
                        summary = summary_generator.get_yahoo_league_summary(league_id, auth_directory)
                        cleanup_temp_dir(auth_directory)
                    else:
                        st.error("Authentication failed. Please try again.")
                elif league_type == "Sleeper":
                    auth_directory = "auth"
                    summary = summary_generator.generate_sleeper_summary(
                        league_id
                    )
                
                progress.text('Generating AI summary...')
                progress.progress(50)
                gpt4_summary_stream = summary_generator.generate_gpt4_summary_streaming(
                    summary, character_description, trash_talk_level
                )
                
                with st.chat_message("Commish", avatar="🤖"):
                    message_placeholder = st.empty()
                    full_response = ""
                    progress.progress(70)
                    for chunk in gpt4_summary_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    
                    # Display the full response within a code block which provides a copy button
                    st.markdown("**Click the copy icon** 📋 below in top right corner to copy your summary and paste it wherever you see fit!")
                    st.code(full_response, language="")
                    st.markdown("Don't like this one? Try entering a **new character** and it will **start generating immediately**.")
                    
                progress.text('Done!')
                progress.progress(100)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                LOGGER.exception(e)
                st.text(traceback.format_exc())

if __name__ == "__main__":
    main()


