from openai import OpenAI
from modules.runnables import *
import json
import streamlit as st
import time

client = OpenAI()

# Set page config for a more professional look
st.set_page_config(page_title="Career Experience Helper", page_icon="💼", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stTextArea textarea {
        border-radius: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .career-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .career-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    .career-card.selected {
        border-color: #4CAF50;
        background-color: #e8f5e9;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'script' not in st.session_state:
    st.session_state.script = None
    st.session_state.current_part = 1
    st.session_state.career = ""
    st.session_state.abstract_experience_result = ""
    st.session_state.quiz_correct = False
    st.session_state.career_image = None

# Main title with animation
st.title("🚀 Career Experience Helper")
st.markdown("---")

# Sidebar for navigation and controls
with st.sidebar:
    st.header("Navigation")
    if st.button("🏠 Home", key="home_button"):
        st.session_state.script = None
        st.session_state.current_part = 1
        st.session_state.career_image = None
    if st.button("🔄 Start Over", key="start_over_button"):
        st.session_state.script = None
        st.session_state.current_part = 1
        st.session_state.career = ""
        st.session_state.abstract_experience_result = ""
        st.session_state.quiz_correct = False
        st.session_state.career_image = None
    st.markdown("---")
    st.write("Made with ❤️ by Your Team")

# Main content area
if st.session_state.script is None:
    st.subheader("Welcome! Choose a career to explore:")
    
    # Define 6 occupation cards
    occupations = [
        "Software Developer",
        "Data Scientist",
        "UX Designer",
        "Marketing Manager",
        "Financial Analyst",
        "Teacher"
    ]
    
    # Create a 2x3 grid for occupation cards
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, occupation in enumerate(occupations):
        with cols[i % 3]:
            if st.button(occupation, key=f"occupation_{i}", use_container_width=True):
                st.session_state.career = occupation
                st.session_state.selected_career = occupation
                st.rerun()
    
    # Hidden input to store selected career
    st.text_input("Selected Career", key="selected_career", value=st.session_state.career, label_visibility="hidden")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🎬 Generate Career Experience", key="generate_button"):
            career = st.session_state.selected_career
            if career:
                with st.spinner(f"Creating your {career} experience..."):
                    script = generate_script_for_career_experience_helper(career)
                    st.session_state.script = json.loads(script)
                    st.session_state.current_part = 1
                    st.session_state.career = career
                    
                    # Try to generate image, use placeholder if it fails
                    image_url = generate_image_for_career_experience_helper(career)
                    if image_url:
                        st.session_state.career_image = image_url
                    else:
                        st.session_state.career_image = "https://via.placeholder.com/1024x1024.png?text=Career+Image+Unavailable"
                
                st.success("Your career experience is ready!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Please select a career before generating the experience.")

else:
    # Progress bar
    progress = (st.session_state.current_part - 1) / 9
    st.progress(progress)
    
    # Display current part
    if st.session_state.current_part <= 7:
        st.subheader(f"Part {st.session_state.current_part}: {st.session_state.script['career']} Experience")
        part_key = f"part{st.session_state.current_part}"
        
        content = st.session_state.script[part_key]['content'] if isinstance(st.session_state.script[part_key], dict) else st.session_state.script[part_key]
        
        with st.expander("Read Content", expanded=True):
            st.write(content)
        
        # Quiz if available
        if isinstance(st.session_state.script[part_key], dict) and 'quiz' in st.session_state.script[part_key]:
            quiz = st.session_state.script[part_key]['quiz']
            st.subheader("Quick Quiz")
            user_answer = st.radio(quiz['question'], quiz['options'], key=f"quiz_{st.session_state.current_part}")
            if st.button("Check Answer", key=f"check_answer_{st.session_state.current_part}"):
                if user_answer == quiz['answer']:
                    st.success("Correct! Well done!")
                    st.session_state.quiz_correct = True
                else:
                    st.error(f"Not quite. The correct answer is: {quiz['answer']}")
                    st.session_state.quiz_correct = False

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_part > 1:
                if st.button("⬅️ Go Back", key=f"back_{st.session_state.current_part}"):
                    st.session_state.current_part -= 1
                    st.session_state.quiz_correct = False
                    st.rerun()
        with col2:
            if st.button("Continue to Next Part ➡️", key=f"next_{st.session_state.current_part}"):
                if not isinstance(st.session_state.script[part_key], dict) or 'quiz' not in st.session_state.script[part_key] or st.session_state.quiz_correct:
                    st.session_state.current_part += 1
                    st.session_state.quiz_correct = False
                    st.rerun()
                else:
                    st.warning("Please answer the quiz correctly before proceeding.")

    # Display abstract experience
    elif st.session_state.current_part == 8:
        st.subheader("Abstract Experience: Try it out!")
        abstract_experience = st.session_state.script['abstract_experience']
        st.write(abstract_experience['instruction'])
        st.write(abstract_experience['content'])

        st.session_state.abstract_experience_result = st.text_area("Share your experience or results:", value=st.session_state.abstract_experience_result, height=150)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Go Back", key="back_abstract"):
                st.session_state.current_part = 7
                st.rerun()
        with col2:
            if st.button("Submit Experience", key="submit_abstract"):
                if st.session_state.abstract_experience_result.strip():
                    st.success("Thank you for sharing your experience!")
                    time.sleep(1)
                else:
                    st.warning("Please share your experience before submitting.")
        with col3:
            if st.button("Continue to Review ➡️", key="next_abstract"):
                if st.session_state.abstract_experience_result.strip():
                    st.session_state.current_part += 1
                    st.rerun()
                else:
                    st.warning("Please share your experience before continuing.")

        # Display the generated image or placeholder
        if st.session_state.career_image:
            st.image(st.session_state.career_image, caption=f"A day in the life of a {st.session_state.career}", use_column_width=True)
        else:
            st.warning("Career image could not be generated. Please try again later.")

    # Display review after all parts
    elif st.session_state.current_part == 9:
        st.subheader("Review: Reflecting on Your Career Experience")
        st.write(st.session_state.script['review']['content'])
        
        # Final quiz
        quizzes = st.session_state.script['review']['quiz']
        st.subheader("Final Quiz")
        
        all_correct = True
        for i, quiz in enumerate(quizzes):
            user_answer = st.radio(quiz['question'], quiz['options'], key=f"final_quiz_{i}")
            if st.button(f"Submit Answer for Question {i+1}", key=f"submit_final_quiz_{i}"):
                if user_answer == quiz['answer']:
                    st.success("Correct! Well done!")
                else:
                    st.error(f"Not quite. The correct answer is: {quiz['answer']}")
                    all_correct = False

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Go Back", key="back_review"):
                st.session_state.current_part = 8
                st.rerun()
        with col2:
            if st.button("Finish Experience 🎉", key="finish_experience"):
                if all_correct:
                    st.balloons()
                    st.success("Congratulations! You've completed the career experience successfully!")
                    st.session_state.script = None
                    st.session_state.current_part = 1
                    st.session_state.career = ""
                    st.session_state.abstract_experience_result = ""
                    st.session_state.quiz_correct = False
                    st.session_state.career_image = None
                    st.rerun()
                else:
                    st.warning("Please answer all quiz questions correctly before finishing.")

# Footer
st.markdown("---")
st.markdown("© 2024 Career Experience Helper. All rights reserved.")
