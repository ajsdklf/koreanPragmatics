import streamlit as st 
from openai import OpenAI 
import json
from pydantic import BaseModel
import random

st.set_page_config(page_title="Idiom Master", page_icon="🇰🇷", layout="wide")

st.title('🇰🇷 Korean Idiom Master 🎓')
st.markdown("### Learn Korean idioms in context and test your understanding!")

client = OpenAI() 

class Conversation(BaseModel):
    history: list[dict] = []
    current_situation: str = ""
    correct_idiom: str = ""
    incorrect_idiom: str = ""
    explanation: str = ""

def generate_and_validate_idioms():
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a Korean language expert specializing in idioms and their contextual usage."},
            {"role": "user", "content": """Generate two Korean idioms: one correct and one incorrect for a given situation.
            Ensure that both idioms are authentic Korean expressions, with the incorrect one being plausible but not fitting the context.
            Also, provide a brief explanation of why the correct idiom is appropriate and why the incorrect one doesn't fit.
            Format your response as a JSON object with keys: 'correct_idiom', 'incorrect_idiom', 'explanation'."""}
        ],
        response_format={ "type": "json_object" }
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return data['correct_idiom'], data['incorrect_idiom'], data['explanation']
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON response from the API. Please try again.")
        return "", "", ""

def validate_idioms(correct_idiom, incorrect_idiom):
    validation_prompt = f"""
    Validate the following Korean idioms:
    1. {correct_idiom}
    2. {incorrect_idiom}

    Confirm if both are authentic Korean idioms and provide a brief assessment of their suitability for language learning.
    If either is not suitable, explain why and suggest an alternative.
    """
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a Korean language expert tasked with validating idioms for educational purposes."},
            {"role": "user", "content": validation_prompt}
        ]
    )
    return response.choices[0].message.content

def generate_situation_and_idioms():
    situation_response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a Korean language expert specializing in creating realistic conversational scenarios."},
            {"role": "user", "content": """Generate a detailed conversation situation in Korean (with English translation).
            The situation should be suitable for demonstrating the use of Korean idioms.
            Provide your response in the following JSON format: 
            {
                'situation_kr': '...',
                'situation_en': '...'
            }"""}
        ],
        response_format={ "type": "json_object" }
    )
    situation_content = situation_response.choices[0].message.content
    try:
        situation_data = json.loads(situation_content)
        correct_idiom, incorrect_idiom, explanation = generate_and_validate_idioms()
        validation_result = validate_idioms(correct_idiom, incorrect_idiom)
        
        if "not suitable" in validation_result.lower():
            st.warning("Generated idioms were not suitable. Regenerating...")
            return generate_situation_and_idioms()
        
        return (situation_data['situation_kr'], situation_data['situation_en'], 
                correct_idiom, incorrect_idiom, explanation)
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON response from the API. Please try again.")
        return "", "", "", "", ""

def continue_conversation(choice, conversation):
    prompt = f"""
    Situation: {conversation.current_situation}
    User's choice: {choice}
    Conversation history: {conversation.history}
    
    Continue the conversation based on the user's choice. If the choice was correct, provide a detailed explanation and encouragement.
    If incorrect, show the other person's subtle confusion or misunderstanding due to the inappropriate idiom usage, and explain why it was incorrect.
    Respond in both Korean and English.
    """
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a helpful Korean language tutor that provides detailed feedback on idiom usage."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = Conversation()

# Generate new situation and idioms
if st.button("🔄 New Situation", key="new_situation"):
    with st.spinner("Generating new scenario..."):
        situation_kr, situation_en, correct, incorrect, explanation = generate_situation_and_idioms()
        if situation_kr and situation_en and correct and incorrect:
            st.session_state.conversation = Conversation(
                current_situation=f"{situation_kr}\n\n{situation_en}",
                correct_idiom=correct,
                incorrect_idiom=incorrect,
                explanation=explanation
            )

# Display current situation
if st.session_state.conversation.current_situation:
    st.markdown("## 🎭 Current Situation")
    st.markdown(st.session_state.conversation.current_situation)
    
    # Display options
    st.markdown("### 🤔 Choose the appropriate idiom:")
    options = [st.session_state.conversation.correct_idiom, 
            st.session_state.conversation.incorrect_idiom]
    random.shuffle(options)
    choice = st.radio("", options, key="idiom_choice")
    
    if st.button("✅ Submit", key="submit_choice"):
        with st.spinner("Analyzing your choice..."):
            response = continue_conversation(choice, st.session_state.conversation)
            st.session_state.conversation.history.append({"role": "assistant", "content": response})
            st.markdown("### 🗣️ Feedback:")
            st.markdown(response)
        
        if choice == st.session_state.conversation.correct_idiom:
            st.success("🎉 Correct! Great job!")
            st.markdown("### 📚 Explanation:")
            st.info(st.session_state.conversation.explanation)
        else:
            st.error("❌ Oops! That wasn't quite right. Let's learn from this!")
            st.markdown("### 📚 Correct Usage:")
            st.info(st.session_state.conversation.explanation)

# Display conversation history
if st.session_state.conversation.history:
    st.markdown("## 📜 Conversation History")
    for i, message in enumerate(st.session_state.conversation.history):
        with st.expander(f"Interaction {i+1}"):
            st.markdown(message['content'])
            
            
# 관용구를 인풋으로 -> 관용구를 써야할지 안써야할지 의사결정하게 하기 