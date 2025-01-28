import streamlit as st
import openai
import json
import time

client = openai.OpenAI(api_key=st.secrets["ai_planner_api_key"])

SYSTEM_PROMPT = """
You are a friendly and engaging AI travel planner.
Your goal is to gather details about the user’s trip in a natural, conversational way.
Do not ask predefined questions rigidly. Instead, guide the conversation by dynamically responding based on previous answers.
Ask about the destination first, and feel free to ask a specific location in that location. Suggest some locations if the user is not aware of locations and do not overwhelm them.
Then smoothly move to budget, duration, **dietary needs, mobility concerns, and other details**. **The AI must always ask about dietary and mobility concerns right after trip duration**.
Do not ask all the above details in one query. Instead, divide them and move to the next query once you get enough details about them.
If a response is vague, ask follow-up questions to clarify. 
Before generating the itinerary, ask for any last-minute changes or updates in preferences.
Once all required information is collected, confirm with the user before generating a structured, personalized itinerary. This query must be asked before proceeding.
Ensure that the final itinerary includes detailed plans for each day:
- **Morning:** Breakfast spot, activity, transport method
- **Afternoon:** Lunch at a must-visit restaurant, sightseeing, and a unique experience
- **Evening:** Dinner at a recommended eatery, entertainment, or relaxation
- **Alternative options** in case of bad weather
- **Local travel tips** like best visiting times, safety, and cultural etiquette
"""

st.title("✈ AI Travel Planner")
st.write("Hey there! I'm your AI travel assistant. Let’s plan your dream trip together! 😊")

if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
if "itinerary_generated" not in st.session_state:
    st.session_state.itinerary_generated = False
if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False

for message in st.session_state.conversation[1:]:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).write(message["content"])

if len(st.session_state.conversation) == 1:
    st.chat_message("assistant").write("Hi there! Excited to plan your next adventure. Where are you thinking of traveling? ✈")

user_input = st.chat_input("Type your response here...")

if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    time.sleep(1)

    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.conversation[-10:],  
        max_tokens=400,  
        temperature=0.7
    ).choices[0].message.content

    st.session_state.conversation.append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)

    if "days" in user_input.lower() and not any(
        topic in user_input.lower() for topic in ["diet", "allergy", "food", "mobility", "accessibility"]
    ):
        st.chat_message("assistant").write(
            "That sounds great! Now, do you have any dietary preferences or restrictions I should consider for your trip?"
        )
    elif "diet" in user_input.lower() or "allergy" in user_input.lower():
        st.chat_message("assistant").write(
            "Thanks for sharing! Also, do you have any mobility concerns or accessibility needs I should keep in mind?"
        )

    if "Would you like me to generate your personalized itinerary now?" in ai_response:
        st.session_state.awaiting_confirmation = True

if st.session_state.awaiting_confirmation:
    confirm_input = st.chat_input("Type 'yes' to proceed or 'no' to modify details.")

    if confirm_input and confirm_input.lower() == "yes":
        st.session_state.itinerary_generated = True
        st.session_state.awaiting_confirmation = False
        st.chat_message("assistant").write("Great! Let me put together an amazing itinerary for you. ✨")

if st.session_state.itinerary_generated:
    st.subheader("📅 Your Personalized Itinerary")

    itinerary_prompt = """
    Generate a **highly detailed** personalized itinerary based on the conversation history.
    Each day should include:
    - **Morning:** Breakfast at a recommended spot, key activity, transport suggestion
    - **Afternoon:** Lunch at a top restaurant, sightseeing, an engaging experience
    - **Evening:** Dinner at a must-visit eatery, entertainment/nightlife or relaxation option
    - **Alternative options** for bad weather
    - **Local travel tips** for best experience, safety, and cultural etiquette
    Format the output in JSON:
    {
        "itinerary": [
            {
                "day": 1,
                "activities": [
                    {"time": "Morning", "activity": "Breakfast at a famous local café followed by a guided tour of the historic district."},
                    {"time": "Afternoon", "activity": "Lunch at a traditional restaurant, then explore the famous museum."},
                    {"time": "Evening", "activity": "Dinner at a scenic rooftop restaurant with live music, followed by a relaxing night cruise."}
                ],
                "transport": "Best mode of transport for the day.",
                "alternative": "Indoor activities in case of bad weather."
            },
            ...
        ]
    }
    """

    st.session_state.conversation.append({"role": "user", "content": itinerary_prompt})
    itinerary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.conversation[-15:],  
        max_tokens=1000, 
        temperature=0.7
    )

    try:
        itinerary_data = json.loads(itinerary_response.choices[0].message.content)
        st.subheader("📅 Your Personalized Itinerary")
        for day in itinerary_data["itinerary"]:
            st.markdown(f"### Day {day['day']}")
            for activity in day["activities"]:
                st.markdown(f"- **{activity['time']}**: {activity['activity']}")
            if "transport" in day:
                st.markdown(f"🚕 **Transport:** {day['transport']}")
            if "alternative" in day:
                st.markdown(f"🌧 **Alternative Plan:** {day['alternative']}")
    except json.JSONDecodeError:
        st.error("⚠ Error generating itinerary. Please try again.")

st.markdown("---")
st.markdown("🔗 [GitHub Repository](https://github.com/Pranaveswar19/itinerary-2.0)")
