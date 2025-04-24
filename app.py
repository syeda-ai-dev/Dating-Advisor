# app.py - Main Streamlit Application
import streamlit as st
import os
import uuid
from datetime import datetime
from groq import Groq
import json
from typing import Dict, List, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Configure page
st.set_page_config(
    page_title="Date Mate - Your Dating Advisor",
    page_icon="💌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "age": "",
        "gender": "",
        "interested_in": [],
        "relationship_goals": "",
        "hobbies": []
    }
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {
        "last_date_discussed": None,
        "last_match_suggested": None,
        "recent_topics": []
    }
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "chat"
if "matches" not in st.session_state:
    # Sample matches for now (would be retrieved from a DB in production)
    st.session_state.matches = [
        {
            "id": "match_1",
            "name": "Alex",
            "age": 28,
            "gender": "Non-binary",
            "interests": ["hiking", "cooking", "art galleries"],
            "compatibility": 85
        },
        {
            "id": "match_2",
            "name": "Jordan",
            "age": 31,
            "gender": "Female",
            "interests": ["rock climbing", "travel", "photography"],
            "compatibility": 79
        },
        {
            "id": "match_3",
            "name": "Taylor",
            "age": 26,
            "gender": "Male",
            "interests": ["reading", "coffee shops", "concerts"],
            "compatibility": 92
        }
    ]

# Define LangGraph state schema
class ChatState(dict):
    """Chat state schema for LangGraph."""
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    user_id: str

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found in environment variables.")
        st.stop()
    return Groq(api_key=api_key)

# System prompt for the dating advisor
DATING_ADVISOR_PROMPT = """
You are Date Mate, a friendly and insightful dating advisor. Your purpose is to help users navigate their dating life, 
offering advice, suggestions, and support.

Core features:
1. Provide personalized dating advice based on user's profile and preferences
2. Suggest conversation starters for dates
3. Help users understand dating patterns and behaviors
4. Offer supportive feedback on dating experiences
5. Suggest potential matches based on compatibility

Your tone should be:
- Warm and supportive: Dating makes people feel vulnerable
- Non-judgmental and inclusive: Avoid assumptions about preferences
- Playful but respectful: Use humor appropriately
- Empowering: Build user confidence
- Empathetic: Recognize emotions around dating
- Clear and practical: Provide actionable advice
- Adaptable: Match the user's mood appropriately

Always maintain a friendly, conversational tone while being thoughtful and insightful.
"""

# LangGraph functions
def initialize_state(user_id: str) -> ChatState:
    """Initialize the chat state."""
    return ChatState(
        messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
        context=st.session_state.conversation_context,
        user_id=user_id
    )

def add_user_message(state: ChatState, input: Dict[str, str]) -> ChatState:
    """Add a user message to the state.
    
    Args:
        state: The current chat state
        input: Dictionary containing the user message
    """
    message = input.get("message", "")
    state["messages"].append({"role": "user", "content": message})
    
    # Update context with simple topic tracking
    if "recent_topics" in state["context"]:
        # Very simple topic extraction - would be more sophisticated in production
        potential_topics = ["date", "match", "profile", "advice", "relationship"]
        for topic in potential_topics:
            if topic in message.lower() and len(state["context"]["recent_topics"]) < 5:
                if topic not in state["context"]["recent_topics"]:
                    state["context"]["recent_topics"].append(topic)
    
    return state

def generate_assistant_response(state: ChatState) -> ChatState:
    """Generate assistant response using Groq API."""    
    client = get_groq_client()
    
    try:
        response = client.chat.completions.create(
            messages=state["messages"],
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            temperature=0.7
        )
        assistant_message = response.choices[0].message.content
        state["messages"].append({"role": "assistant", "content": assistant_message})
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        state["messages"].append({"role": "assistant", "content": "I'm having trouble connecting right now. Please try again in a moment."})
    
    return state

def save_conversation(state: ChatState) -> ChatState:
    """Save conversation to session state."""    
    # Convert messages to proper format for display
    history = []
    for msg in state["messages"]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
        # Skip system messages for display
    
    # Update session state
    st.session_state.chat_history = history
    st.session_state.conversation_context = state["context"]
    
    return state

# Define chain components
def build_chat_chain():
    chain = RunnableSequence([
        RunnableLambda(add_user_message),
        RunnableLambda(generate_assistant_response),
        RunnableLambda(save_conversation)
    ])
    return chain

# Initialize the chain
chat_chain = build_chat_chain()

# UI Components
def render_sidebar():
    """Render the sidebar with navigation and user profile."""    
    with st.sidebar:
        st.title("💌 Date Mate")
        
        # Navigation
        st.subheader("Navigation")
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_tab = "chat"
        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.current_tab = "profile"
        if st.button("❤️ Matches", use_container_width=True):
            st.session_state.current_tab = "matches"
        if st.button("🔍 Dating Tips", use_container_width=True):
            st.session_state.current_tab = "tips"
        
        # User info
        st.divider()
        st.subheader("My Profile")
        if st.session_state.profile["name"]:
            st.write(f"Name: {st.session_state.profile['name']}")
            st.write(f"Age: {st.session_state.profile['age']}")
            st.write(f"Looking for: {st.session_state.profile['relationship_goals']}")
        else:
            st.write("Your profile is not complete. Please go to the Profile tab to set it up.")

def render_chat_tab():
    """Render the chat interface."""    
    st.header("💬 Chat with your Dating Advisor")
    
    # Display chat messages
    for i, msg in enumerate(st.session_state.chat_history):
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar="💌"):
                st.write(msg.content)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Initialize state if this is the first message
        if not st.session_state.chat_history:
            state = initialize_state(st.session_state.user_id)
        else:
            # Reconstruct state from session_state
            state = ChatState(
                messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                context=st.session_state.conversation_context,
                user_id=st.session_state.user_id
            )
            
            # Add previous messages
            for msg in st.session_state.chat_history:
                if isinstance(msg, HumanMessage):
                    state["messages"].append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    state["messages"].append({"role": "assistant", "content": msg.content})
        
        # Process through chain
        final_state = chat_chain.run({"message": user_input, "state": state})
        
        # Force a rerun to display the new messages
        st.rerun()

def render_profile_tab():
    """Render the profile editing interface."""    
    st.header("👤 My Profile")
    
    profile = st.session_state.profile
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name", value=profile["name"])
        age = st.number_input("Age", min_value=18, max_value=99, value=int(profile["age"]) if profile["age"] else 25)
        gender = st.selectbox(
            "Gender", 
            ["", "Male", "Female", "Non-binary", "Other"], 
            index=0 if not profile["gender"] else ["", "Male", "Female", "Non-binary", "Other"].index(profile["gender"])
        )
    
    with col2:
        interested_in = st.multiselect(
            "Interested in (select all that apply)",
            ["Men", "Women", "Non-binary people", "Everyone"],
            default=profile["interested_in"]
        )
        
        relationship_goals = st.selectbox(
            "Relationship goals",
            ["", "Casual dating", "Long-term relationship", "Marriage", "Friendship first", "Not sure yet"],
            index=0 if not profile["relationship_goals"] else ["", "Casual dating", "Long-term relationship", "Marriage", "Friendship first", "Not sure yet"].index(profile["relationship_goals"])
        )
    
    st.subheader("Hobbies & Interests")
    hobbies_text = st.text_area("Enter your hobbies (comma separated)", value=", ".join(profile["hobbies"]))
    hobbies = [h.strip() for h in hobbies_text.split(",") if h.strip()]
    
    if st.button("Save Profile", type="primary"):
        st.session_state.profile = {
            "name": name,
            "age": str(age),
            "gender": gender,
            "interested_in": interested_in,
            "relationship_goals": relationship_goals,
            "hobbies": hobbies
        }
        st.success("Profile saved successfully!")

def render_matches_tab():
    """Render potential matches."""    
    st.header("❤️ Potential Matches")
    
    if not st.session_state.profile["name"]:
        st.warning("Please complete your profile first to see potential matches.")
        if st.button("Go to Profile"):
            st.session_state.current_tab = "profile"
            st.rerun()
        return
    
    st.write("Here are some people you might be interested in:")
    
    for i, match in enumerate(st.session_state.matches):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Placeholder for profile picture
            st.image("https://via.placeholder.com/150", width=150)
        
        with col2:
            st.subheader(f"{match['name']}, {match['age']}")
            st.write(f"**Gender:** {match['gender']}")
            st.write(f"**Interests:** {', '.join(match['interests'])}")
            
        with col3:
            st.metric("Compatibility", f"{match['compatibility']}%")
            if st.button("Chat", key=f"chat_btn_{i}"):
                st.session_state.current_tab = "chat"
                
                # Initialize state if this is the first message
                if not st.session_state.chat_history:
                    state = initialize_state(st.session_state.user_id)
                else:
                    # Reconstruct state from session_state
                    state = ChatState(
                        messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                        context=st.session_state.conversation_context,
                        user_id=st.session_state.user_id
                    )
                    
                    # Add previous messages
                    for msg in st.session_state.chat_history:
                        if isinstance(msg, HumanMessage):
                            state["messages"].append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            state["messages"].append({"role": "assistant", "content": msg.content})
                
                # Update context
                state["context"]["last_match_suggested"] = match["name"]
                message = f"I'm interested in {match['name']}. Can you help me start a conversation with them? They're into {', '.join(match['interests'])}."
                
                # Process through LangGraph - fixed to pass message in the expected format
                final_state = chat_chain.run({"message": message, "state": state})
                st.rerun()
        
        st.divider()

def render_tips_tab():
    """Render dating tips section."""    
    st.header("🔍 Dating Tips & Resources")
    
    # Dating tips categories
    categories = [
        "First Date Ideas", 
        "Conversation Starters", 
        "Online Dating Profile Tips",
        "Understanding Red & Green Flags",
        "Building Healthy Relationships"
    ]
    
    selected_category = st.selectbox("Select a topic", categories)
    
    if selected_category == "First Date Ideas":
        st.subheader("Creative First Date Ideas")
        st.write("""        
        1. **Try a cooking class together** - Learn a new skill while getting to know each other
        2. **Visit a local museum or art gallery** - Gives you plenty to talk about
        3. **Go for a scenic hike** - Nature provides a relaxed setting for conversation
        4. **Explore a farmers market** - Casual atmosphere with lots to see and sample
        5. **Take a coffee shop tour** - Visit several unique coffee shops in your area
        """)
        
        if st.button("Ask for personalized date ideas"):
            st.session_state.current_tab = "chat"
            
            # Initialize state if this is the first message
            if not st.session_state.chat_history:
                state = initialize_state(st.session_state.user_id)
            else:
                # Reconstruct state from session_state
                state = ChatState(
                    messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                    context=st.session_state.conversation_context,
                    user_id=st.session_state.user_id
                )
                
                # Add previous messages
                for msg in st.session_state.chat_history:
                    if isinstance(msg, HumanMessage):
                        state["messages"].append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        state["messages"].append({"role": "assistant", "content": msg.content})
            
            # Update context
            state["context"]["recent_topics"].append("date ideas")
            message = "Can you suggest some unique first date ideas based on my profile and interests?"
            
            # Process through LangGraph - fixed to pass message in the expected format
            final_state = chat_chain.run({"message": message, "state": state})
            st.rerun()
    
    elif selected_category == "Conversation Starters":
        st.subheader("Engaging Conversation Starters")
        st.write("""        
        1. **What's the best advice you've ever received?**
        2. **If you could have dinner with anyone, living or dead, who would it be?**
        3. **What small thing makes your day better?**
        4. **What's something you're looking forward to in the next few months?**
        5. **If you could instantly become an expert in something, what would you choose?**
        """)
        
        if st.button("Get personalized conversation starters"):
            st.session_state.current_tab = "chat"
            message = "Can you suggest some conversation starters tailored to my interests and dating preferences?"
            
            # Initialize state if this is the first message
            if not st.session_state.chat_history:
                state = initialize_state(st.session_state.user_id)
            else:
                # Reconstruct state from session_state
                state = ChatState(
                    messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                    context=st.session_state.conversation_context,
                    user_id=st.session_state.user_id
                )
                
                # Add previous messages
                for msg in st.session_state.chat_history:
                    if isinstance(msg, HumanMessage):
                        state["messages"].append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        state["messages"].append({"role": "assistant", "content": msg.content})
            
            # Process through LangGraph - fixed to pass message in the expected format
            final_state = chat_chain.run({"message": message, "state": state})
            st.rerun()
    
    elif selected_category == "Online Dating Profile Tips":
        st.subheader("Creating an Effective Dating Profile")
        st.write("""        
        1. **Use recent, high-quality photos** - Include a clear headshot and full-body photo
        2. **Be specific about your interests** - "I love hiking in national parks" is better than "I like outdoors"
        3. **Show, don't tell** - Instead of saying "I'm funny," share a humorous anecdote
        4. **Keep it positive** - Focus on what you want, not what you don't want
        5. **Be authentic** - Your profile should reflect who you really are
        """)
        
        if st.button("Review my dating profile"):
            st.session_state.current_tab = "chat"
            message = "Based on my profile information, can you help me create an effective dating profile description?"
            
            # Initialize state if this is the first message
            if not st.session_state.chat_history:
                state = initialize_state(st.session_state.user_id)
            else:
                # Reconstruct state from session_state
                state = ChatState(
                    messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                    context=st.session_state.conversation_context,
                    user_id=st.session_state.user_id
                )
                
                # Add previous messages
                for msg in st.session_state.chat_history:
                    if isinstance(msg, HumanMessage):
                        state["messages"].append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        state["messages"].append({"role": "assistant", "content": msg.content})
            
            # Process through LangGraph - fixed to pass message in the expected format
            final_state = chat_chain.run({"message": message, "state": state})
            st.rerun()
    
    elif selected_category == "Understanding Red & Green Flags":
        st.subheader("Recognizing Relationship Patterns")
        
        tab1, tab2 = st.tabs(["Green Flags", "Red Flags"])
        
        with tab1:
            st.write("""            
            **Positive signs to look for:**
            
            * **Respectful communication** - They listen actively and value your opinions
            * **Emotional openness** - They can express their feelings and are receptive to yours
            * **Consistency between words and actions** - They follow through on what they say
            * **Respect for boundaries** - They understand and honor your limits
            * **Shared responsibility** - They contribute equally to the relationship
            """)
        
        with tab2:
            st.write("""            
            **Warning signs to be aware of:**
            
            * **Controlling behavior** - They try to dictate who you see or what you do
            * **Disrespect for boundaries** - They pressure you or ignore your comfort levels
            * **Inconsistency** - Their behavior or communication is unpredictable
            * **Dismissing your feelings** - They invalidate or minimize your concerns
            * **Isolation tactics** - They try to separate you from friends or family
            """)
        
        if st.button("Discuss relationship patterns"):
            st.session_state.current_tab = "chat"
            message = "Can you help me understand how to recognize healthy relationship patterns in dating?"
            
            # Initialize state if this is the first message
            if not st.session_state.chat_history:
                state = initialize_state(st.session_state.user_id)
            else:
                # Reconstruct state from session_state
                state = ChatState(
                    messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                    context=st.session_state.conversation_context,
                    user_id=st.session_state.user_id
                )
                
                # Add previous messages
                for msg in st.session_state.chat_history:
                    if isinstance(msg, HumanMessage):
                        state["messages"].append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        state["messages"].append({"role": "assistant", "content": msg.content})
            
            # Process through LangGraph - fixed to pass message in the expected format
            final_state = chat_chain.run({"message": message, "state": state})
            st.rerun()
    
    elif selected_category == "Building Healthy Relationships":
        st.subheader("Foundations of Healthy Relationships")
        st.write("""        
        * **Open communication** - Creating safe spaces for honest expression
        * **Trust building** - Consistency, reliability, and transparency
        * **Mutual respect** - Valuing each other's autonomy and perspectives
        * **Shared and individual growth** - Supporting each other while maintaining individuality
        * **Conflict resolution** - Addressing disagreements constructively
        """)
        
        if st.button("Learn more about healthy relationships"):
            st.session_state.current_tab = "chat"
            message = "What are some ways to build a strong foundation for a healthy relationship from the beginning?"
            
            # Initialize state if this is the first message
            if not st.session_state.chat_history:
                state = initialize_state(st.session_state.user_id)
            else:
                # Reconstruct state from session_state
                state = ChatState(
                    messages=[{"role": "system", "content": DATING_ADVISOR_PROMPT}],
                    context=st.session_state.conversation_context,
                    user_id=st.session_state.user_id
                )
                
                # Add previous messages
                for msg in st.session_state.chat_history:
                    if isinstance(msg, HumanMessage):
                        state["messages"].append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        state["messages"].append({"role": "assistant", "content": msg.content})
            
            # Process through LangGraph - fixed to pass message in the expected format
            final_state = chat_chain.run({"message": message, "state": state})
            st.rerun()

# Main application
def main():
    render_sidebar()
    
    # Display the appropriate tab
    if st.session_state.current_tab == "chat":
        render_chat_tab()
    elif st.session_state.current_tab == "profile":
        render_profile_tab()
    elif st.session_state.current_tab == "matches":
        render_matches_tab()
    elif st.session_state.current_tab == "tips":
        render_tips_tab()

# Run the app
if __name__ == "__main__":
    main()