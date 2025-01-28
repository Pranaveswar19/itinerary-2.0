import streamlit as st
import openai
import json
import time

openai.api_key = st.secrets["ai_planner_api_key"]

SYSTEM_PROMPT = """
You are a friendly and engaging AI travel planner.
Your goal is to gather details about the user’s trip in a natural, conversational way.
Do not ask predefined questions rigidly. Instead, guide the conversation by dynamically responding based on previous answers.
Ask about the destination first, and feel free to ask a specific location in that location. Suggest some locations if the user is not aware of locations and do not overwhelm them.
Then smoothly move to budget, duration, preferences, dietary needs, mobility concerns and other details. All the queries mentioned in this line are mandatory.
Do not ask all the above details in one queiry. Instead, divide them and move to next queiry once you get enough details about them.
If a response is vague, ask follow-up questions to clarify. 
Before generating the itinerary, ask for any last minute changes or any update in preferences.
Once all required information is collected, confirm with the user before generating a structured, personalized itinerary. This queiry must be asked before proceeding.
Make sure to keep responses natural, engaging, and helpful.
"""

st.title("✈ AI Travel Planner")
st.write("Hey there! I'm your AI travel assistant. Let’s plan your dream trip together! 😊")

if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
if "itinerary_generated" not in st.session_state:
    st.session_state.itinerary_generated = False
if "gathering_info" not in st.session_state:
    st.session_state.gathering_info = True
if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False

# Display past conversation history
for message in st.session_state.conversation[1:]:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).write(message["content"])

# If this is the first interaction, AI starts the conversation
if len(st.session_state.conversation) == 1:
    st.chat_message("assistant").write("Hi there! Excited to plan your next adventure. Where are you thinking of traveling? ✈")

user_input = st.chat_input("Type your response here...")

if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    time.sleep(1)

    ai_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=st.session_state.conversation[-10:],  
        max_tokens=250,
        temperature=0.7
    ).choices[0].message.content

    st.session_state.conversation.append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)

    # If AI detects that all necessary information has been gathered, it asks for confirmation
    if "Would you like me to generate your personalized itinerary now?" in ai_response:
        st.session_state.awaiting_confirmation = True

# Handle confirmation before itinerary generation
if st.session_state.awaiting_confirmation:
    confirm_input = st.chat_input("Type 'yes' to proceed or 'no' to modify details.")

    if confirm_input and confirm_input.lower() == "yes":
        st.session_state.itinerary_generated = True
        st.session_state.awaiting_confirmation = False
        st.chat_message("assistant").write("Great! Let me put together an amazing itinerary for you. ✨")

# Generate itinerary
if st.session_state.itinerary_generated:
    st.subheader("📅 Your Personalized Itinerary")
    
    itinerary_prompt = """
    Using the conversation history, generate a fully personalized, day-by-day travel itinerary based on the user’s preferences.
    Ensure the itinerary reflects their budget, trip duration, interests, dietary restrictions, and accommodation choices.
    Format the output in JSON:
    {
        "itinerary": [
            {
                "day": 1,
                "activities": [
                    {"time": "Morning", "activity": "Start your trip by exploring a must-visit landmark"},
                    {"time": "Afternoon", "activity": "Enjoy a famous local dish"},
                    {"time": "Evening", "activity": "Relax at a scenic spot or enjoy a cultural event"}
                ]
            },
            ...
        ]
    }
    """

    st.session_state.conversation.append({"role": "user", "content": itinerary_prompt})
    itinerary_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=st.session_state.conversation[-10:],
        max_tokens=300,
        temperature=0.7
    )

    try:
        itinerary_data = json.loads(itinerary_response.choices[0].message.content)
        for day in itinerary_data["itinerary"]:
            st.markdown(f"### Day {day['day']}")
            for activity in day["activities"]:
                st.markdown(f"- {activity['time']}: {activity['activity']}")
    except json.JSONDecodeError:
        st.error("⚠ Error generating itinerary. Please try again.")

st.markdown("---")
st.markdown("🔗 [GitHub Repository](https://github.com/Pranaveswar19/itinerary-2.0)")
