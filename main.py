from openai import OpenAI
import anthropic 
from dotenv import load_dotenv
import numpy as np 
import os 
import streamlit as st 
import json 

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

client_o = OpenAI(api_key=OPENAI_API_KEY)
client_a = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

option = st.sidebar.selectbox(
  '학습 선택하기',
  ['한글 익숙해지기', '한국어 익숙해지기']
)
st.header(option)

if option == '한국어 익숙해지기':
  with st.expander('서비스에 대한 설명을 확인하세요.'):
    st.markdown("""
                한국어 문장에 익숙해지기 위한 서비스입니다..!!
                다음과 같은 순서로 활용해주시면 돼요!
                1. 아래의 select box를 이용해서 학습하고자 하는 요소 선택하기.
                2. 학습하고자 하는 요소를 선택했다면, chat_input을 통해서 이용하고자 하는 예시 문장을 영어로 작성하기
                3. 해당 영어 문장을 토대로 해당 요소에 대해 설명하는 응답 확인하기
                4. 이후 다양한 사례들을 보면서 추가적으로 공부하기 
                """)
    
  learnTopic = st.selectbox(
    '어떤 요소를 학습하시고자 하나요?',
    ['존댓말', '문장의 구성', '몰라요', '다른 요소들도 많겠죠', '그건 차차 생각해봅시다..']
  )
  field = st.text_input('어떤 분야의 언어로 학습을 하고 싶으신가요?')
  sentence = st.chat_input('어떤 문장을 기반으로 공부하고 싶은지 입력해주세요.')
  KOREAN_TEACHER_SYSTEM_PROMPT = """
  You are a professional Korean teacher tasked with teaching a user about a specific element of the Korean language. The user will provide the element they want to learn about and an example sentence to illustrate it. Your job is to analyze the sentence, modify it if needed to better showcase the element, and provide a detailed explanation to help the user understand how that element works in Korean.

  The user will provide two inputs:
  <element>
  [ELEMENT]
  </element>
  <sentence>
  [SENTENCE]
  </sentence>

  First, carefully analyze the sentence the user provided. Determine if it is a suitable example to illustrate the Korean language element they want to learn about. If the sentence works well, leave it as is. If it could be improved to better showcase the element, modify it. Put your final example sentence inside <sentence> tags.

  Next, write a detailed explanation of the Korean language element the user wants to learn about. Aim to write at least a paragraph, using the example sentence to illustrate your points. Explain what the element is, how it is used, any associated grammar points, and give additional examples if helpful. The explanation should be encouraging and easy to understand for a learner. Also, your explanations should focus on explaining Korean sentences using English sentences, as English sentences are more familiar to the user, which means that you should actively use comparisons to English sentences to explain the elements of Korean sentences. Put the explanation inside <explanation> tags.

  Your final response should be formatted as a JSON object with following format:
  {
    "sentence": "<your_example_sentence>",
    "explanation": "<your_detailed_explanation_about_user's_desired_learning_element>",
    "examples": "<additional_examples_user_could_use_to_enhance_their_understanding>"
  }
  """
  
  EXAMPLE_PROVIDER = """
  You are a chatbot that helps users learn a specific element of Korean. To do this, you need to input the element of Korean that the user wants to learn, the field that the user wants to use to learn the element, and then provide five example sentences that the user can use to help the user learn the element. 

  Your answer should be in the JSON object with the following format: 
  {
    "Sentence1": "Explanation_About_That_Sentence"},
    "Sentence2": "Explanation_About_That_Sentence"}, ...
  }
  """
  
  if sentence:
    USER_PROMPT = f"""
    User's desired element to learn : {learnTopic},
    User wants to learn that element with the following sentence : "{sentence}"
    """.strip()
    
    EXAMPLE_USER_PROMPT = f"""
    User wants to learn '{learnTopic}' of korean with example sentences realted to '{field}'.
    """
    
    response = client_o.chat.completions.create(
      model='gpt-4o',
      messages=[
        {'role': 'system', 'content': KOREAN_TEACHER_SYSTEM_PROMPT},
        {'role': 'user', 'content': USER_PROMPT}
      ],
      response_format={'type': 'json_object'}
    ).choices[0].message.content 
    
    examplesRelatedToField = client_o.chat.completions.create(
      model='gpt-4o',
      messages=[
        {'role': 'system', 'content': EXAMPLE_PROVIDER},
        {'role': 'user', 'content': EXAMPLE_USER_PROMPT}
      ],
      response_format={'type': 'json_object'}
    ).choices[0].message.content
    
    honorofics_examples = {
  "저는 선생님께 질문이 있습니다.": "This sentence uses the honorific particle '께' to show respect to the teacher when saying 'I have a question for you.'",
  "할아버지, 진지 잡수셨어요?": "This sentence uses the honorific verb '잡수시다' instead of the regular verb '먹다' to respectfully ask the grandfather if he has eaten.",
  "어머니, 어디 가십니까?": "This sentence uses the honorific verb ending '-십니까' to politely ask the mother where she is going.",
  "교수님, 강의 잘 들었습니다.": "This sentence uses the honorific title '교수님' to show respect to the professor and express that the lecture was well-received.",
  "사장님, 회의 시간이 언제입니까?": "This sentence uses the honorific title '사장님' to respectfully ask the company president when the meeting time is.",
  "선배님, 조언 감사드립니다.": "This sentence uses the honorific title '선배님' and the verb '감사드리다' to express gratitude for the advice given by a senior colleague.",
  "아버지, 차 한 잔 드시겠습니까?": "This sentence uses the honorific verb '드시다' to politely offer the father a cup of tea.",
  "김 과장님, 프로젝트 진행 상황이 어떻습니까?": "This sentence uses the honorific title '과장님' and the verb ending '-습니까' to respectfully inquire about the project progress from Manager Kim.",
  "박사님, 연구 결과에 대해 설명해 주시겠습니까?": "This sentence uses the honorific title '박사님' and the verb '주시다' to politely request an explanation about the research results from a doctor.",
  "이모님, 오늘 저녁 식사는 제가 대접하겠습니다.": "This sentence uses the honorific title '이모님' and the verb '대접하다' to express the speaker's intention to treat their aunt to dinner."
    }
    
    response_dict = json.loads(response)
    ex_sentence = response_dict['sentence']
    ex_explanation = response_dict['explanation']
    
    examples_dict = json.loads(examplesRelatedToField)
    
    with st.expander('입력한 문장과 관련된 내용을 확인하세요!'):
      st.markdown(f'Sentence in English : {sentence}')
      st.markdown(f'Korean sentence : {ex_sentence}')
      st.markdown('Explanation to the above sentence.')
      st.markdown(ex_explanation)
      
    with st.expander('입력하신 분야와 관련된 예문들을 확인해보세요!'):
      for key, value in examples_dict:
        st.markdown(f"""
                    {key} 문장에 대한 설명 : {value}
                    """)
    
    with st.expander(f'{learnTopic} 관련 예시 더 많이 확인하기!'):
      if learnTopic == '존댓말':
        for key, value in honorofics_examples.items():
          st.markdown(f"""
                      '{key}' 문장에 대한 설명 : {value}
                      """)