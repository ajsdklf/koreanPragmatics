import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Page config
st.set_page_config(page_title="PKC - Personal Knowledge Companion", page_icon="🧠", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stImage {
        max-width: 300px;
        margin: 0 auto;
        display: block;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("PKC - Personal Knowledge Companion")
    st.subheader("Optimize your web browsing efficiency")

with col2:
    lottie_brain = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_kyu7xb1v.json")
    st_lottie(lottie_brain, height=150)

st.write("---")

# Main features
st.header("Enhance Your Web Experience")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎯 Set Browsing Goals")
    st.write("Define your browsing objectives before you start, ensuring a focused and productive session.")

with col2:
    st.markdown("### 📚 Automatic Summaries")
    st.write("Our AI summarizes every page you visit, organizing information based on your set activities.")

with col3:
    st.markdown("### 🔗 Smart Connections")
    st.write("Create a personalized knowledge graph as you browse, connecting related information automatically.")

st.write("---")

# How it works
st.header("How PKC Works")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Set Your Goals")
    st.write("Begin by selecting your browsing objectives. This helps PKC tailor your experience.")
    
    st.subheader("2. Browse and Learn")
    st.write("As you explore the web, PKC automatically summarizes and organizes information.")
    
    st.subheader("3. Add Personal Insights")
    st.write("Easily add memos and thoughts to any page, enriching your personal knowledge base.")

with col2:
    lottie_workflow = load_lottieurl("https://assets2.lottiefiles.com/private_files/lf30_FPH6Ci.json")
    st_lottie(lottie_workflow, height=400)

st.write("---")

# Benefits
st.header("Why Choose PKC?")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### ⏱️ Save Time")
    st.write("Quickly revisit and understand previously browsed content.")

with col2:
    st.markdown("### 🧠 Enhance Learning")
    st.write("Build a personalized knowledge base as you browse.")

with col3:
    st.markdown("### 🔍 Efficient Retrieval")
    st.write("Easily find and connect information across your browsing history.")

with col4:
    st.markdown("### 📈 Boost Productivity")
    st.write("Stay focused on your goals and make the most of your online time.")

st.write("---")

# Call to Action
st.header("Ready to Revolutionize Your Web Browsing?")
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.button("Add PKC to Chrome", key="cta_button")

# Footer
st.write("---")
st.write("© 2024 Personal Knowledge Companion (PKC). All rights reserved.")