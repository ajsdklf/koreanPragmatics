import pandas as pd
import plotly.express as px
import streamlit as st
from openai import AsyncOpenAI, OpenAI
import numpy as np
import asyncio
import json

# Initialize OpenAI clients
async_client = AsyncOpenAI()
client = OpenAI()

# Initialize session state
# Note: Session state is used to maintain the app's state.
for key in ['confidence_history', 'threshold', 'messages', 'extracted_info', 'chat_history', 'current_action']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['confidence_history', 'messages', 'chat_history'] else (0.6 if key == 'threshold' else ({} if key == 'extracted_info' else None))

# Streamlit page configuration
st.set_page_config(page_title="GGPP Algorithm Demo", layout="wide")
st.title("GGPP (낄끼빠빠) Algorithm")

# Sidebar and introduction section
with st.sidebar:
    st.header("Available Tasks")
    st.info("""
    The model can perform the following tasks:
    1. Weather Forecast: Provides weather information for a given location.
    2. Restaurant Recommendation: Recommends restaurants based on cuisine and location.
    3. Language Translation: Translates text from one language to another.
    4. General Conversation: Engages in general dialogue with users.
    """)
    st.session_state.threshold = st.slider("Set Confidence Threshold", 0.0, 1.0, st.session_state.threshold, 0.01)

with st.expander("Introduction to GGPP Algorithm", expanded=True):
    st.markdown("""
    This demo showcases the operation of the GGPP (낄끼빠빠) Algorithm.
    
    The app demonstrates a mathematical approach for enabling LLMs to develop situational awareness.
    
    This algorithm allows LLMs to measure their confidence when making function calls or taking actions, enabling them to develop 'situational awareness' about whether to proceed with an action.
    """)
    
PROMPT = """Answer with either Forecast, """

# Helper functions
def calculate_entropy(probabilities):
    """
    Calculate the entropy of a given probability distribution.
    
    :param probabilities: List of probabilities
    :return: Entropy value
    """
    return -sum(p * np.log2(p) for p in probabilities if p > 0)

def ggpp_algorithm(action_probabilities):
    """
    Implement the GGPP algorithm.
    
    :param action_probabilities: List of probabilities for each action
    :return: Decision (string) and confidence (float)
    """
    entropy = calculate_entropy(action_probabilities)
    max_entropy = np.log2(len(action_probabilities))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    confidence = 1 - normalized_entropy
    
    if confidence >= 0.8:
        return "Take action", confidence
    elif 0.6 <= confidence < 0.8:
        return "Evaluate", confidence
    else:
        return "Chitchat", confidence

def display_confidence_meter(confidence):
    """
    Display a confidence meter.
    
    :param confidence: Confidence value (float between 0 and 1)
    """
    st.write("Confidence Meter:")
    st.progress(confidence)

# System prompts
SYSTEM_PROMPTS = {
    'weather': "You are an AI assistant specialized in providing weather forecasts. Analyze the given text and determine if it's requesting weather information. Respond with 'True' if the text appears to be asking for weather information or forecasts, and 'False' otherwise. Your response must be either 'True' or 'False' without any additional explanation.",
    'restaurant': "You are an AI assistant specialized in restaurant recommendations. Analyze the given text and determine if it's requesting restaurant suggestions. Respond with 'True' if the text appears to be asking for restaurant or food recommendations, and 'False' otherwise. Your response must be either 'True' or 'False' without any additional explanation.",
    'translation': "You are an AI assistant specialized in language translation. Analyze the given text and determine if it requires translation. Respond with 'True' if the text appears to be requesting or needing translation, and 'False' otherwise. Your response must be either 'True' or 'False' without any additional explanation.",
    'chitchat': "You are an AI assistant capable of engaging in general conversation. Analyze the given text and determine if it's suitable for general chat. Respond with 'True' if the text doesn't fit into other specific categories (weather forecast, restaurant recommendation, translation) and seems appropriate for general conversation, and 'False' otherwise. Your response must be either 'True' or 'False' without any additional explanation.",
    'evaluate': "You are an AI assistant capable of evaluating the essential meaning of user requests. Analyze the given text and provide a brief explanation of its core intent or meaning. Respond with a concise explanation of what the user is trying to convey or ask, focusing on the underlying purpose of the message."
}

# OpenAI API functions
async def ggpp_response(system_prompt, user_prompt, model="gpt-4o", top_logprobs=2):
    """
    Generate a response using the OpenAI API.
    
    :param system_prompt: System prompt
    :param user_prompt: User prompt
    :param model: Model name to use
    :param top_logprobs: Number of top log probabilities
    :return: API response
    """
    try:
        response = await async_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            logprobs=True,
            top_logprobs=top_logprobs,
        )
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def extract_logprobs(response):
    """
    Extract log probabilities from the API response.
    
    :param response: API response
    :return: Tuple of log probabilities and linear probabilities
    """
    if response and response.choices:
        logprobs = response.choices[0].logprobs.content[0].top_logprobs
        log_probs = [logprob.logprob for logprob in logprobs]
        linear_probs = [np.exp(log_prob) for log_prob in log_probs]
        return log_probs, linear_probs
    return [], []  # Return empty lists if no valid response

async def process_responses(user_input):
    """
    Process multiple responses for user input asynchronously.
    
    :param user_input: User input
    :return: List of normalized action probabilities
    """
    tasks = [ggpp_response(SYSTEM_PROMPTS[key], user_input) for key in ['weather', 'restaurant', 'translation', 'chitchat']]
    responses = await asyncio.gather(*tasks)
    
    action_probs = []
    for response in responses:
        _, linear_probs = extract_logprobs(response)
        if linear_probs:
            action_probs.append(linear_probs[0] if response.choices[0].message.content == "True" else linear_probs[1])
        else:
            action_probs.append(0.0)  # Assign 0 probability if no valid response
    
    total_prob = sum(action_probs)
    return [prob / total_prob for prob in action_probs] if total_prob > 0 else [0.25, 0.25, 0.25, 0.25]

def evaluate_input(user_input):
    """
    Evaluate the meaning of user input.
    
    :param user_input: User input
    :return: Evaluation result
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS['evaluate']},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content if response else "Unable to evaluate input."

def get_action_prompt(action, *args):
    """
    Generate a prompt for the given action.
    
    :param action: Action to perform
    :param args: Additional arguments needed for the action
    :return: Generated prompt string
    """
    if action == "Weather-Forecast":
        return f"Provide a concise weather forecast for {args[0]}. Include temperature, precipitation chance, and any notable weather conditions."
    elif action == "Restaurant-Recommendation":
        return f"Recommend three {args[0]} restaurants in {args[1]}. For each, provide the name, a brief description, and what they're known for."
    elif action == "Language-Translation":
        return f"Translate the following text to {args[1]}, maintaining the original meaning and tone as closely as possible: {args[0]}"
    else:
        return ""

def perform_action(action, user_input):
    """
    Perform the selected action.
    
    :param action: Action to perform
    :param user_input: User input or extracted information
    :return: Result of the action
    """
    system_content = get_action_prompt(action, *user_input)
    
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": "Assistant: "}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but there was an error processing your request: {str(e)}. Please try again."

def perform_chitchat():
    """
    Perform general conversation.
    
    :return: Result of the chitchat
    """
    messages = [
        {"role": "system", "content": "You are a friendly, conversational AI assistant. Engage in a natural, empathetic dialogue, providing informative and engaging responses while maintaining a casual tone."},
    ]
    
    for message in st.session_state.chat_history:
        messages.append({"role": message["role"], "content": message["content"]})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content 

def extract_info(user_input, action):
    """
    Extract necessary information from user input.
    
    :param user_input: User input
    :param action: Action to perform
    :return: Extracted information
    """
    required_info = {
        "Weather-Forecast": ["location", "date"],
        "Restaurant-Recommendation": ["cuisine", "location"],
        "Language-Translation": ["text", "target_language"],
    }
    
    info_to_extract = required_info.get(action, [])
    combined_input = user_input + " " + " ".join(f"{k}: {v}." for k, v in st.session_state.extracted_info.items())
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Extract the following information from the user input: {', '.join(info_to_extract)}. Return the extracted information as a JSON object. If all information is extracted, return a JSON object with this structure: {{\"extracted\": true, \"extracted_info\": [dictionary of extracted info with keys matching those given in the prompt]}}. If not all required information could be extracted, return a JSON object with this structure: {{\"extracted\": false, \"extracted_info\": [extracted info], \"missing_info\": [missing info]}}. Be precise and concise in your extraction."},
            {"role": "user", "content": combined_input}
        ],
        response_format={ "type": "json_object" }
    )
    
    response = json.loads(response.choices[0].message.content)
    if 'extracted_info' in response:
        st.session_state.extracted_info.update(response['extracted_info'])
    
    return response

# Main Streamlit app logic
st.header("GGPP Algorithm Demo")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Main Streamlit app logic (continued)
if user_input := st.chat_input("How can I assist you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.spinner("Processing..."):
        try:
            # Process responses for user input
            action_probs = asyncio.run(process_responses(user_input))
            decision, confidence = ggpp_algorithm(action_probs)
            st.session_state.confidence_history.append(confidence)

            # Create tabs
            tabs = st.tabs(["Decision", "Action Probabilities", "Confidence", "Trend"])

            with tabs[0]:
                # Display current action
                if st.session_state.current_action:
                    st.success(f"Current Action: {st.session_state.current_action}")
                else:
                    st.info("No specific action is currently being performed.")

                actions = ["Weather-Forecast", "Restaurant-Recommendation", "Language-Translation", "Chit-Chat"]
                selected_action = actions[np.argmax(action_probs)] if decision == "Take action" else None
                
                st.info(f"Selected Action: {selected_action}")
                st.info(f"confidence: {confidence:.2f}")
                
                try:
                    if decision == "Take action":
                        # Perform selected action
                        if selected_action == "Chit-Chat":
                            response = perform_chitchat()
                            st.session_state.current_action = None
                        else:
                            if st.session_state.current_action is None:
                                st.session_state.current_action = selected_action
                            info = extract_info(user_input, st.session_state.current_action)
                            if info["extracted"]:
                                response = perform_action(st.session_state.current_action, list(info["extracted_info"].values()))
                                st.session_state.extracted_info = {}  # Reset extracted info
                                st.session_state.current_action = None  # Reset current action
                            else:
                                response = f"Could you please provide the following information as well? {', '.join(info['missing_info'])}"
                    elif decision == "Evaluate":
                        # Evaluate user input
                        evaluation = evaluate_input(user_input)
                        st.info(f"Evaluation: {evaluation}")
                        if st.session_state.current_action is None:
                            action_keyword = next((action for action in actions if action.lower().split('-')[0] in evaluation.lower()), "Chit-Chat")
                            st.session_state.current_action = action_keyword
                        info = extract_info(user_input, st.session_state.current_action)
                        if info["extracted"]:
                            response = perform_action(st.session_state.current_action, list(info["extracted_info"].values()))
                            st.session_state.extracted_info = {}  # Reset extracted info
                            st.session_state.current_action = None  # Reset current action
                        else:
                            response = f"It seems you're asking about {st.session_state.current_action.lower().replace('-', ' ')}. Could you provide the following information? {', '.join(info['missing_info'])}"
                    else:
                        # Perform general conversation
                        response = perform_chitchat()
                        st.session_state.current_action = None
                except Exception as e:
                    response = f"I apologize, but there's an issue processing your request at the moment. Could you please try again later? Error: {str(e)}"
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history.append({"role": "assistant", "content": response})

            with tabs[1]:
                # Display action probabilities
                st.subheader("Action Probabilities")
                for action, prob in zip(actions, action_probs):
                    st.metric(label=action, value=f"{prob:.2f}")
                    st.progress(prob)

            with tabs[2]:
                # Display current confidence
                st.subheader("Confidence")
                st.metric("Current Confidence", f"{confidence:.4f}")
                display_confidence_meter(confidence)

            with tabs[3]:
                # Generate confidence trend graph
                st.subheader("Confidence Trend")
                df = pd.DataFrame({
                    'Iteration': range(1, len(st.session_state.confidence_history) + 1),
                    'Confidence': st.session_state.confidence_history
                })
                
                fig = px.line(df, x='Iteration', y='Confidence', line_shape='spline', markers=True)
                fig.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Take Action Threshold")
                fig.add_hline(y=0.6, line_dash="dash", line_color="red", annotation_text="Chitchat Threshold")
                
                fig.update_layout(
                    title_text='Confidence Trend Over Time',
                    title_x=0.5,
                    xaxis_title='Iteration',
                    yaxis_title='Confidence',
                    yaxis_range=[0, 1],
                    template='plotly_white',
                    height=500,
                )
                
                fig.update_traces(
                    hovertemplate='<b>반복</b>: %{x}<br><b>신뢰도</b>: %{y:.2f}'
                )
                
                # 대화형 차트 표시
                st.plotly_chart(fig, use_container_width=True)
                
                # 신뢰도 기록 데이터 테이블 표시
                st.subheader("신뢰도 기록")
                st.dataframe(df.style.highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightpink'))

        except Exception as e:
            st.error(f"요청을 처리하는 동안 오류가 발생했습니다: {str(e)}")

# 앱 설명
st.caption("이 데모는 향상된 GGPP 알고리즘을 보여줍니다. 신뢰도가 0.8 이상이면 선택된 행동을 수행하고, 0.6에서 0.8 사이면 요청의 본질적 의미를 평가하며, 0.6 미만이거나 일반 대화의 확률이 가장 높으면 일반 대화를 수행합니다.")