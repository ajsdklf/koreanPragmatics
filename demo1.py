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

def load_css(file_name):
  with open(file_name) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("styles.css")

#### PROMPTS

CONSONANT_SCRIPT = """
  ---

  Welcome to learning the Korean consonants! There are 19 in total, each with a unique sound. Let's dive in and discover how they connect to English.

  First up, the basic consonants:

  1. **ㄱ (g/k)**: This sounds like 'g' in 'go' at the beginning of a word, but 'k' in the middle or end, like 'like'.
  2. **ㄴ (n)**: This is an 'n' sound, like in 'no' or 'sun'.
  3. **ㄷ (d/t)**: This sounds like 'd' in 'dog' at the beginning of a word, but 't' in the middle or end, like 'bat'.
  4. **ㄹ (r/l)**: This is a combination of 'r' and 'l'. At the start of a syllable, it sounds like 'r' in 'run'. At the end of a syllable, it sounds like 'l' in 'real'.
  5. **ㅁ (m)**: This is an 'm' sound, like in 'mom' or 'sum'.
  6. **ㅂ (b/p)**: This sounds like 'b' in 'bat' at the beginning of a word, but 'p' in the middle or end, like 'cup'.
  7. **ㅅ (s)**: This is an 's' sound, like in 'snake' or 'bus'. It can also sound like 'sh' before 'i'.
  8. **ㅇ (ng)**: This is silent at the beginning of a syllable but sounds like 'ng' in 'song' at the end.
  9. **ㅈ (j)**: This is a 'j' sound, like in 'joke' or 'edge'.
  10. **ㅊ (ch)**: This is a 'ch' sound, like in 'church' or 'match'.
  11. **ㅋ (k)**: This is a strong 'k' sound, like in 'kite' or 'skate'.
  12. **ㅌ (t)**: This is a strong 't' sound, like in 'top' or 'hat'.
  13. **ㅍ (p)**: This is a strong 'p' sound, like in 'pen' or 'cap'.
  14. **ㅎ (h)**: This is an 'h' sound, like in 'hat' or 'hope'.

  Next, we have the double consonants which are tense versions of the basic ones:

  1. **ㄲ (kk)**: This is a tense 'k', similar to 'scar'.
  2. **ㄸ (tt)**: This is a tense 't', similar to 'start'.
  3. **ㅃ (pp)**: This is a tense 'p', similar to 'spa'.
  4. **ㅆ (ss)**: This is a tense 's', similar to 'sang'.
  5. **ㅉ (jj)**: This is a tense 'j', similar to 'judge'.

  Lastly, we have the aspirated consonants:

  1. **ㄱㅎ (kh)**: This is an aspirated 'k', similar to 'key'.
  2. **ㄷㅎ (th)**: This is an aspirated 't', similar to 'take'.
  3. **ㅂㅎ (ph)**: This is an aspirated 'p', similar to 'pie'.

  Understanding and mastering these consonants is key to speaking and reading Korean fluently. Practice makes perfect, so try pronouncing these consonants by finding similar sounds in English words. Soon, you'll be able to master the Korean consonant system with ease.

  ---
"""


VOWELS_SCRIPT = """
  ---

  Welcome to learning the Korean vowels! There are 21 in total, each with a unique sound. Let's dive in and discover how they connect to English.

  First up, the basic vowels:

  1. **ㅏ (ah)**: This makes an 'ah' sound, like in 'father'. Think of how you say "spa" in English.
  2. **ㅓ (uh)**: This is an 'uh' sound, similar to 'uh-oh'. Imagine the 'o' sound in 'bought'.
  3. **ㅗ (oh)**: This is 'oh' like in 'go'. Think of saying "no" in English.
  4. **ㅜ (oo)**: This says 'oo' as in 'boo'. It's the same sound as 'food'.
  5. **ㅡ (eu)**: This makes an 'eu' sound, like the end of 'grandeur'. It's a bit like a muted 'u' in 'put', but the tongue position is more centralized.
  6. **ㅣ (ee)**: This says 'ee' like in 'see'. It's the same sound as 'tree'.

  Next, we have the combined vowels:

  1. **ㅐ (ae)**: This makes an 'ae' sound, like in 'cat'. It's a blend of 'ah' and 'eh'.
  2. **ㅔ (e)**: This is an 'e' sound, like in 'bed'. It's a straightforward 'eh'.

  Now let's combine some to make diphthongs!

  1. **ㅑ (ya)**: This is 'ya' like 'yada yada'. It's like 'y' + 'ah'.
  2. **ㅒ (yae)**: This makes a 'yae' sound, similar to 'yeah'. It's like 'y' + 'ae'.
  3. **ㅕ (yeo)**: This makes a 'yuh' sound - think 'young'. It's like 'y' + 'uh'.
  4. **ㅖ (ye)**: This is 'ye' as in 'yes'. It's like 'y' + 'eh'.
  5. **ㅛ (yo)**: This is simply 'yo' as in 'yo-yo'. It's like 'y' + 'oh'.
  6. **ㅠ (yu)**: This says 'yu' like 'you'. It's like 'y' + 'oo'.

  We also have more complex diphthongs:

  1. **ㅘ (wa)**: This is 'wa' like 'wand'. It's like 'w' + 'ah'.
  2. **ㅙ (wae)**: This adds a bit more 'w' sound, similar to 'way'. It's like 'w' + 'ae'.
  3. **ㅚ (oe)**: This makes a sound similar to 'we' in 'wet'. It's like 'w' + 'eh'.
  4. **ㅝ (wo)**: This is 'wuh' as in 'wonder'. It's like 'w' + 'uh'.
  5. **ㅞ (we)**: This follows suit, similar to 'wet'. It's like 'w' + 'eh'.
  6. **ㅟ (wi)**: This is 'wi' like in 'week'. It's like 'w' + 'ee'.

  Finally, we have a unique vowel:

  1. **ㅢ (ui)**: This is unique, blending 'eu' and 'ee' sounds. It's like saying 'eui' in 'seize'.

  Remember, practice makes perfect! Try pronouncing these vowels by finding similar sounds in English words, and soon you'll be able to master the Korean vowel system with ease.

  ---
"""

LETTER_FORMATION_SCRIPT = """
---

Welcome to understanding how Korean consonants and vowels combine to form words! This is a fundamental aspect of learning Korean, and we'll compare it to English to make it easier to grasp. We'll use the names of famous K-pop idols to help illustrate these principles.

### Basic Principle

In Korean, each block (or character) represents a syllable. Each syllable is made up of at least one consonant and one vowel. These blocks are formed by combining consonants (자음) and vowels (모음) in specific ways.

### Structure of Korean Syllables

A typical Korean syllable block follows these patterns:

1. **Consonant + Vowel (CV)**: The simplest form.
2. **Consonant + Vowel + Consonant (CVC)**: Adding a final consonant.
3. **Consonant + Vowel + Vowel (CVV)**: A form with diphthongs.

### Comparison with English

In English, words are formed by placing letters linearly, like "cat" or "dog." In Korean, however, the letters are combined into blocks. Let's explore this with examples:

### Example 1: Consonant + Vowel (CV)

**Name: 수호 (Suho)** - EXO

- **ㅅ (s) + ㅜ (u) = 수 (su)**: The consonant ㅅ and vowel ㅜ combine to form 수.
- **ㅎ (h) + ㅗ (o) = 호 (ho)**: The consonant ㅎ and vowel ㅗ combine to form 호.

Together, these syllables form the name **수호** (Suho).

### Example 2: Consonant + Vowel + Consonant (CVC)

**Name: 정국 (Jungkook)** - BTS

1. **정 (Jeong)**
   - **ㅈ (j) + ㅓ (eo) = 저 (jeo)**: The consonant ㅈ and vowel ㅓ combine to form 저.
   - **ㅇ (ng)**: Adding the final consonant ㅇ creates 정.

2. **국 (Guk)**
   - **ㄱ (g) + ㅜ (u) = 구 (gu)**: The consonant ㄱ and vowel ㅜ combine to form 구.
   - **ㄱ (k)**: Adding the final consonant ㄱ creates 국.

Together, these syllables form the name **정국** (Jungkook).

### Example 3: Consonant + Vowel + Vowel (CVV)

**Name: 화사 (Hwasa)** - MAMAMOO

1. **화 (Hwa)**
   - **ㅎ (h) + ㅘ (wa) = 화 (hwa)**: The consonant ㅎ and vowel ㅘ combine to form 화. Here, ㅘ is a diphthong composed of ㅗ (o) + ㅏ (a).

2. **사 (Sa)**
   - **ㅅ (s) + ㅏ (a) = 사 (sa)**: The consonant ㅅ and vowel ㅏ combine to form 사.

Together, these syllables form the name **화사** (Hwasa).

### Example 4: Consonant + Vowel (CV)

**Name: 로제 (Rosé)** - BLACKPINK

1. **로 (Ro)**
   - **ㄹ (r/l) + ㅗ (o) = 로 (ro)**: The consonant ㄹ and vowel ㅗ combine to form 로.

2. **제 (Je)**
   - **ㅈ (j) + ㅔ (e) = 제 (je)**: The consonant ㅈ and vowel ㅔ combine to form 제.

Together, these syllables form the name **로제** (Rosé).

### Example 5: Consonant + Vowel (CV)

**Name: 아이유 (IU)**

1. **아 (A)**
   - **ㅇ (silent) + ㅏ (a) = 아 (a)**: The silent consonant ㅇ and vowel ㅏ combine to form 아.

2. **이 (I)**
   - **ㅇ (silent) + ㅣ (i) = 이 (i)**: The silent consonant ㅇ and vowel ㅣ combine to form 이.

3. **유 (Yu)**
   - **ㅇ (silent) + ㅠ (yu) = 유 (yu)**: The silent consonant ㅇ and vowel ㅠ combine to form 유.

Together, these syllables form the name **아이유** (IU).

### Summary

Korean words are formed by combining consonants and vowels into syllabic blocks. Each block represents a syllable, and syllables are combined to form words. This block system is unique to Korean and allows for a compact and organized way to write.

By practicing how consonants and vowels come together to form these blocks, you'll get a better understanding of how to read and write Korean words. Keep practicing with different names and words, and soon you'll master the art of Korean syllabic blocks!

  ---
"""
NAME_EXPLAINER = """
The user has studied the consonant and vowel system of Hangul, and will see how their name is written in Hangul, and will use that to learn how Korean letters are formed. When you receive the user's name as input, convert it to Hangul first. For example, if the user's name is Evangelia, you should convert it to [이뱅글리아] to account for the American English pronunciation. Then, explain in detail how each letter of the user's name is formed, so that the user can understand how the letters are formed in Hangeul. Your response should be based on the following format:
###
[Answer Format]
Name in english : [User's name] \n
Name in Korean : [User's name in Korean] \n
Explanation : [Explanation of user's name in Korean]
###
"""

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

Your answer needs to be in English.
"""

HONOROFIC_EXAMPLE_PROVIDER = """
You are a chatbot that helps users learn a honorofics of Korean. Your task is to provide good example sentences and great explanation that user could use to study Korean Honorofics. When providing examples and explanation, you should follow the given rules.
---
[Rules]
1. You will be given the specific circumstances that user wants to use to learn honorofics of Korean. For example, user might want to learn honorofics used in the circumstance of making an order in cafeteria. Your examples should be generated based on the circumstances given by user. 
2. You will also be given specified element of honorifcs user wants to focus on. For example, a user might indicate that they would like to focus on the conceptual elements of respectful behaviour, or the different types of respectful behaviour that vary depending on the situation. When generating explanation, element that user wants to foucs on must be taken into account. 
3. Your explanation should be focused on utilizing English equivalent of Korean. User's are native English speaker and much more familiar with English than Korean. Therefore, when explaining a specific Korean word, always include the English equivalent.
4. Your explanation must be as detailed and kind. It should be written so kindly that even middle school student could read your explanation and understand things you are explaining.
---

Your response should consist of a JSON object with the following format:
{
"examples": [
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },...
]
}

Followings are some of the examples you should refer to:
"example": [
  {
  "korean_sentence": "저는 선생님께 질문이 있습니다.",
  "english_sentence": "I have a question for you, teacher.",
  "explanation": "This sentence uses the honorific particle '께' (to) to show respect to the teacher when saying 'I have a question for you.' The use of '께' instead of '에게' (to) elevates the formality."
  },
  {
  "korean_sentence": "할아버지, 진지 잡수셨어요?",
  "english_sentence": "Grandfather, have you eaten?",
  "explanation": "This sentence uses the honorific verb '잡수시다' (to eat) instead of the regular verb '먹다' (to eat) to respectfully ask the grandfather if he has eaten. '진지' (meal) is an honorific term for 'meal' or 'food.'"
  },...
]
}
"""

PRONOUNCIATION_EXAMPLE_PROVIDER = """
You are a chatbot that helps users learn a pronounciations of Korean. Your task is to provide good example sentences and great explanation that user could use to study Korean pronounciations of Korean. When providing examples and explanation, you should follow the given rules.
---
[Rules]
1. You will be given the specific circumstances that user wants to use to learn pronounciations of Korean. Your examples should be generated based on the circumstances given by user. 
2. You will also be given specified element of pronounciations user wants to focus on. For example, a user might indicate that they want to focus on intonation and stress, or that they want to focus on diphthongs. When generating explanation, element that user wants to foucs on must be taken into account. 
3. Your explanation should be focused on utilizing English equivalent of Korean. User's are native English speaker and much more familiar with English than Korean. Therefore, when explaining a specific Korean word, always include the English equivalent.
4. Your explanation must be as detailed and kind. It should be written so kindly that even middle school student could read your explanation and understand things you are explaining.
5. Your explanation should always include the pronunciation of the Korean sentence. For example, an explanation of the sentence “나 오늘 너무 행복해" should include the pronunciation: "na oenul neomoo haengbokhae".
---

Your response should consist of a JSON object with the following format:
{
"examples": [
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },...
]
}

Followings are some of the examples you should refer to:
{
"example": [
  {
  "korean_sentence": "저는 매일 아침 운동을 합니다.",
  "english_sentence": "I exercise every morning.",
  "explanation": "The word '운동' (exercise) is pronounced as [un-dong], similar to 'oon-dong' in English. Here, 'ㅇ' at the beginning is silent, and 'ㅜ' makes an 'oo' sound as in 'moon'. '동' sounds like 'dong' in 'gong'."
  },
  {
  "korean_sentence": "그는 한국어를 공부합니다.",
  "english_sentence": "He studies Korean.",
  "explanation": "In '한국어' (Korean), '한' is pronounced [han], similar to 'han' in 'hand'. '국' is pronounced [guk], similar to 'gook' in 'cook'. The '어' sounds like 'uh'."
  },...
]
}
"""

SENTENCE_STRUCTURE_EXAMPLE_PROVIDER = """
You are a chatbot that helps users learn sentence structure of Korean. Your task is to provide good example sentences and great explanation that user could use to study Korean sentence structure. When providing examples and explanation, you should follow the given rules.
---
[Rules]
1. You will be given the specific circumstances that user wants to use to learn sentence structure of Korean. For example, user might want to learn sentence structure with sentences used in the circumstance of making an order in cafeteria. Your examples should be generated based on the circumstances given by user. 
2. You will also be given specified element of sentence structure user wants to focus on. For example, a user can indicate that they want to focus on one of the following elements: sentence structure, postposition, adverbs, and vocabulary. When generating explanation, element that user wants to foucs on must be taken into account. 
3. Your explanation should be focused on utilizing English equivalent of Korean. User's are native English speaker and much more familiar with English than Korean. Therefore, when explaining a specific Korean word, always include the English equivalent.
4. Your explanation must be as detailed and kind. It should be written so kindly that even middle school student could read your explanation and understand things you are explaining.
---

Your response should consist of a JSON object with the following format:
{
"examples": [
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },
  {
    "korean_sentence": "[example sentence in Korean]",
    "english_sentence": "[example sentence in English]",
    "explanation": "[explanation of that example]"
  },...
]
}

Followings are some of the examples you should refer to:
{
"example": [
  {
    "korean_sentence": "저는 아침에 운동을 합니다.",
    "english_sentence": "I exercise in the morning.",
    "explanation": "This sentence follows the Subject-Object-Verb (SOV) structure commonly used in Korean. '저는' (I) is the subject, '아침에' (in the morning) is a time expression, and '운동을 합니다' (exercise) is the verb phrase."
    },
    {
    "korean_sentence": "그녀는 한국어를 공부합니다.",
    "english_sentence": "She studies Korean.",
    "explanation": "In this SOV structure sentence, '그녀는' (she) is the subject, '한국어를' (Korean) is the object, and '공부합니다' (studies) is the verb."
  },...
]
}
"""


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

sentence_structure_exmaples = [
{
"korean_sentence": "저는 아침에 운동을 합니다.",
"english_sentence": "I exercise in the morning.",
"explanation": "This sentence follows the Subject-Object-Verb (SOV) structure commonly used in Korean. '저는' (I) is the subject, '아침에' (in the morning) is a time expression, and '운동을 합니다' (exercise) is the verb phrase."
},
{
"korean_sentence": "그녀는 한국어를 공부합니다.",
"english_sentence": "She studies Korean.",
"explanation": "In this SOV structure sentence, '그녀는' (she) is the subject, '한국어를' (Korean) is the object, and '공부합니다' (studies) is the verb."
},
{
"korean_sentence": "우리는 주말에 영화를 봅니다.",
"english_sentence": "We watch a movie on the weekend.",
"explanation": "The sentence follows the SOV structure: '우리는' (we) is the subject, '주말에' (on the weekend) is a time expression, and '영화를 봅니다' (watch a movie) is the verb phrase."
},
{
"korean_sentence": "나는 저녁을 먹고 싶습니다.",
"english_sentence": "I want to eat dinner.",
"explanation": "This SOV structure sentence includes a verb phrase '먹고 싶습니다' (want to eat) after the object '저녁을' (dinner), with '나는' (I) as the subject."
},
{
"korean_sentence": "그들은 매일 학교에 갑니다.",
"english_sentence": "They go to school every day.",
"explanation": "'그들은' (they) is the subject, '매일' (every day) is a time expression, '학교에' (to school) is a location, and '갑니다' (go) is the verb."
},
{
"korean_sentence": "선생님은 학생들을 가르칩니다.",
"english_sentence": "The teacher teaches the students.",
"explanation": "'선생님은' (the teacher) is the subject, '학생들을' (the students) is the object, and '가르칩니다' (teaches) is the verb, following the SOV structure."
},
{
"korean_sentence": "우리는 서울에서 만났습니다.",
"english_sentence": "We met in Seoul.",
"explanation": "The sentence follows the SOV structure: '우리는' (we) is the subject, '서울에서' (in Seoul) is a location expression, and '만났습니다' (met) is the verb."
},
{
"korean_sentence": "나는 책을 읽고 있습니다.",
"english_sentence": "I am reading a book.",
"explanation": "'나는' (I) is the subject, '책을' (a book) is the object, and '읽고 있습니다' (am reading) is the verb phrase, following the SOV structure."
},
{
"korean_sentence": "그는 요리를 잘합니다.",
"english_sentence": "He cooks well.",
"explanation": "'그는' (he) is the subject, '요리를' (cooking) is the object, and '잘합니다' (cooks well) is the verb phrase, following the SOV structure."
},
{
"korean_sentence": "저는 친구와 함께 여행을 갑니다.",
"english_sentence": "I go on a trip with a friend.",
"explanation": "'저는' (I) is the subject, '친구와 함께' (with a friend) is a prepositional phrase, '여행을' (a trip) is the object, and '갑니다' (go) is the verb, following the SOV structure."
}
]

pronunciation_examples = [
{
"korean_sentence": "저는 매일 아침 운동을 합니다.",
"english_sentence": "I exercise every morning.",
"explanation": "The word '운동' (exercise) is pronounced as [un-dong], similar to 'oon-dong' in English. Here, 'ㅇ' at the beginning is silent, and 'ㅜ' makes an 'oo' sound as in 'moon'. '동' sounds like 'dong' in 'gong'."
},
{
"korean_sentence": "그는 한국어를 공부합니다.",
"english_sentence": "He studies Korean.",
"explanation": "In '한국어' (Korean), '한' is pronounced [han], similar to 'han' in 'hand'. '국' is pronounced [guk], similar to 'gook' in 'cook'. The '어' sounds like 'uh'."
},
{
"korean_sentence": "우리는 서울에서 만났습니다.",
"english_sentence": "We met in Seoul.",
"explanation": "The word '서울' (Seoul) contains the diphthong 'ㅜ', pronounced as [seo-ul], which sounds like 'suh-ool'. Ensure smooth transition between the vowels 'ㅓ' and 'ㅜ', similar to saying 'so-ool'."
},
{
"korean_sentence": "나는 저녁을 먹고 싶습니다.",
"english_sentence": "I want to eat dinner.",
"explanation": "When '저녁을' (dinner) and '먹고' (eat) are pronounced together, '저녁을' ends with 'ㄹ', which smoothly links to '먹고', resulting in [jeo-nyeok-eul-meok-go]. '저녁' sounds like 'jeo-nyuhk', similar to 'jaw-nyuk'. '먹고' sounds like 'muhk-go', similar to 'muck-go'."
},
{
"korean_sentence": "그녀는 한국어를 잘합니다.",
"english_sentence": "She speaks Korean well.",
"explanation": "The intonation should rise slightly at the end of '잘합니다' (does well) to convey the affirmative statement. '잘합니다' is pronounced [jal-ham-ni-da], similar to 'jal-hahm-nee-da', where '잘' is like 'jal' in 'jolly'."
},
{
"korean_sentence": "우리는 주말에 영화를 봅니다.",
"english_sentence": "We watch a movie on the weekend.",
"explanation": "In '영화를' (movie), the nasal consonant 'ㅇ' should be clearly pronounced. '영화' is pronounced [yeong-hwa], similar to 'yong-hwah'. The 'ㅇ' makes a nasal sound similar to 'ng' in 'song'."
},
{
"korean_sentence": "나는 책을 읽고 있습니다.",
"english_sentence": "I am reading a book.",
"explanation": "In '책을' (book), the consonant 'ㄱ' is slightly tensed, pronounced as [chaek-eul], differentiating it from a softer sound. '책' sounds like 'chaek', similar to 'check', and '읽고' sounds like 'ilk-go', where '읽' is similar to 'illk'."
},
{
"korean_sentence": "선생님은 학생들을 가르칩니다.",
"english_sentence": "The teacher teaches the students.",
"explanation": "In '학생들' (students), the 'ㄹ' in '들' is pronounced as a liquid 'r/l' sound, resulting in [hak-saeng-deul]. '학생' sounds like 'hak-saeng', similar to 'hack-sang', and '들' sounds like 'deul', similar to 'dull'."
},
{
"korean_sentence": "그들은 매일 학교에 갑니다.",
"english_sentence": "They go to school every day.",
"explanation": "In '학교' (school), the vowel 'ㅗ' in '교' is reduced slightly in speech, resulting in [hak-gyo]. '학교' sounds like 'hak-gyo', similar to 'hack-gyo'."
},
{
"korean_sentence": "저는 친구와 함께 여행을 갑니다.",
"english_sentence": "I go on a trip with a friend.",
"explanation": "In '친구와' (with a friend), the 'ㄴ' in '친' and 'ㄱ' in '구' are assimilated smoothly, resulting in [chin-gu-wa]. '친구' sounds like 'chin-gu', similar to 'chin-goo', and '함께' sounds like 'ham-kke', similar to 'hahm-keh'."
}
]

WORD_EXTRACTOR = """
You are an assistant who helps native English speakers learn Korean words. As input, you will be given a Korean sentence. From the sentence, you will extract Korean words and provide a detailed description of each word. When extracting words and providing explanation you should keep in mind the following rules:
---
[Rules]
1. Do not extract every word. You should extract three words per sentence and criteria for selecting words should be how important each word is when learning Korean.
2. the meaning of the word
3. the pronunciation of the word
4. explanation of the word: The explanation of the word should be presented in English, considering that the user is an English-speaking foreigner. For example, when explaining the word "쓰다", you should provide a detailed explanation using the English word "write", which has the same meaning.
---

Another important rule is that you should never use markdown techniques. Only markdowns that allowed are bold, list, bullet-points. Never use headers, code and other markdown techniques.

Your answer should look something like the following example:
===
Words used in the example sentence : 
Word1
날씨 (nal-ssi)

Meaning: Weather

Pronunciation: [nal-ssi]

Explanation: The word "날씨" refers to the state of the atmosphere at a particular place and time, including factors like temperature, humidity, wind, and precipitation. In this sentence, "날씨" is used to comment on the weather being nice.

Word2
정말 (jeong-mal)

Meaning: Really, truly

Pronunciation: [jeong-mal]

Explanation: "정말" is used to emphasize the truth or intensity of something. In the sentence, it emphasizes just how good the weather is, equivalent to saying "really" in English.

Word3
지내다 (ji-nae-da)

Meaning: To spend time, to live
Pronunciation: [ji-nae-da]
Explanation: "지내다" is a verb that means to spend time or to live in a certain way. In the context of the question "어떻게 지내셨어요?", it is asking how someone has been doing or how they have spent their time recently.
===
"""


#########################################################################

client_o = OpenAI(api_key=OPENAI_API_KEY)
client_a = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

option = st.sidebar.selectbox(
  '학습 선택하기',
  ['한글 익숙해지기', '한국어 익숙해지기']
)
st.header('DEMO1: FIRST TRY')

if option == '한글 익숙해지기':
  learnOption = st.selectbox(
    '어떤 공부를 하고 싶으세요?',
    ['한국 알파벳 공부하기', '글자 형성 원리 공부하기_이론', '글자 형성 원리 공부하기_원하는 이름 활용']
  )
  
  if learnOption == '한국 알파벳 공부하기': 
    with st.expander('자음 체계 공부를 시작해보세요!'):
      st.markdown(CONSONANT_SCRIPT)
    with st.expander('모음 체계 공부를 시작해보세요!'):
      st.markdown(VOWELS_SCRIPT)
  
  if learnOption == '글자 형성 원리 공부하기_이론':
    with st.expander('학습을 시작해보세요!'):
      st.markdown(LETTER_FORMATION_SCRIPT)
  
  if learnOption == '글자 형성 원리 공부하기_원하는 이름 활용':
    name = st.text_input('학습하는데 이용하고 싶은 이름을 영어로 입력해주세요!')
    NAME_INPUT = f"User's name is {name}."
    if name:
      with st.spinner('학습 자료 생성 중입니다!'):
        name_explanation = client_o.chat.completions.create(
          model='gpt-4o',
          messages=[
            {'role': 'system', 'content': NAME_EXPLAINER},
            {'role': 'user', 'content': NAME_INPUT}
          ]
        ).choices[0].message.content
        with st.expander('그 이름이 한글로 어떻게 되는지 확인해보세요!'):
          st.markdown(name_explanation)

if option == '한국어 익숙해지기':
  with st.expander('서비스에 대한 설명을 확인하세요.'):
    st.markdown("""
                한국어 문장에 익숙해지기 위한 기능입니다..!!
                다음과 같은 순서로 활용해주시면 돼요!
                1. 아래의 select box를 이용해서 학습하고자 하는 요소 선택하기.
                2. 학습하고자 하는 요소를 선택했다면, chat_input을 통해서 이용하고자 하는 예시 문장을 영어로 작성하고 text_input에 본인이 한국어를 학습하는데 이용하고 싶은 예문의 상황을 입력해주세요!
                3. 해당 영어 문장을 토대로 해당 요소에 대해 설명하는 응답 확인해주세요!
                4. 이후 다양한 사례들을 보면서 추가적으로 공부하시면 됩니다!
                """)
    
  learnTopic = st.selectbox(
    '어떤 요소를 학습하시고자 하나요?',
    ['존댓말', '문장의 구성', '발음']
  )
  if learnTopic == '존댓말':
    learningElement = st.selectbox(
      '존댓말의 어떤 부분을 집중적으로 학습하고 싶으신가요?',
      ['존댓말의 개념적 요소', '상황에 따라 달라지는 다양한 존댓말', '존댓말 관련 문화적 맥락']
    )
  if learnTopic == '문장의 구성':
    learningElement = st.selectbox(
      '문장 구성의 어떤 부분을 집중적으로 학습하고 싶으신가요?',
      ['문장 구조', '조사', '동사 및 형용사의 활용', '부사 및 어휘']
    )
  if learnTopic == '발음':
    learningElement = st.selectbox(
      '발음의 어떤 부분을 집중적으로 학습하고 싶으신가요?',
      ['자음과 모음의 발음', '억양과 강세', '받침 발음', '음운의 변동']
    )
  circumstance = st.text_input('어떤 상황을 기반으로 학습을 하고 싶으신가요? ex. Making an order in restaurant. Talking to bias in fan-meeting etc.')
  sentence = st.chat_input('어떤 문장을 기반으로 공부하고 싶은지 입력해주세요. 최대한 구체적으로 적어주세요!')
  
  if sentence:
    with st.spinner('학습 자료가 만들어지고 있어요!'):
      USER_PROMPT = f"""
      User's desired element to learn : {learnTopic},
      User wants to learn that element with the following sentence : "{sentence}"
      """.strip()
      
      EXAMPLE_USER_PROMPT = f"""
      User wants to learn '{learnTopic}' of korean with example sentences realted to '{circumstance}'. User especailly want to foucs on {learningElement} of {learnTopic} from the examples you provide.
      """
      
      if learnTopic == "존댓말":
        EXAMPLE_PROVIDER = HONOROFIC_EXAMPLE_PROVIDER
      elif learnTopic == "문장의 구성":
        EXAMPLE_PROVIDER = SENTENCE_STRUCTURE_EXAMPLE_PROVIDER
      elif learnTopic == "발음":
        EXAMPLE_PROVIDER = PRONOUNCIATION_EXAMPLE_PROVIDER
      else:
        EXAMPLE_PROVIDER = None
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
        for example in examples_dict['examples']:
          words = client_o.chat.completions.create(
            model='gpt-4o',
            messages=[
              {'role': 'system', 'content': WORD_EXTRACTOR},
              {'role': 'user', 'content': example['korean_sentence']}
            ]
          ).choices[0].message.content
          st.markdown(f"""
Korean Sentence : {example['korean_sentence']} \n
English Sentence : {example['english_sentence']} \n
Explanation : {example['explanation']} \n

-----------------------------------------------

{words} \n
""")
      
      with st.expander(f'{learnTopic} 관련 예시 더 많이 확인하기!'):
        if learnTopic == '존댓말':
          for example in honorofics_examples:
            st.markdown(f"""
                      -----------------------------------------------
                      Korean Sentence : {example['korean_sentence']} \n 
                      English Sentence : {example['english_sentence']} \n 
                      Explanation : {example['explanation']} \n 
                      -----------------------------------------------
                        """)
        if learnTopic == '문장의 구성':
          for example in sentence_structure_exmaples:
            st.markdown(f"""
                      -----------------------------------------------
                      Korean Sentence : {example['korean_sentence']} \n 
                      English Sentence : {example['english_sentence']} \n 
                      Explanation : {example['explanation']} \n 
                      -----------------------------------------------
                      """)
        
        if learnTopic == '발음':
          for example in pronunciation_examples:
            st.markdown(f"""
                      -----------------------------------------------
                      Korean Sentence : {example['korean_sentence']} \n 
                      English Sentence : {example['english_sentence']} \n 
                      Explanation : {example['explanation']} \n 
                      -----------------------------------------------
                      """)
            