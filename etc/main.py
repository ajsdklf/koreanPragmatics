import streamlit as st 
from openai import OpenAI 
import anthropic 
import os 
import json 
from dotenv import load_dotenv 

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client_openai = OpenAI(api_key=OPENAI_API_KEY)
client_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

st.title("Demo 2: KOREAN LEARNING WITH INTERACTION")

ICEBREAKER = """
You are an assistant ice breaking with user. We are making a Korean learning app, and we need your help to make the conversation more engaging. Your focus should be on making the conversation more engaging and fun while trying to get the following information as naturally as you can:
###
1. What context user wants to use to generate a example sentence in Korean.
2. Specific sentence in English that user wants to translate into Korean. 
###
You have to make sure that the conversation is engaging and fun while getting the information from the user. To do this, you can ask questions, share interesting facts, or even tell jokes.
"""

KOREAN_TEACHER = """
You are a Korean teacher. User is a foreigner whose native language is English. You need to generate solid examples that users could use to learn Korean. Your example should be explained as detailed as possible to help user understand the exact context and usage of that example sentence. As an input, you will be given the following informations:
###
1. Context user wants to use to generate a example sentence in Korean.
2. Specific sentence in English that user wants to translate into Korean.
###

Based on the above given information, you need to generate a example sentence in Korean and provide detailed explanation.
"""

FUNCTION_CALLER = """
As an input, you will be given a conversation between the user and the AI assistant. When given the enough information in the converstaion, you need to call a function named 'KOREAN_TEACHER' to generate a example sentence in Korean. Followings are the information you need to call function:

###
1. Context user wants to use to generate a example sentence in Korean.
2. Specific sentence in English that user wants to translate into Korean.
###

When given those infomrations, you need to call the function 'KOREAN_TEACHER' to generate a example sentence in Korean.
"""

ADDITIONAL_EXPLAINER = """
You are an additional explainer for user who is interested in learning Korean. User is interested in learning Korean and wants to know more about the example sentence in Korean. You need to provide additional explanation for the example sentence in Korean. As an input, you will be given the following informations:
###
1. User's request for additional explanation.
2. Example sentence in Korean that user wants to get additional explanation.
###

Based on the above given information, you need to provide additional explanation for the example sentence in Korean. Your explanation must be as detailed as possible to help user understand the exact context and usage of that example sentence. 
"""

def call_korean_teacher(sentence, context):
    example = client_openai.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': KOREAN_TEACHER},
            {'role': 'user', 'content': f"I want to learn how to say '{sentence}' in Korean. I also want some examples that is used in {context}."}
        ]
    ).choices[0].message.content
    
    return example

def call_additional_explainer(request, sentence):
    explanation = client_openai.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'system', 'content': ADDITIONAL_EXPLAINER}, {'role': 'user', 'content': f"For '{sentence}', User wants to know more about {request}."}]
    ).choices[0].message.content
    
    return explanation

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'call_korean_teacher',
            'description': 'Create example sentences and explanation in Korean.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'context': {
                        'type': 'string',
                        'description': 'Context user wants to use to generate a example sentence in Korean.'
                    },
                    'sentence': {
                        'type': 'string',
                        'description': 'Specific sentence in English that user wants to translate into Korean.'
                    },
                },
                'required': [
                    'context',
                    'sentence'
                ]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'call_additional_explainer',
            'description': 'Provide additional explanation for the example sentence in Korean.',
            'parameters': {
                'type': 'object', 
                'properties': {
                    'request': {
                        'type': 'string',
                        'description': "User's request for additional explanation."
                    },
                    'sentence': {
                        'type': 'string',
                        'description': 'Example sentence in Korean that user wants to get additional explanation.'
                    }
                },
                'required': [
                    'request',
                    'sentence'
                ],
            }
        }
    }
]


if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'initialize' not in st.session_state:
    st.session_state.initialize = False

with st.expander('Explanation about our service'):
    """
    1. Start talking with AI assistant by saying "Hello".
    2. Talk with AI assistant about your daily life, your interest, or really just anything you want to talk about. 
    3. Based on the conversation, AI assistant will automatically generate you a example sentence in Korean and provide detailed explanation. 
    """

def init():
    st.session_state.initialize = True

if st.session_state.initialize == False:
    st.session_state.messages.append({'role': 'assistant', 'content': 'Hello! How are you doing?'})

initializer = st.button('start learning!', on_click=init)

if st.session_state.initialize:
    user_input = st.chat_input('You: ')
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    if user_input:
        with st.chat_message('user'):
            st.markdown(user_input)
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        messages = [{'role': 'system', 'content': FUNCTION_CALLER}] + [msg for msg in st.session_state.messages]
        tool_calls = client_openai.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            tools=tools,
            tool_choice='auto'
        ).choices[0].message.tool_calls
        if tool_calls == None:
            AI_response = client_openai.chat.completions.create(
                model='gpt-4o',
                messages=[{'role': 'system', 'content': ICEBREAKER}] + [msg for msg in st.session_state.messages]
            ).choices[0].message.content
            st.session_state.messages.append({'role': 'assistant', 'content': AI_response})
            with st.chat_message('assistant'):
                st.markdown(AI_response)
        else:
            if tool_calls[0].function.name == 'call_korean_teacher':
                arguments = tool_calls[0].function.arguments
                args_dict = json.loads(arguments)
                sentence = args_dict['sentence']
                context = args_dict['context']
                example = call_korean_teacher(sentence=sentence, context=context)
                with st.chat_message('assistant'):
                    st.markdown(example)
                with st.chat_message('assistant'):
                    st.markdown('If you want more explanations, feel free to ask whatever. I am here to help you!')
                st.session_state.messages.append({'role': 'assistant', 'content': example})
            if tool_calls[0].function.name == 'call_additional_explainer':
                arguments = tool_calls[0].function.arguments
                args_dict = json.loads(arguments)
                request = args_dict['request']
                sentence = args_dict['sentence']
                explanation = call_additional_explainer(request=request, sentence=sentence)
                with st.chat_message('assistant'):
                    st.markdown(explanation)
                with st.chat_message('assistant'):
                    st.markdown('If you want more extra explanations, feel free to ask whatever. I am here to help you!') 
                st.session_state.messages.append({'role': 'assistant', 'content': explanation})
