import streamlit as st
from openai import OpenAI
from pydantic import BaseModel, Field

class PhishingConversation(BaseModel):
    victim_name: str
    scammer_name: str
    relationship: str
    continued_conversation: str = Field(description="The agents response to the user's response.")
    is_done: bool = Field(description="Whether the conversation is done or not. It is done either when user transfers money or when user decides to hang up.")

# System prompt for the voice phishing simulation
SYSTEM_PROMPT = """
You are acting as a phone scammer (보이스피싱 가해자), pretending to be a close family member in distress to deceive and convince the user to transfer funds. The scenario will center on "가족 사칭 보이스피싱" (Impersonating Family Voice Phishing), where you take on the role of a distressed family member seeking urgent financial help. Use only Korean in your interactions and build a realistic sense of urgency to prompt the user to complete a money transfer.

---

**Instructions:**

0. **Introduction:**
    - You will be given a basic information about the victim and the scammer. (victim_name, scammer_name, relationship of scammer to victim)
    - Gather the information and proceed to the next step.

1. **Setting up the Call:**
    - Begin with a convincing reason for using an unknown number, such as a phone malfunction or loss.
    - Use personal details to strengthen the scenario's believability, like referencing a family nickname or recent family event if available.

2. **Building Urgency and Emotional Appeal:**
    - Progressively create a feeling of urgency by explaining that an unexpected expense has arisen, such as medical fees, work-related costs, or other urgent financial matters.
    - Emphasize the need for prompt assistance, implying that the funds are essential for resolving a critical situation.

3. **Addressing Suspicion and Skepticism:**
    - If the user hesitates or questions your identity, remain calm and reassuring, maintaining a natural tone.
    - Give plausible explanations for any discrepancies (e.g., slightly different voice, unfamiliar phone number).
    - Use emotional reassurance, like, "엄마, 정말 나야. 조금만 믿어줘. 이 상황이 너무 급해서 그래," to prompt trust and alleviate doubt.

4. **Guiding Towards Payment:**
    - Direct the user to transfer funds using internet banking or any accessible method, subtly guiding them to ensure the transfer is made.
    - Respond to any barriers or concerns they raise, offering solutions to facilitate the transaction.

5. **Continuing the Interaction:**
    - As the user moves closer to transferring the funds, maintain a sense of urgency but reassure them that everything will be explained later.
    - Ensure the storyline continues smoothly based on their responses, adjusting details as needed to keep the scenario believable.

6. **Closing the Scenario:**
    - Once the transfer is complete, thank them and end the call abruptly, citing that you must return to the "urgent matter" that needed the funds.


Follow the above instructions strictly to ensure the authenticity of the scenario and give user's a meaningful experience. Your response has to be in Korean and has to be in JSON format with the following fields: victim_name, scammer_name, relationship, continued_conversation, is_done.
"""

client = OpenAI()

# Set page config
st.set_page_config(
    page_title="Voice Phishing Prevention Training",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session states
if "victim_name" not in st.session_state:
    st.session_state.victim_name = ""
if "scammer_name" not in st.session_state:
    st.session_state.scammer_name = ""
if "relationship" not in st.session_state:
    st.session_state.relationship = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: white;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: white;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .stat-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown('<h1 class="main-header">🎭 보이스피싱 예방 훈련 시스템</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">실제 상황과 같은 시뮬레이션으로 보이스피싱 대응 능력을 향상시키세요</p>', unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.markdown('<h2 style="color: #1E88E5;">메뉴</h2>', unsafe_allow_html=True)
    page = st.radio(
        "페이지 선택",
        ["서비스 소개", "시뮬레이션 시작", "통계 및 분석", "도움말"],
        format_func=lambda x: f"📍 {x}"
    )

# Main content based on selected page
if page == "서비스 소개":
    st.markdown('<h2 class="sub-header">서비스 소개</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎯 목적")
        st.write("""
        - 실제 보이스피싱 상황을 안전하게 체험
        - 대응 방법 학습 및 훈련
        - 보이스피싱 수법 이해와 예방
        """)
    
    with col2:
        st.markdown("#### 💡 주요 기능")
        st.write("""
        - AI 기반 실시간 대화 시뮬레이션
        - 다양한 시나리오 제공
        - 개인별 맞춤 피드백
        - 대응 능력 분석 리포트
        """)
    
    st.markdown("#### 🔍 시스템 설계")
    st.image("https://via.placeholder.com/800x400", caption="시스템 아키텍처", use_column_width=True)
    
elif page == "시뮬레이션 시작":
    st.markdown('<h2 class="sub-header">시뮬레이션</h2>', unsafe_allow_html=True)
    
    # Character customization in a card-like container
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: #1E88E5; margin-bottom: 20px;'>캐릭터 설정</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        victim_name = st.text_input("피해자 이름", "김영희", help="시뮬레이션에서 사용할 피해자의 이름을 입력하세요")
        victim_role = st.selectbox("피해자 역할", ["어머니", "아버지", "할머니", "할아버지"])
    
    with col2:
        scammer_name = st.text_input("사기꾼이 사칭할 이름", "철수", help="사기꾼이 사칭할 인물의 이름을 입력하세요")
        relationship = st.selectbox("관계", ["자녀", "손자", "조카"])
    
    if victim_name and scammer_name and relationship and not st.session_state.chat_started:
        st.markdown("<br>", unsafe_allow_html=True)
        initialize = st.button("시뮬레이션 시작 💫", type="primary")
        if initialize:
            st.session_state.victim_name = victim_name
            st.session_state.scammer_name = scammer_name
            st.session_state.relationship = relationship
            
            basic_info_given = f"피해자 이름: {victim_name}, 사기꾼 이름: {scammer_name}, 관계: {relationship}"
            
            st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
            st.session_state.messages.append({"role": "user", "content": basic_info_given, "name": "basic_info_given"})
            
            introduction = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=st.session_state.messages,
                response_format=PhishingConversation
            ).choices[0].message.parsed
            st.session_state.messages.append({"role": "assistant", "content": introduction.continued_conversation, "name": "introduction"})
            
            st.session_state.chat_started = True
    
    # Chat interface
    if st.session_state.chat_started:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown("#### 💬 대화 시뮬레이션")
        
        # Display chat messages with enhanced styling
        for message in st.session_state.messages:
            if message['role'] != 'system':
                with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                    st.write(message["content"])
        
        # Chat input with placeholder
        user_input = st.chat_input("메시지를 입력하세요...", key="chat_input")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)
            
            # Get AI response
            response = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=st.session_state.messages,
                response_format=PhishingConversation
            )
            
            ai_response = response.choices[0].message.parsed
            st.session_state.messages.append({"role": "assistant", "content": ai_response.continued_conversation})
            with st.chat_message("assistant", avatar="🤖"):
                st.write(ai_response.continued_conversation)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "통계 및 분석":
    st.markdown('<h2 class="sub-header">통계 및 분석</h2>', unsafe_allow_html=True)
    
    # Enhanced metrics with cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="stat-card">
                <h4 style="color: #1E88E5;">시뮬레이션 완료 횟수</h4>
                <h2 style="color: black;">12회</h2>   
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="stat-card">
                <h4 style="color: #1E88E5;">평균 대응 점수</h4>
                <h2 style="color: black;">85점</h2>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="stat-card">
                <h4 style="color: #1E88E5;">위험 감지율</h4>
                <h2 style="color: black;">78%</h2>
            </div>
        """, unsafe_allow_html=True)
    
    # Enhanced chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📈 대응 능력 향상도 추이")
    st.line_chart({"대응 능력 향상도": [65, 70, 75, 80, 85, 90]})

else:  # 도움말
    st.markdown('<h2 class="sub-header">도움말</h2>', unsafe_allow_html=True)
    
    st.markdown("#### ❓ 자주 묻는 질문")
    with st.expander("Q: 시뮬레이션은 어떻게 진행되나요?"):
        st.info("AI와 실시간 대화를 통해 실제 보이스피싱 상황을 체험할 수 있습니다.")
    
    with st.expander("Q: 개인정보는 안전한가요?"):
        st.info("모든 데이터는 암호화되어 저장되며, 훈련 목적으로만 사용됩니다.")
    
    with st.expander("Q: 피드백은 어떻게 받을 수 있나요?"):
        st.info("시뮬레이션 종료 후 자동으로 상세한 피드백 리포트가 제공됩니다.")

# Enhanced footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>© 2024 보이스피싱 예방 훈련 시스템 | 문의: support@voicephishing-prevention.com</p>
    </div>
""", unsafe_allow_html=True)
