# [Commish.ai](https://commish.streamlit.app/): AI-Powered Fantasy Football Recaps

Generate engaging weekly recaps for your Fantasy Football league with the help of AI 🤖.

- Supports **ESPN**, **Sleeper**, and **Yahoo** leagues.
- Powered by **OpenAI GPT-4**.
- Free to use!

## Usage

Best utilized between **Tuesday 4am EST and Thursday 7pm EST** during the standard "down-time" between fantasy weeks. Data will generally be forced to display for the most recent completed week. A notification will display green when recaps are ready and yellow when you're in the middle of active games (an incomplte week).

Getting your league ID is required for both ESPN and Yahoo. However, ESPN addtionally requires a SWID and ESPN_S2 id which can be collected with a simple chrome extension or manually by inspecting cookies in the browser:
- **ESPN**:
        - *League ID*: [Find it here](https://support.espn.com/hc/en-us/articles/360045432432-League-ID).
        - *SWID and ESPN_S2*: Use this [Chrome extension](https://chrome.google.com/webstore/detail/espn-private-league-key-a/bakealnpgdijapoiibbgdbogehhmaopn) or follow [manual steps](https://www.gamedaybot.com/help/espn_s2-and-swid/).
- **Yahoo**:
        - *League ID*: Navigate to Yahoo Fantasy Sports → Click your league → Mouse over **League**, click **Settings**. The League ID number is listed first.
        - *Authenticate*: Follow the prompt to enter your authentication code. Then fill in the character description and trash talk levels as your normally would.
- **Sleeper**:
        - *League ID*: [Find it here](https://support.sleeper.com/en/articles/4121798-how-do-i-find-my-league-id).

## Features

- Automated recap generation.
- Persona-based storytelling.
- Trash-talk meter to control the sassiness of the recap.

## Acknowledgements

- Special thanks to [espn-api](https://github.com/cwendt94/espn-api) and [yfpy](https://github.com/uberfastman/yfpy) for their fantastic Python wrappers.

## License

This project is open source under the MIT license.

[Visit Commish.ai](https://commish.streamlit.app/)
