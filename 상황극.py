import streamlit as st 
from openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core import Settings 
from llama_index.llms.openai import OpenAI as OpenAI_llama
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.query_engine import RetrieverQueryEngine
import json 

Settings.llm = OpenAI_llama(model='gpt-3.5-turbo')
client = OpenAI()

st.title("특허를 위한 데모 : 상황극 데모")

DECIDER = """
You are a decider. Based on the given context which consists of user and assistant's conversation and the user's current learning level, you need to decide whether you want to call function or not. The function you can call is 'call_explainer'. You can call the function when you think user needs additional explanation about the topic's context. Followings are some examples of specific situation where you will need to call function:
#################### 
1. if the user uses '반말', which is only used between friends, call the function in order to kindly correct the user to use '존댓말' which is used in formal situations. 
2. If user don't follow appropriate sentence structure, call the function in order to provide detailed explanation about the sentence structure.
####################

When calling a function, be sure that your topic argument is the specific topic that needs to be explained more in detail and the context argument is the specific context related to the topic that needs to be explained more in detail. Also be careful not to just call function everytime. You should only call function when you think user needs additional explanation about the topic's context.
"""

storage_context = StorageContext.from_defaults(persist_dir='./index_example1')
index = load_index_from_storage(storage_context)

retriever = VectorIndexRetriever(
  index=index,
  similarity_top_k=3
)

response_synthesizer = get_response_synthesizer(
  response_mode=ResponseMode.COMPACT
)

query_engine = RetrieverQueryEngine(
  retriever=retriever,
  response_synthesizer=response_synthesizer
)

def call_explainer(topic, context):
  query = f"""
  User needs to be provided explanation about {topic}'s {context}. Provide detailed explanation about {topic}'s {context}.
  """
  
  nodes = retriever.retrieve(query)
  response = query_engine.query(query)
  
  return [response, nodes]

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'call_explainer',
            'description': "Provide additional explanation about user's usage of Korean in simulation.",
            'parameters': {
                'type': 'object',
                'properties': {
                    'topic': {
                        'type': 'string',
                        'description': 'Specific topic that needs to be explained more in detail.'
                    },
                    'context': {
                        'type': 'string',
                        'description': 'Specific context related to topic that needs to be explained more in detail.'
                    },
                },
                'required': [
                    'topic',
                    'context'
                ]
            }
        }
    },
]

if "messages" not in st.session_state:
  st.session_state.messages = []

if "initialize" not in st.session_state:
  st.session_state.initialize = False
  
if 'explanations' not in st.session_state:
  st.session_state.explanations = []

def initializer():
  st.session_state.initialize = True

current_learning_level = "User currently learned basic Korean words and phrases.They have also learned about honorofics and basic sentence structure of Korean. They are now practicing their Korean skills by simulating a situation where they are making an order in restaurant."

TALK_ASSISTANT = f"""
User wants to pracitce their Korean skills by simulating a situation where they are making an order in restaurant. Followings are the current learning level of the user:
{current_learning_level}

Get down to their level and help them practice their Korean skills. You should not provide any explanations or translations. Just keep the converstaion going and help them practice on their own.
"""

st.button("Start Simulation", on_click=initializer)

if not st.session_state.initialize:
  st.session_state.messages.append({'role': 'assistant', 'content': '안녕하세요! 주문하시겠어요?'})

for message in st.session_state.messages:
  with st.chat_message(message['role']):
    st.write(message['content'])

if st.session_state.initialize:
  user_response = st.chat_input("You: ")
  if user_response:
    st.session_state.messages.append({'role': 'user', 'content': user_response})
    with st.chat_message('user'):
      st.write(user_response)
    decision = client.chat.completions.create(
      model='gpt-4o',
      messages=[{'role': 'system', 'content': DECIDER}] + [msg for msg in st.session_state.messages],
      tools=tools,
      tool_choice='auto'
    ).choices[0].message.tool_calls
    if decision == None:
      AI_response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': TALK_ASSISTANT}] + [msg for msg in st.session_state.messages],
      ).choices[0].message.content
      
      with st.chat_message('assistant'):
        st.markdown(AI_response)
      st.session_state.messages.append({'role': 'assistant', 'content': AI_response})
    else:
      if decision[0].function.name == 'call_explainer':
        parameters = decision[0].function.arguments
        params_dict = json.loads(parameters)
        topic = params_dict['topic']
        context = params_dict['context']
        explanation = call_explainer(topic=topic, context=context)
        
        AI_response = client.chat.completions.create(
          model='gpt-3.5-turbo',
          messages=[{'role': 'system', 'content': TALK_ASSISTANT}] + [msg for msg in st.session_state.messages],
        ).choices[0].message.content
        
        with st.expander("Check out for detailed explanation."):
          st.write(explanation[0].response)
        st.session_state.explanations.append({'role': 'assistant', 'content': explanation[0].response})
        
        with st.chat_message('assistant'):
          st.markdown(AI_response)
        st.session_state.messages.append({'role': 'assistant', 'content': AI_response})
        with st.chat_message('assistant'):
          for node in explanation[1]:
            st.write(node.text)
            st.write(f"similarity: {node.score}")