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
  You are a chatbot that helps users learn a specific element of Korean. To do this, you will be given the element of Korean that the user wants to learn and the specific circumstances that the user wants to use to learn that element of Korean. Taking those (desired learning element and circumstatnces) into account, provide five example sentences that the user could use to better understand that element of Korean. Your explanation must be as detailed as possible. Also, when explaining your example sentence, you should focus on utilizing the English equivalent of that Korean word. Users are more familiar with English, so when explaining a specific Korean word, always include the English equivalent.
  
  Your response should consist of a JSON object with the following format:
  {
    "example": {
      "korean_sentence": "[example sentence in Korean]",
      "english_sentence": "[example sentence in English]",
      "explanation": "[explanation of that example]"
    },
    "example": {
      "korean_sentence": "[example sentence in Korean]",
      "english_sentence": "[example sentence in English]",
      "explanation": "[explanation of that example]"
    },...
  }
  
  Followings are some of the examples you should consider:
  {
    "example": {
      "korean_sentence": "저는 선생님께 질문이 있습니다.",
      "english_sentence": "I have a question for you, teacher.",
      "explanation": "This sentence uses the honorific particle '께' (to) to show respect to the teacher when saying 'I have a question for you.' The use of '께' instead of '에게' (to) elevates the formality."
    },
    "example": {
      "korean_sentence": "할아버지, 진지 잡수셨어요?",
      "english_sentence": "Grandfather, have you eaten?",
      "explanation": "This sentence uses the honorific verb '잡수시다' (to eat) instead of the regular verb '먹다' (to eat) to respectfully ask the grandfather if he has eaten. '진지' (meal) is an honorific term for 'meal' or 'food.'"
    }
  """
  
  if sentence:
    with st.spinner('학습 자료가 만들어지고 있어요!'):
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
      
      honorofics_examples = [
    {
      "korean_sentence": "저는 선생님께 질문이 있습니다.",
      "english_sentence": "I have a question for you, teacher.",
      "explanation": "This sentence uses the honorific particle '께' (to) to show respect to the teacher when saying 'I have a question for you.' The use of '께' instead of '에게' (to) elevates the formality."
    },
    {
      "korean_sentence": "할아버지, 진지 잡수셨어요?",
      "english_sentence": "Grandfather, have you eaten?",
      "explanation": "This sentence uses the honorific verb '잡수시다' (to eat) instead of the regular verb '먹다' (to eat) to respectfully ask the grandfather if he has eaten. '진지' (meal) is an honorific term for 'meal' or 'food.'"
    },
    {
      "korean_sentence": "어머니, 어디 가십니까?",
      "english_sentence": "Mother, where are you going?",
      "explanation": "This sentence uses the honorific verb ending '-십니까' (are you going) to politely ask the mother where she is going. The ending '-십니까' (are you going) is more formal than '-가요?' (are you going?)."
    },
    {
      "korean_sentence": "교수님, 강의 잘 들었습니다.",
      "english_sentence": "Professor, I listened to the lecture well.",
      "explanation": "This sentence uses the honorific title '교수님' (professor) to show respect to the professor and express that the lecture was well-received. The title '님' (Mr./Mrs./Ms.) adds formality and respect."
    },
    {
      "korean_sentence": "사장님, 회의 시간이 언제입니까?",
      "english_sentence": "President, when is the meeting time?",
      "explanation": "This sentence uses the honorific title '사장님' (president) to respectfully ask the company president when the meeting time is. The term '사장님' (president) is a respectful way to address the president of a company."
    },
    {
      "korean_sentence": "선배님, 조언 감사드립니다.",
      "english_sentence": "Senior, thank you for your advice.",
      "explanation": "This sentence uses the honorific title '선배님' (senior) and the verb '감사드리다' (to thank) to express gratitude for the advice given by a senior colleague. '감사드리다' (to thank) is a more respectful form of '감사하다' (to thank)."
    },
    {
      "korean_sentence": "아버지, 차 한 잔 드시겠습니까?",
      "english_sentence": "Father, would you like a cup of tea?",
      "explanation": "This sentence uses the honorific verb '드시다' (to eat/drink) to politely offer the father a cup of tea. '드시다' (to eat/drink) is the honorific form of '먹다' (to eat) and '마시다' (to drink)."
    },
    {
      "korean_sentence": "김 과장님, 프로젝트 진행 상황이 어떻습니까?",
      "english_sentence": "Manager Kim, how is the project progress?",
      "explanation": "This sentence uses the honorific title '과장님' (manager) and the verb ending '-습니까' (is it) to respectfully inquire about the project progress from Manager Kim. '과장님' (manager) is a respectful way to address a manager."
    },
    {
      "korean_sentence": "박사님, 연구 결과에 대해 설명해 주시겠습니까?",
      "english_sentence": "Doctor, could you explain the research results?",
      "explanation": "This sentence uses the honorific title '박사님' (doctor) and the verb '주시다' (to give) to politely request an explanation about the research results from a doctor. '주시다' (to give) is the honorific form of '주다' (to give)."
    },
    {
      "korean_sentence": "이모님, 오늘 저녁 식사는 제가 대접하겠습니다.",
      "english_sentence": "Aunt, I will treat you to dinner tonight.",
      "explanation": "This sentence uses the honorific title '이모님' (aunt) and the verb '대접하다' (to treat) to express the speaker's intention to treat their aunt to dinner. '이모님' (aunt) is a respectful way to address one's aunt."
    }
  ]

      
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
        for key, value in examples_dict.items():
          st.markdown(f"""
                      {key} 문장에 대한 설명 : {value}
                      """)
      
      with st.expander(f'{learnTopic} 관련 예시 더 많이 확인하기!'):
        if learnTopic == '존댓말':
          for key, value in honorofics_examples.items():
            st.markdown(f"""
                        '{key}' 문장에 대한 설명 : {value}
                        """)