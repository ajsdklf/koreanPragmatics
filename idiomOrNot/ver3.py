import random 
import streamlit as st
from module.runnables import *
import os

st.set_page_config(page_title="Idiom or Not", page_icon="🗣️", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        width: 100%;
    }
    .stRadio>div {
        flex-direction: row;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Idiom or Not 🗣️")
st.markdown("Explore the world of idioms and test your understanding!")

# Initialize session state variables
if 'idiom' not in st.session_state:
    st.session_state.idiom = ""
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'scenario_generated' not in st.session_state:
    st.session_state.scenario_generated = False
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'dialogue_step' not in st.session_state:
    st.session_state.dialogue_step = 0
if 'answer_checked' not in st.session_state:
    st.session_state.answer_checked = False
if 'audio_generated' not in st.session_state:
    st.session_state.audio_generated = {}
if 'examples_rendered' not in st.session_state:
    st.session_state.examples_rendered = False
if 'dialogue_audio' not in st.session_state:
    st.session_state.dialogue_audio = []

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    idiom_to_use = st.text_input("Enter an idiom to explore:", placeholder="e.g., 'Break a leg'")
with col2:
    def initialize():
        if idiom_to_use:
            st.session_state.idiom = idiom_to_use
            st.session_state.initialized = True
            st.session_state.analysis = None
            st.session_state.scenario_generated = False
            st.session_state.scenario = None
            st.session_state.dialogue_step = 0
            st.session_state.answer_checked = False
            st.session_state.audio_generated = {}
            st.session_state.examples_rendered = False
            st.session_state.dialogue_audio = []
        else:
            st.warning("Please enter an idiom first!")

    initializer = st.button("Analyze Idiom", on_click=initialize, type="primary")

# Analysis section
if st.session_state.initialized and st.session_state.idiom and not st.session_state.analysis:
    with st.spinner("🔍 Analyzing the idiom..."):
        try:
            analysis = extract_pragmatic_meaning(st.session_state.idiom)
            st.session_state.analysis = analysis
            st.success("✅ Analysis complete!")
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.session_state.initialized = False

if st.session_state.analysis:
    st.markdown("### 📊 Idiom Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Idiom:** {st.session_state.analysis.idiom}")
        if 'idiom_audio' not in st.session_state.audio_generated:
            generate_audio(f"Idiom: {st.session_state.analysis.idiom}", "idiom_audio.mp3", "alloy")
            st.session_state.audio_generated['idiom_audio'] = True
        st.audio("idiom_audio.mp3")
        
        st.markdown("**Pragmatic Meaning:**")
        st.info(st.session_state.analysis.pragmatic_meaning)
        if 'pragmatic_meaning_audio' not in st.session_state.audio_generated:
            generate_audio(f"Pragmatic Meaning: {st.session_state.analysis.pragmatic_meaning}", "pragmatic_meaning_audio.mp3", "nova")
            st.session_state.audio_generated['pragmatic_meaning_audio'] = True
        st.audio("pragmatic_meaning_audio.mp3")
    with col2:
        st.markdown("**Examples:**")
        examples_audio = "Examples: "
        for i, example in enumerate(st.session_state.analysis.examples, 1):
            st.success(f"{i}. {example}")
            examples_audio += f"Example {i}: {example}. "
        if 'examples_audio' not in st.session_state.audio_generated:
            generate_audio(examples_audio, "examples_audio.mp3", "shimmer")
            st.session_state.audio_generated['examples_audio'] = True
        st.audio("examples_audio.mp3")
    st.markdown("**Caution:**")
    st.warning(st.session_state.analysis.caution)
    if 'caution_audio' not in st.session_state.audio_generated:
        generate_audio(f"Caution: {st.session_state.analysis.caution}", "caution_audio.mp3", "echo")
        st.session_state.audio_generated['caution_audio'] = True
    st.audio("caution_audio.mp3")

    # Scenario generation
    if not st.session_state.scenario_generated:
        if st.button("Generate Scenario", type="primary"):
            with st.spinner("🎲 Generating scenario..."):
                try:
                    st.session_state.is_correct = False
                    st.session_state.scenario = generate_idiom_scenario(st.session_state.idiom, st.session_state.is_correct)
                    st.session_state.scenario_generated = True
                    st.session_state.dialogue_step = 0
                    st.session_state.audio_generated = {k: v for k, v in st.session_state.audio_generated.items() if not k.startswith('dialogue_')}  # Reset only scenario audio
                    st.session_state.dialogue_audio = []
                    # Generate all dialogue audio at once
                    for i, dialogue in enumerate(st.session_state.scenario.conversation_including_idiom):
                        voice = random.choice(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
                        generate_audio(dialogue, f"dialogue_{i}_audio.mp3", voice)
                        st.session_state.dialogue_audio.append(f"dialogue_{i}_audio.mp3")
                    st.success("✅ Scenario generated!")
                except Exception as e:
                    st.error(f"An error occurred while generating the scenario: {str(e)}")

# Scenario display and interaction
if st.session_state.scenario_generated:
    st.subheader("Scenario Context:")
    st.write(st.session_state.scenario.overall_context)
    if 'scenario_context_audio' not in st.session_state.audio_generated:
        generate_audio(f"Scenario Context: {st.session_state.scenario.overall_context}", "scenario_context_audio.mp3", "alloy")
        st.session_state.audio_generated['scenario_context_audio'] = True
    st.audio("scenario_context_audio.mp3")
    
    st.subheader("Conversation:")
    for i in range(min(st.session_state.dialogue_step + 1, len(st.session_state.scenario.conversation_including_idiom))):
        st.write(st.session_state.scenario.conversation_including_idiom[i])
        st.audio(st.session_state.dialogue_audio[i])
    
    if st.session_state.dialogue_step < len(st.session_state.scenario.conversation_including_idiom) - 1:
        if st.button("Continue", key="continue_dialogue"):
            st.session_state.dialogue_step += 1
    else:
        st.success("Conversation complete!")
        
        st.subheader("Was the idiom used appropriately?")
        user_choice = st.radio(
            "Select your answer:",
            ("Yes, it was used appropriately", "No, it was used inappropriately"),
            key="user_idiom_choice"
        )
        
        if not st.session_state.answer_checked:
            if st.button("Check Answer", key="check_answer"):
                correct_answer = "Yes, it was used appropriately" if st.session_state.scenario.is_right else "No, it was used inappropriately"
                if user_choice == correct_answer:
                    result = "Correct! You've identified the usage correctly."
                    st.success(result)
                else:
                    result = "Incorrect. Let's review the explanation to understand better."
                    st.error(result)
                if 'answer_result_audio' not in st.session_state.audio_generated:
                    generate_audio(result, "answer_result_audio.mp3", "nova")
                    st.session_state.audio_generated['answer_result_audio'] = True
                st.audio("answer_result_audio.mp3")
                st.session_state.answer_checked = True
        
        if st.session_state.answer_checked:
            with st.expander("Reveal Explanation", expanded=False):
                st.subheader("Explanation:")
                st.write(st.session_state.scenario.explanation)
                if 'explanation_audio' not in st.session_state.audio_generated:
                    generate_audio(f"Explanation: {st.session_state.scenario.explanation}", "explanation_audio.mp3", "alloy")
                    st.session_state.audio_generated['explanation_audio'] = True
                st.audio("explanation_audio.mp3")
            
            st.subheader("Other expressions:")
            other_expressions_audio = "Other expressions: "
            for expr in st.session_state.scenario.other_expressions:
                st.info(f"- {expr}")
                other_expressions_audio += f"{expr}. "
            if 'other_expressions_audio' not in st.session_state.audio_generated:
                generate_audio(other_expressions_audio, "other_expressions_audio.mp3", "shimmer")
                st.session_state.audio_generated['other_expressions_audio'] = True
            st.audio("other_expressions_audio.mp3")
            
            st.subheader("Follow-up Conversation:")
            for i, line in enumerate(st.session_state.scenario.follow_up_conversation):
                st.write(line)
                if f'follow_up_{i}_audio' not in st.session_state.audio_generated:
                    voice = random.choice(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
                    generate_audio(line, f"follow_up_{i}_audio.mp3", voice)
                    st.session_state.audio_generated[f'follow_up_{i}_audio'] = True
                st.audio(f"follow_up_{i}_audio.mp3")

    if st.button("Start Over", key="start_over"):
        for key in ['idiom', 'initialized', 'is_correct', 'analysis', 'scenario_generated', 'scenario', 'dialogue_step', 'answer_checked', 'audio_generated', 'examples_rendered', 'dialogue_audio']:
            if key in st.session_state:
                del st.session_state[key]
        # Clean up audio files
        for file in os.listdir():
            if file.endswith(".mp3"):
                os.remove(file)
        st.rerun()