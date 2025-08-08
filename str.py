# === Import Required Libraries ===
import streamlit as st       # Streamlit is used to build interactive web apps with Python
import requests              # Used to send HTTP requests to FastAPI backend

# === Define the Backend API URL ===
API_URL = "http://127.0.0.1:8000"  # Change this if deployed online

# === Set up the Streamlit App UI ===
st.set_page_config(page_title="EdTech Adaptive Learning Platform", layout="centered")
st.title("📚 EdTech Adaptive Learning Platform")

# === Sidebar Menu ===
# Users can choose which functionality they want to use
menu = st.sidebar.selectbox("Choose a feature", [
    "Submit Learning Data",
    "Get Recommendations",
    "Adaptive Assessment",
    "Feedback Analyzer",
    "Chatbot Tutor"
])

# === 1. Submit Learning Data ===
# This section allows the user to enter their learning progress
if menu == "Submit Learning Data":
    st.header("📥 Submit Learning Data")
    
    # Create a form to collect user data
    with st.form("submit_form"):
        user_id = st.number_input("User ID", min_value=1, value=101)
        topic = st.selectbox("Topic", ["Algebra", "Geometry", "Calculus", "Trigonometry", "Statistics"])
        time_spent = st.slider("Time Spent (minutes)", 5, 120, 30)
        quiz_score = st.slider("Quiz Score", 0, 100, 70)
        preference = st.selectbox("Learning Preference", ["Visual", "Text", "Audio", "Interactive"])
        feedback = st.text_area("Feedback")
        rating = st.slider("Content Rating (1-5)", 1, 5, 4)
        submitted = st.form_submit_button("Submit")

    # When submitted, send the data to FastAPI
    if submitted:
        payload = {
            "user_id": user_id,
            "topic": topic,
            "time_spent": time_spent,
            "quiz_score": quiz_score,
            "preference": preference,
            "feedback": feedback,
            "rating": rating
        }
        res = requests.post(f"{API_URL}/submit_data", json=payload)  # Send POST request
        st.success(res.json().get("message"))  # Show success message

# === 2. Get Personalized Topic Recommendations ===
elif menu == "Get Recommendations":
    st.header("📌 Learning Recommendations")
    user_id = st.number_input("Enter your User ID", min_value=1)

    # On button click, request recommendations from backend
    if st.button("Get Recommendations"):
        res = requests.get(f"{API_URL}/get_recommendations/{user_id}")
        if res.status_code == 200:
            data = res.json()
            st.write("### Recommended Topics:")
            st.write(data.get("recommended_topics", []))  # Display topics
        else:
            st.error("User not found.")  # Error if user ID doesn't exist

# === 3. Generate Adaptive Assessment ===
elif menu == "Adaptive Assessment":
    st.header("📝 Adaptive Assessment")
    user_id = st.number_input("Enter your User ID for assessment", min_value=1)

    # On button click, request assessment from backend
    if st.button("Generate Assessment"):
        res = requests.get(f"{API_URL}/adaptive_assessment/{user_id}")
        if res.status_code == 200:
            data = res.json()
            st.write(f"### Level: {data.get('assessment_level')}")  # Show level
            st.write("### Questions:")
            for q in data.get("questions", []):  # Loop through questions
                st.write(f"- {q}")
        else:
            st.error("User not found.")

# === 4. Feedback Sentiment Analyzer ===
elif menu == "Feedback Analyzer":
    st.header("💬 Feedback Sentiment Analysis")
    feedback = st.text_area("Enter feedback to analyze")

    # When user clicks analyze, send feedback to FastAPI
    if st.button("Analyze Sentiment"):
        res = requests.post(f"{API_URL}/analyze_feedback", json={"feedback": feedback})
        if res.status_code == 200:
            sentiment = res.json().get("feedback_sentiment")  # Get label and score
            st.write(f"**Label:** {sentiment['label']}, **Score:** {round(sentiment['score'], 2)}")
        else:
            st.error("Analysis failed.")

# === 5. Chatbot Tutor (LLM Placeholder) ===
elif menu == "Chatbot Tutor":
    st.header("🤖 AI Tutor Chatbot")
    query = st.text_input("Ask something about your subject")

    # When user types question and clicks ask, send it to the backend
    if st.button("Ask"):
        res = requests.post(f"{API_URL}/chatbot", json={"query": query})
        if res.status_code == 200:
            reply = res.json().get("reply")  # Get response
            st.write("### Tutor Response:")
            st.write(reply)
        else:
            st.error("Chatbot unavailable.")
