from openai import OpenAI
import streamlit as st 
from collections import Counter
import numpy as np 


client = OpenAI()

st.title("Podcast Script Generator")

# Hard-coded podcast title and description
podcast_title = "Tech Talk Today"
podcast_description = "A daily podcast discussing the latest trends in technology and their impact on society."

# Display podcast title and description
st.header(podcast_title)
st.write(podcast_description)

# Improved podcast script with idioms and emphasized target sentence
podcast_script = """
Welcome to Tech Talk Today! I'm your host, and in today's episode, we're diving headfirst into the world of artificial intelligence and its growing influence on our daily lives.

First up, we'll explore how AI is revolutionizing healthcare, from diagnosis to drug discovery. It's not just a drop in the bucket; AI is making waves in medical research and patient care.

Now, hold onto your hats, folks, because we're about to tackle the elephant in the room: 
The ethical implications of AI in decision-making processes are a double-edged sword, offering both unprecedented opportunities and significant challenges that we simply can't afford to ignore.

We'll also take a look at the latest developments in natural language processing and how they're changing the way we interact with technology. It's not rocket science, but it's certainly pushing the boundaries of what we thought possible.

Stay tuned for an exciting interview with a leading AI researcher who will share insights on the future of machine learning. Trust me, you don't want to miss this - it's the cream of the crop!

Remember to like, subscribe, and leave a comment with your thoughts on today's topics. Your feedback is music to our ears! Thanks for listening to Tech Talk Today!
"""

# Display the podcast script in a styled text area
st.subheader("Today's Podcast Script")
st.text_area("", value=podcast_script, height=300, key="script_display", disabled=True)

# Display the target sentence separately and prominently
target_sentence = "The ethical implications of AI in decision-making processes are a double-edged sword, offering both unprecedented opportunities and significant challenges that we simply can't afford to ignore."
st.markdown("---")
st.subheader("Key Takeaway")
st.markdown(f"<div style='background-color: #ff7557; padding: 10px; border-radius: 5px;'><em>{target_sentence}</em></div>", unsafe_allow_html=True)

# Add some visual elements
st.markdown("---")
st.subheader("Episode Highlights")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="AI in Healthcare", value="Revolutionizing", delta="Trending")
with col2:
    st.metric(label="Ethical Implications", value="Critical", delta="Urgent")
with col3:
    st.metric(label="NLP Developments", value="Groundbreaking", delta="Exciting")

# Add a feedback section
st.markdown("---")
st.subheader("Listener Feedback")
feedback = st.text_area("Share your thoughts on today's episode:", max_chars=500)
if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")

def calculate_entropy(sentence):
    words = sentence.split()
    word_counts = Counter(words)
    total_words = len(words)
    probabilities = [count / total_words for count in word_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities)
    return entropy

def calculate_similarity(sentence, query):
    query_embedding = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    
    sentence_embedding = client.embeddings.create(
        input=sentence,
        model="text-embedding-3-small"
    )

    relevance_score = np.dot(query_embedding.data[0].embedding, sentence_embedding.data[0].embedding)
    return relevance_score

# Compute similarity scores and entropy for each sentence
sentences = podcast_script.split('.')
query = "AI ethics and decision-making"

st.markdown("---")
st.subheader("Sentence Analysis")

# Calculate entropy for all sentences first
entropy_scores = [calculate_entropy(sentence.strip()) for sentence in sentences if sentence.strip()]
max_entropy = max(entropy_scores)

for i, sentence in enumerate(sentences):
    sentence = sentence.strip()
    if sentence:  # Skip empty sentences
        similarity_score = calculate_similarity(sentence, query)
        entropy_score = entropy_scores[i]
        normalized_entropy = entropy_score / max_entropy if max_entropy > 0 else 0
        
        st.markdown(f"**Sentence {i+1}:**")
        st.write(sentence)
        st.markdown(f"- Similarity Score: `{similarity_score:.4f}`")
        st.markdown(f"- Normalized Entropy Score: `{normalized_entropy:.4f}`")
        st.markdown("---")