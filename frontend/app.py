import streamlit as st
import asyncio
from utils.api_client import APIClient, APIError
from utils.helpers import (
    init_session_state,
    display_chat_history,
    display_error,
    display_loading,
    display_profile_form,
    display_matches,
    get_chat_input
)

# Page config
st.set_page_config(
    page_title="Date Mate",
    page_icon="❤️",
    layout="wide"
)

# Initialize API client
api_client = APIClient()

# Initialize session state
init_session_state()

def main():
    st.title("❤️ Date Mate")
    st.write("Your AI Dating Advisor and Matchmaker")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Profile", "Chat with Advisor", "Practice Chat", "Find Matches"]
    )
    
    if page == "Profile":
        st.header("Your Dating Profile")
        
        try:
            # Get current profile if it exists
            current_profile = asyncio.run(
                api_client.get_profile(st.session_state.user_id)
            )
        except APIError:
            current_profile = None
        
        # Display profile form
        profile_data = display_profile_form(current_profile)
        
        if profile_data:
            with display_loading("Saving profile..."):
                try:
                    asyncio.run(
                        api_client.update_profile(st.session_state.user_id, profile_data)
                    )
                    st.session_state.profile_complete = True
                    st.success("Profile saved successfully!")
                except APIError as e:
                    display_error(str(e))
    
    elif page == "Chat with Advisor":
        st.header("Dating Advisor")
        
        if not st.session_state.profile_complete:
            st.warning("Please complete your profile first!")
            return
        
        # Display chat interface
        display_chat_history(st.session_state.chat_history)
        
        message = get_chat_input()
        if message:
            with display_loading("Getting advice..."):
                try:
                    response = asyncio.run(
                        api_client.chat_with_advisor(message, st.session_state.user_id)
                    )
                    st.session_state.chat_history = response["chat_history"]
                    st.experimental_rerun()
                except APIError as e:
                    display_error(str(e))
    
    elif page == "Practice Chat":
        st.header("Practice Chat")
        
        if not st.session_state.profile_complete:
            st.warning("Please complete your profile first!")
            return
        
        # Display chat interface
        display_chat_history(st.session_state.chat_history)
        
        message = get_chat_input()
        if message:
            with display_loading("Getting response..."):
                try:
                    response = asyncio.run(
                        api_client.chat_with_partner(message, st.session_state.user_id)
                    )
                    st.session_state.chat_history = response["chat_history"]
                    st.experimental_rerun()
                except APIError as e:
                    display_error(str(e))
    
    elif page == "Find Matches":
        st.header("Find Matches")
        
        if not st.session_state.profile_complete:
            st.warning("Please complete your profile first!")
            return
        
        min_score = st.slider("Minimum Match Score", 0, 100, 50)
        limit = st.number_input("Number of Matches", min_value=1, max_value=50, value=10)
        
        if st.button("Find Matches"):
            with display_loading("Finding matches..."):
                try:
                    matches = asyncio.run(
                        api_client.get_matches(
                            st.session_state.user_id,
                            min_score=min_score,
                            limit=limit
                        )
                    )
                    if matches:
                        display_matches(matches)
                    else:
                        st.info("No matches found. Try adjusting your criteria.")
                except APIError as e:
                    display_error(str(e))

if __name__ == "__main__":
    main()