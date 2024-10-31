import streamlit as st
import instructor 
from pydantic import BaseModel
from openai import OpenAI

client = instructor.from_openai(OpenAI())

class User(BaseModel):
    name: str
    age: int

class Story(BaseModel):
    paragraph1: str
    paragraph2: str
    paragraph3: str
    paragraph4: str

# Initialize session state for paragraphs and generation state
if "paragraph1" not in st.session_state:
    st.session_state["paragraph1"] = ""
if "paragraph2" not in st.session_state:
    st.session_state["paragraph2"] = ""
if "paragraph3" not in st.session_state:
    st.session_state["paragraph3"] = ""
if "paragraph4" not in st.session_state:
    st.session_state["paragraph4"] = ""
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
if "current_paragraph" not in st.session_state:
    st.session_state["current_paragraph"] = 1

# Create containers for each paragraph
st.title("Story Generation")

# Add generate button at the top
if st.button("Generate Story") and not st.session_state["is_generating"]:
    # Reset paragraphs
    for i in range(1, 5):
        st.session_state[f"paragraph{i}"] = ""
    st.session_state["is_generating"] = True
    st.session_state["current_paragraph"] = 1
    
    try:
        # Generate current paragraph
        story_part = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Generate paragraph {st.session_state['current_paragraph']} of a 4-paragraph story."},
                {"role": "user", "content": f"Create paragraph {st.session_state['current_paragraph']} of a creative story."},
            ],
            response_model=Story
        )
        
        # Update session state with generated paragraph
        current_para = st.session_state["current_paragraph"]
        st.session_state[f"paragraph{current_para}"] = getattr(story_part, f"paragraph{current_para}")
        
        if current_para < 4:
            st.session_state["current_paragraph"] += 1
            st.rerun()
        else:
            st.session_state["is_generating"] = False
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state["is_generating"] = False

# Display paragraphs
containers = [st.container() for _ in range(4)]
for i, container in enumerate(containers, 1):
    with container:
        st.subheader(f"Paragraph {i}")
        if st.session_state[f"paragraph{i}"]:
            st.markdown(f"""
            <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6;'>
                {st.session_state[f'paragraph{i}']}
            </div>
            """, unsafe_allow_html=True)
        else:
            status = "Waiting..." if i > st.session_state["current_paragraph"] else "Generating..." if st.session_state["is_generating"] else "Click 'Generate Story' to create a new story"
            st.info(status)
        st.markdown("---")
