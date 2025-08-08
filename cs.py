# === Import Required Libraries ===
import pandas as pd  # For data manipulation (reading CSV, working with DataFrames)
from sklearn.feature_extraction.text import TfidfVectorizer  # To convert text to numeric form using TF-IDF
from sklearn.metrics.pairwise import cosine_similarity  # To measure similarity between user query and resources

# === Step 1: Load Learning Resources Dataset ===
# This CSV contains details of various learning resources like title, subject, difficulty, description, etc.
df = pd.read_csv("learning_resources_large.csv")

# === Step 2: Prepare Text for TF-IDF ===
# Combine relevant columns (title, description, subject) into one text field to use for similarity comparison
df['text'] = df['title'] + " " + df['description'] + " " + df['subject']

# === Step 3: Convert Text Data into TF-IDF Vectors ===
# This converts each resource's text into a numeric vector while ignoring common English stop words
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['text'])  # Each row corresponds to a resource

# === Step 4: Define Function to Recommend Resources Based on User's Query ===
def get_recommendations_from_query(user_query, top_n=5):
    """
    Given a user's free-text query, return top N most relevant learning resources using cosine similarity.
    """
    # Convert user query into TF-IDF vector using the same vectorizer
    query_vector = vectorizer.transform([user_query])
    
    # Calculate cosine similarity between user query and all resources
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Get indices of top N most similar resources
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    # Return selected rows with useful columns (title, url, subject, etc.) as a list of dictionaries
    return df[['title', 'url', 'subject', 'difficulty', 'description']].iloc[top_indices].to_dict(orient='records')

# === Step 5: Run the Script as a Test ===
if __name__ == "__main__":
    # Example user query
    query = "I want to learn about algebra or math equations"

    # Get top 5 recommended resources based on the query
    results = get_recommendations_from_query(query)

    # Print the recommendations
    for res in results:
        print(res)
