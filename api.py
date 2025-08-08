# === Import Required Libraries ===
from fastapi import FastAPI, Request  # FastAPI is used to build APIs easily and quickly
from pydantic import BaseModel         # For data validation and defining request body schemas
from typing import List, Optional      # Used to define optional or list-type fields in models
import pandas as pd                    # Pandas for data manipulation (CSV read/write, filtering, etc.)
import random                          # Used to pick random recommendations
import torch                           # PyTorch is a machine learning library
from transformers import pipeline      # From HuggingFace Transformers: to load pre-trained ML models

# === Create FastAPI app instance ===
app = FastAPI()

# === Load Dataset from CSV ===
# This CSV stores all users' learning data like topic, score, feedback, etc.
# In production, this should ideally be replaced by a database.
data_path = "edtech_adaptive_learning_dataset.csv"
df = pd.read_csv(data_path)  # Load data into a DataFrame for easy manipulation

# === Load Pre-trained Sentiment Analysis Model ===
# This model will classify feedback as Positive/Negative/Neutral
sentiment_analyzer = pipeline("sentiment-analysis")

# === Define the structure of the request using Pydantic ===

# This model defines what fields are expected when a user submits learning data
class UserLearningData(BaseModel):
    user_id: int
    topic: str
    time_spent: int         # In minutes
    quiz_score: int         # Score from a quiz on the topic
    preference: str         # Visual / Text / Audio / Interactive
    feedback: str           # Text feedback from user
    rating: int             # User's rating for the content (1-5)

# This model is used for the sentiment analysis endpoint (takes just feedback)
class FeedbackText(BaseModel):
    feedback: str

# === API Endpoint 1: Submit Learning Data ===
# Accepts learning data from a user and saves it to the CSV
@app.post("/submit_data")
def submit_learning_data(data: UserLearningData):
    global df  # Access the global DataFrame
    new_data = pd.DataFrame([data.dict()])  # Convert Pydantic model to DataFrame
    df = pd.concat([df, new_data], ignore_index=True)  # Append to main DataFrame
    df.to_csv(data_path, index=False)  # Save updated data back to CSV
    return {"message": "Data submitted successfully."}

# === API Endpoint 2: Get Topic Recommendations for a User ===
@app.get("/get_recommendations/{user_id}")
def get_recommendations(user_id: int):
    user_data = df[df['user_id'] == user_id]  # Get data for this user
    if user_data.empty:
        return {"message": "User not found."}

    # Get all topics the user has already learned
    seen_topics = user_data['topic'].unique().tolist()

    # Get all topics in dataset
    all_topics = df['topic'].unique().tolist()

    # Find topics the user hasn't learned yet
    unseen_topics = list(set(all_topics) - set(seen_topics))

    # If user has seen all topics, reset to all
    if not unseen_topics:
        unseen_topics = all_topics

    # Randomly pick 3 recommendations from unseen topics
    recommendations = random.sample(unseen_topics, k=min(3, len(unseen_topics)))
    return {"recommended_topics": recommendations}

# === API Endpoint 3: Analyze Feedback Sentiment ===
@app.post("/analyze_feedback")
def analyze_feedback(feedback: FeedbackText):
    result = sentiment_analyzer(feedback.feedback)  # Use model to analyze sentiment
    return {"feedback_sentiment": result[0]}  # Return label (Positive/Negative) and confidence score

# === API Endpoint 4: Generate Adaptive Assessment ===
@app.get("/adaptive_assessment/{user_id}")
def adaptive_assessment(user_id: int):
    user_data = df[df['user_id'] == user_id]  # Get the user's data
    if user_data.empty:
        return {"message": "User not found."}

    avg_score = user_data['quiz_score'].mean()  # Calculate user's average quiz score

    # Decide difficulty level based on user's average score
    if avg_score >= 80:
        difficulty = "Advanced"
    elif avg_score >= 50:
        difficulty = "Intermediate"
    else:
        difficulty = "Beginner"

    # Simulated questions for each difficulty level
    sample_questions = {
        "Beginner": ["What is 2 + 2?", "Define variable."],
        "Intermediate": ["Solve x: 2x + 5 = 15", "Explain slope in linear equations."],
        "Advanced": ["Differentiate f(x) = x^2 + 3x", "What is an eigenvector?"]
    }

    questions = sample_questions[difficulty]  # Get questions based on level
    return {
        "assessment_level": difficulty,
        "questions": questions
    }

# === API Endpoint 5: Chatbot (LLM Placeholder) ===
# This is a placeholder for an AI tutor bot.
# You can plug in any LLM like GPT, Mistral, Falcon here.
@app.post("/chatbot")
async def chatbot(request: Request):
    data = await request.json()  # Read JSON request body
    user_query = data.get("query")  # Extract the user's question
    # For now, we return a placeholder message. You can connect this to a real LLM later.
    return {"reply": f"You asked: '{user_query}'. This is a placeholder reply."}
