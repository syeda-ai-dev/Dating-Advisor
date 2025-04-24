import streamlit as st
from typing import List, Dict, Optional
import uuid

def init_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "profile_complete" not in st.session_state:
        st.session_state.profile_complete = False

def display_chat_history(chat_history: List[Dict]):
    """Display chat messages in a conversational format."""
    for message in chat_history:
        if message["role"] == "user":
            st.write(f'👤 You: {message["content"]}')
        else:
            st.write(f'🤖 AI: {message["content"]}')

def display_error(error_msg: str):
    """Display error message in UI."""
    st.error(f"Error: {error_msg}")

def display_loading(text: str = "Processing..."):
    """Display loading spinner with custom text."""
    return st.spinner(text)

def display_profile_form(current_profile: Optional[Dict] = None) -> Dict:
    """Display and handle profile form submission."""
    with st.form("profile_form"):
        name = st.text_input("Name", value=current_profile.get("name", "") if current_profile else "")
        age = st.number_input("Age", min_value=18, max_value=99, value=current_profile.get("age", 18) if current_profile else 18)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Other"], index=0 if not current_profile else ["Male", "Female", "Non-binary", "Other"].index(current_profile.get("gender", "Male")))
        interested_in = st.multiselect("Interested in", ["Male", "Female", "Non-binary", "Other"], default=current_profile.get("interested_in", []) if current_profile else [])
        
        relationship_goals = st.selectbox(
            "Relationship Goals",
            ["Long-term relationship", "Casual dating", "Friendship", "Marriage"],
            index=0 if not current_profile else ["Long-term relationship", "Casual dating", "Friendship", "Marriage"].index(current_profile.get("relationship_goals", "Long-term relationship"))
        )
        
        hobbies = st.text_area("Hobbies (one per line)", value="\n".join(current_profile.get("hobbies", [])) if current_profile else "")
        personality_traits = st.text_area("Personality Traits (one per line)", value="\n".join(current_profile.get("personality_traits", [])) if current_profile else "")
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            return {
                "name": name,
                "age": age,
                "gender": gender,
                "interested_in": interested_in,
                "relationship_goals": relationship_goals,
                "hobbies": [hobby.strip() for hobby in hobbies.split("\n") if hobby.strip()],
                "personality_traits": [trait.strip() for trait in personality_traits.split("\n") if trait.strip()],
                "values": current_profile.get("values", []) if current_profile else [],
                "languages": current_profile.get("languages", ["English"]) if current_profile else ["English"],
                "location": current_profile.get("location", "") if current_profile else "",
                "education": current_profile.get("education", "") if current_profile else "",
                "occupation": current_profile.get("occupation", "") if current_profile else "",
                "deal_breakers": current_profile.get("deal_breakers", []) if current_profile else [],
                "love_language": current_profile.get("love_language", "") if current_profile else "",
                "communication_style": current_profile.get("communication_style", "") if current_profile else "",
                "life_goals": current_profile.get("life_goals", []) if current_profile else [],
            }
    return None

def display_matches(matches: List[Dict]):
    """Display potential matches in a card format."""
    for match in matches:
        with st.expander(f"{match['profile']['name']} (Match Score: {match['match_score']}%)"):
            st.write(f"Age: {match['profile']['age']}")
            st.write(f"Gender: {match['profile']['gender']}")
            st.write(f"Relationship Goals: {match['profile']['relationship_goals']}")
            st.write("Hobbies:")
            for hobby in match['profile']['hobbies']:
                st.write(f"- {hobby}")
            st.write("Personality Traits:")
            for trait in match['profile']['personality_traits']:
                st.write(f"- {trait}")
            
def get_chat_input() -> str:
    """Get chat input from user."""
    return st.text_input("Type your message here:", key="chat_input")