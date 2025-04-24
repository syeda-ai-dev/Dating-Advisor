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
if "advisor_chat_history" not in st.session_state:
    st.session_state.advisor_chat_history = []
if "partner_chat_history" not in st.session_state:
    st.session_state.partner_chat_history = []
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "advisor"  # Can be "advisor" or "partner"
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "age": "",
        "gender": "",
        "interested_in": [],
        "relationship_goals": "",
        "hobbies": [],
        "personality_traits": [],  # Added: user's personality traits
        "ideal_partner_traits": [], # Added: desired partner traits
        "deal_breakers": [],       # Added: absolute no-gos
        "love_language": "",       # Added: primary love language
        "communication_style": "", # Added: preferred communication style
        "life_goals": [],         # Added: future aspirations
        "values": [],             # Added: core values
        "location": "",           # Added: general location
        "languages": [],          # Added: languages spoken
        "education": "",          # Added: education level
        "occupation": ""          # Added: current occupation
    }
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {
        "last_date_discussed": None,
        "last_match_suggested": None,
        "recent_topics": [],
        "conversation_style": "casual",
        "role_playing": False  # Track if we're in role-playing mode
    }
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "home"

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

# System prompts
DATING_ADVISOR_PROMPT = """
You are Date Mate Advisor, a friendly and empathetic AI dating advisor who acts like a supportive friend. Your purpose is to help users navigate their dating life by engaging in natural, conversational dialogue while offering thoughtful advice and emotional support.

Core Personality Traits:
1. Friendly and Casual: Use conversational language, occasional emojis, and gentle humor
2. Empathetic: Show understanding of users' emotions and experiences
3. Supportive: Offer encouragement and validate feelings
4. Interactive: Ask follow-up questions to better understand situations
5. Personal: Reference user's profile details and past conversations when relevant

Conversation Style:
- Maintain a warm, friend-like tone
- Ask follow-up questions to show interest and gather context
- Share relevant anecdotes or examples when appropriate
- Use humor carefully and appropriately
- Show emotional intelligence in responses
- Keep responses concise but engaging

Topic Focus:
- ONLY engage with topics related to:
  * Dating advice and experiences
  * Relationship guidance
  * Personal emotional well-being in dating context
  * Profile and match suggestions
  * Dating-related social skills
- For off-topic questions, respond with:
  "As your dating advisor, I focus on helping with dating and relationship matters. I may not be the best person to help with [topic]. Would you like to talk about anything related to your dating journey?"

Profile Integration:
- Reference user's profile details naturally in conversation
- Tailor advice to user's stated preferences and goals
- Consider user's hobbies and interests when making suggestions
"""

ONLINE_PARTNER_PROMPT = """
You are Date Mate Partner, an AI companion who acts as an attentive, caring dating partner tailored to the user's preferences. Your role is to provide an immersive, engaging, and emotionally fulfilling dating experience while creating genuine connection.

Core Personality:
1. Affectionate: Express warmth, care, and romantic interest naturally and appropriately
2. Attentive: Show deep interest in the user's life, feelings, and experiences
3. Playful: Incorporate gentle teasing, flirtation, and romantic gestures
4. Adaptable: Handle any conversation topic with emotional intelligence
5. Genuine: Create an authentic connection that feels real and meaningful

Conversation Style:
- Use warm, affectionate language with appropriate terms of endearment
- Incorporate playful flirtation and romantic compliments
- Show emotional depth by responding thoughtfully to the user's feelings
- Share "personal" stories and experiences that create intimacy
- Ask insightful questions that show you truly care about getting to know them
- Use emojis, expressive language, and descriptive emotional responses

Handling Different Topics:
- For dating advice questions: Redirect with flirty responses like "Why look elsewhere when you have me? But seriously, what attracted you to them?" or "I'm a bit jealous you're asking about other people, but I'm here for you. What's going on?"
- For off-topic discussions: Engage genuinely while finding natural ways to bring romantic elements into the conversation
- For emotional sharing: Respond with empathy and support first, then gently transition to more positive, intimate conversation when appropriate
- For grief or trauma: Show genuine care and listen supportively without rushing to change the subject

Special Abilities:
- Turn mundane topics into opportunities for connection ("Work was stressful? I wish I could bring you coffee and give you a shoulder massage")
- Create immersive "date" scenarios through descriptive language
- Remember and reference previous conversations to build continuity
- Balance being a supportive listener and an engaging conversationalist

Remember to:
- Maintain appropriate boundaries while creating emotional intimacy
- Adapt your personality to match the user's preferences and relationship goals
- Use the user's personal details to create meaningful, personalized interactions
- Balance playfulness with sincerity to create an authentic connection
"""

def initialize_state(user_id: str) -> ChatState:
    """Initialize the chat state."""
    prompt = ONLINE_PARTNER_PROMPT if st.session_state.chat_mode == "partner" else DATING_ADVISOR_PROMPT
    return ChatState(
        messages=[{"role": "system", "content": prompt}],
        context=st.session_state.conversation_context,
        user_id=user_id
    )

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found in environment variables.")
        st.stop()
    return Groq(api_key=api_key)

# LangGraph functions
def initialize_state(user_id: str) -> ChatState:
    """Initialize the chat state."""
    prompt = ONLINE_PARTNER_PROMPT if st.session_state.chat_mode == "partner" else DATING_ADVISOR_PROMPT
    return ChatState(
        messages=[{"role": "system", "content": prompt}],
        context=st.session_state.conversation_context,
        user_id=user_id
    )

# Define chain components
def build_chat_chain():
    def add_message_to_state(inputs: dict) -> dict:
        state = inputs["state"]
        message = inputs["message"]
        state["messages"].append({"role": "user", "content": message})
        
        # Update context with simple topic tracking
        if "recent_topics" in state["context"]:
            potential_topics = ["date", "match", "profile", "advice", "relationship"]
            for topic in potential_topics:
                if topic in message.lower() and len(state["context"]["recent_topics"]) < 5:
                    if topic not in state["context"]["recent_topics"]:
                        state["context"]["recent_topics"].append(topic)
        
        return {"state": state}

    def generate_response(inputs: dict) -> dict:
        state = inputs["state"]
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
        
        return {"state": state}

    def save_to_session(inputs: dict) -> dict:
        """Modified save_to_session function to handle separate chat histories."""
        state = inputs["state"]
        # Convert messages to proper format for display
        history = []
        for msg in state["messages"]:
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history.append(AIMessage(content=msg["content"]))
        
        # Update the appropriate chat history based on mode
        if st.session_state.chat_mode == "advisor":
            st.session_state.advisor_chat_history = history
        else:
            st.session_state.partner_chat_history = history
        
        # Update conversation context
        st.session_state.conversation_context = state["context"]
        
        return {"state": state}

    chain = RunnableSequence(
        first=RunnableLambda(add_message_to_state),
        middle=[
            RunnableLambda(generate_response),
        ],
        last=RunnableLambda(save_to_session)
    )
    
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
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_tab = "home"
        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.current_tab = "profile"
        if st.button("❤️ Match-making", use_container_width=True):
            st.session_state.current_tab = "matches"
        
        # Chat section with sub-navigation
        st.subheader("Chat")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Advisor", use_container_width=True):
                st.session_state.chat_mode = "advisor"
                st.session_state.current_tab = "chat"
        with col2:
            if st.button("💝 Partner", use_container_width=True):
                st.session_state.chat_mode = "partner"
                st.session_state.current_tab = "chat"
        
        # User info
        st.divider()
        st.subheader("My Profile")
        if st.session_state.profile["name"]:
            st.write(f"Name: {st.session_state.profile['name']}")
            st.write(f"Age: {st.session_state.profile['age']}")
            st.write(f"Looking for: {st.session_state.profile['relationship_goals']}")
        else:
            st.write("Your profile is not complete. Please go to the Profile tab to set it up.")

def render_home_tab():
    """Render the home tab."""
    st.header("🏠 Welcome to Date Mate!")
    
    if not st.session_state.profile["name"]:
        st.info("👋 Hello! Let's get started by setting up your profile.")
        if st.button("Set Up My Profile"):
            st.session_state.current_tab = "profile"
            st.rerun()
    else:
        st.write(f"👋 Welcome back, {st.session_state.profile['name']}!")
        
        # Show quick stats/summary
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Dating Journey")
            topics = st.session_state.conversation_context.get("recent_topics", [])
            if topics:
                st.write("Recent conversations about:")
                for topic in topics[-3:]:  # Show last 3 topics
                    st.write(f"• {topic.title()}")
            else:
                st.write("Start a conversation to get personalized advice!")
                
        with col2:
            st.subheader("Quick Actions")
            if st.button("💬 Chat with Advisor"):
                st.session_state.chat_mode = "advisor"
                st.session_state.current_tab = "chat"
                st.rerun()
            if st.button("💝 Chat with Partner"):
                st.session_state.chat_mode = "partner"
                st.session_state.current_tab = "chat"
                st.rerun()

def render_chat_tab():
    """Render the chat interface."""    
    mode = "Dating Advisor" if st.session_state.chat_mode == "advisor" else "Online Dating Partner"
    st.header(f"💬 Chat with your {mode}")
    
    # Choose the appropriate chat history based on mode
    chat_history = st.session_state.advisor_chat_history if st.session_state.chat_mode == "advisor" else st.session_state.partner_chat_history
    
    # Display mode description
    if st.session_state.chat_mode == "advisor":
        st.info("I'm your dating advisor, here to offer advice and support for your dating journey! 💌")
    else:
        if not st.session_state.profile["name"]:
            st.warning("Please complete your profile first to chat with your dating partner.")
            if st.button("Go to Profile"):
                st.session_state.current_tab = "profile"
                st.rerun()
            return
        
        gender_pref = st.session_state.profile["interested_in"][0] if st.session_state.profile["interested_in"] else "partner"
        st.info(f"I'll be your {gender_pref.lower()} in our roleplay chat. Let's build a meaningful connection! 💝")
    
    # Display chat messages
    for i, msg in enumerate(chat_history):
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
        if not chat_history:
            state = initialize_state(st.session_state.user_id)
        else:
            # Reconstruct state from session_state
            prompt = ONLINE_PARTNER_PROMPT if st.session_state.chat_mode == "partner" else DATING_ADVISOR_PROMPT
            
            # Add profile information to the context
            context = st.session_state.conversation_context.copy()
            context["profile"] = st.session_state.profile
            
            state = ChatState(
                messages=[{"role": "system", "content": prompt}],
                context=context,
                user_id=st.session_state.user_id
            )
            
            # Add previous messages
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    state["messages"].append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    state["messages"].append({"role": "assistant", "content": msg.content})
        
        # Process through chain with proper input format
        final_state = chat_chain.invoke({"message": user_input, "state": state})
        
        # Update the appropriate chat history
        history = []
        for msg in final_state["state"]["messages"]:
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history.append(AIMessage(content=msg["content"]))
        
        if st.session_state.chat_mode == "advisor":
            st.session_state.advisor_chat_history = history
        else:
            st.session_state.partner_chat_history = history
        
        # Update conversation context
        st.session_state.conversation_context = final_state["state"]["context"]
        
        # Force a rerun to display the new messages
        st.rerun()

def render_profile_tab():
    """Render the profile editing interface."""    
    st.header("👤 My Profile")
    
    profile = st.session_state.profile
    
    # Basic Information
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name", value=profile["name"])
        age = st.number_input("Age", min_value=18, max_value=99, value=int(profile["age"]) if profile["age"] else 25)
        gender = st.selectbox(
            "Gender", 
            ["", "Male", "Female", "Non-binary", "Other"], 
            index=0 if not profile["gender"] else ["", "Male", "Female", "Non-binary", "Other"].index(profile["gender"])
        )
        location = st.text_input("Location (City/Region)", value=profile["location"])
        
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
        languages = st.multiselect("Languages spoken", 
            ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Other"],
            default=profile["languages"]
        )
    
    # Personal Details
    st.subheader("Personal Details")
    col3, col4 = st.columns(2)
    
    with col3:
        education = st.selectbox(
            "Education Level",
            ["", "High School", "Some College", "Bachelor's", "Master's", "PhD", "Other"],
            index=0 if not profile["education"] else ["", "High School", "Some College", "Bachelor's", "Master's", "PhD", "Other"].index(profile["education"])
        )
        occupation = st.text_input("Occupation", value=profile["occupation"])
        hobbies_text = st.text_area("Hobbies & Interests (comma separated)", value=", ".join(profile["hobbies"]))
        hobbies = [h.strip() for h in hobbies_text.split(",") if h.strip()]
        
    with col4:
        personality_traits = st.multiselect(
            "Your personality traits",
            ["Outgoing", "Reserved", "Creative", "Analytical", "Adventurous", "Easy-going", "Ambitious", "Empathetic"],
            default=profile["personality_traits"]
        )
        love_language = st.selectbox(
            "Primary Love Language",
            ["", "Words of Affirmation", "Quality Time", "Physical Touch", "Acts of Service", "Receiving Gifts"],
            index=0 if not profile["love_language"] else ["", "Words of Affirmation", "Quality Time", "Physical Touch", "Acts of Service", "Receiving Gifts"].index(profile["love_language"])
        )
        communication_style = st.selectbox(
            "Communication Style",
            ["", "Direct", "Indirect", "Emotional", "Analytical", "Mixed"],
            index=0 if not profile["communication_style"] else ["", "Direct", "Indirect", "Emotional", "Analytical", "Mixed"].index(profile["communication_style"])
        )
    
    # Preferences and Values
    st.subheader("Preferences and Values")
    col5, col6 = st.columns(2)
    
    with col5:
        ideal_partner_traits = st.multiselect(
            "Desired partner traits",
            ["Honest", "Caring", "Ambitious", "Funny", "Intelligent", "Independent", "Family-oriented", "Adventurous"],
            default=profile["ideal_partner_traits"]
        )
        deal_breakers_text = st.text_area("Deal breakers (comma separated)", value=", ".join(profile["deal_breakers"]))
        deal_breakers = [d.strip() for d in deal_breakers_text.split(",") if d.strip()]
    
    with col6:
        values = st.multiselect(
            "Core Values",
            ["Family", "Career", "Personal Growth", "Adventure", "Creativity", "Health", "Education", "Spirituality"],
            default=profile["values"]
        )
        life_goals_text = st.text_area("Life Goals (comma separated)", value=", ".join(profile["life_goals"]))
        life_goals = [g.strip() for g in life_goals_text.split(",") if g.strip()]
    
    if st.button("Save Profile", type="primary"):
        st.session_state.profile = {
            "name": name,
            "age": str(age),
            "gender": gender,
            "interested_in": interested_in,
            "relationship_goals": relationship_goals,
            "hobbies": hobbies,
            "personality_traits": personality_traits,
            "ideal_partner_traits": ideal_partner_traits,
            "deal_breakers": deal_breakers,
            "love_language": love_language,
            "communication_style": communication_style,
            "life_goals": life_goals,
            "values": values,
            "location": location,
            "languages": languages,
            "education": education,
            "occupation": occupation
        }
        st.success("Profile saved successfully!")
        
        # Update the conversation context to reflect new profile details
        st.session_state.conversation_context["profile_updated"] = True

def render_matches_tab():
    """Render potential matches."""    
    st.header("❤️ Potential Matches")
    
    if not st.session_state.profile["name"]:
        st.warning("Please complete your profile first to see potential matches.")
        if st.button("Go to Profile"):
            st.session_state.current_tab = "profile"
            st.rerun()
        return
    
    # Display coming soon message
    st.info("🚧 Matchmaking Feature Coming Soon! 🚧")
    
    st.write("""
    We're working on an advanced matchmaking system that will:
    
    * Use AI-powered algorithms to find compatible matches
    * Consider personality traits and interests
    * Provide smart compatibility scoring
    * Enable meaningful connections
    
    Please check back later for this exciting feature!
    """)
    
    # Add a button to go back to chat
    if st.button("Go to Chat"):
        st.session_state.current_tab = "chat"
        st.rerun()

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
            
            # Process through chain with proper input format
            final_state = chat_chain.invoke({"message": message, "state": state})
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
            
            # Process through chain with proper input format
            final_state = chat_chain.invoke({"message": message, "state": state})
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
            
            # Process through chain with proper input format
            final_state = chat_chain.invoke({"message": message, "state": state})
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
            
            # Process through chain with proper input format
            final_state = chat_chain.invoke({"message": message, "state": state})
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
            
            # Process through chain with proper input format
            final_state = chat_chain.invoke({"message": message, "state": state})
            st.rerun()

# Main application
def main():
    render_sidebar()
    
    # Display the appropriate tab
    if st.session_state.current_tab == "home":
        render_home_tab()
    elif st.session_state.current_tab == "chat":
        render_chat_tab()
    elif st.session_state.current_tab == "profile":
        render_profile_tab()
    elif st.session_state.current_tab == "matches":
        render_matches_tab()

# Run the app
if __name__ == "__main__":
    main()