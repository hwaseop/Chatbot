import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import json


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?", "timestamp": datetime.now().isoformat()}]

# datetime을 문자열로 변환하는 함수
def convert_messages_for_openai(messages):
    return [
        {
            "role": msg["role"],
            "content": msg["content"],
            # 문자열 타임스탬프를 datetime 객체로 변환 후, 다시 문자열로 포맷
            "timestamp": datetime.strptime(msg["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S") if "timestamp" in msg else None
        }
        for msg in messages
    ]

# 챗봇 함수
def chat_with_gpt(messages):
    # OpenAI API로 보낼 메시지 변환
    openai_messages = convert_messages_for_openai(messages)

    response = client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=1000,
        messages=openai_messages
    )
    return response.choices[0].message.content.strip()

def extract_chat_topic(messages):
    """
    채팅 로그에서 주제를 추출하는 함수.
    - 사용자 첫 질문을 기반으로 주제를 추출.
    """
    for msg in messages:
        if msg["role"] == "user":
            # 첫 번째 사용자 메시지를 기준으로 주제 추출
            return msg["content"].split()[0][:20]  # 첫 단어 또는 첫 20자 반환
    return "general"  # 기본값

def save_chat_log():
    # 주제 자동 추출
    chat_topic = extract_chat_topic(st.session_state.messages)
    
    # 파일명 생성: 현재 날짜와 채팅 주제를 포함
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{chat_topic}_chat_log.json"
    
    # 사용자 입력 경로 받기
    custom_path = st.text_input(
        "저장할 경로를 입력하세요 (기본 경로: 'saved_chats'):", 
        value="saved_chats"
    )
    
    if st.button("파일 저장"):
        try:
            # 사용자 입력 경로와 파일명 결합
            file_path = os.path.join(custom_path, filename)
            
            # 디렉토리 생성 (없을 경우)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 파일 저장
            with open(file_path, "w", encoding='utf-8') as file:
                json.dump(st.session_state.messages, file, ensure_ascii=False, indent=4)
            
            # 성공 메시지 표시
            st.success(f"채팅 로그가 저장되었습니다: {file_path}")
        except Exception as e:
            # 오류 메시지 표시
            st.error(f"채팅 로그 저장 중 오류가 발생했습니다: {e}")

# 채팅 내용 초기화 함수
def clear_chat():
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?", "timestamp": datetime.now().isoformat()}]

# 사이드바에 버튼 추가
with st.sidebar:
    st.title("🤖 AI Agent")
    st.caption("🚀 Structure Engineering chatbot based on OpenAI")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    if st.button("채팅 로그 저장"):
        save_chat_log()
    if st.button("채팅 내용 초기화"):
        clear_chat()

# 메인 페이지 설정
st.write("채팅 내용을 여기에 표시합니다.")

# 대화 내용 표시
for msg in st.session_state.messages:
    # 문자열 타임스탬프를 datetime 객체로 변환
    timestamp = datetime.strptime(msg["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")  # 시간 포맷

    if msg["role"] == "user":
        # 사용자 메시지
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 5px;">
                <div style="font-size: 12px; color: gray; margin-right: 10px;">{formatted_timestamp}</div>
                <div style="text-align: right; margin-right: 10px; font-size: 20px;">🤔</div>
            </div>
            <div style="text-align: right; border: 1px solid; border-radius: 10px; padding: 10px; margin-left: auto; width: fit-content; max-width: 80%; background-color: #D0E8F2; color: black; margin-bottom: 15px;">
                {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # 챗봇 메시지
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 5px;">
                <div style="text-align: left; margin-right: 10px; font-size: 20px;">🤖</div>
                <div style="font-size: 12px; color: gray; margin-left: 10px;">{formatted_timestamp}</div>
            </div>
            <div style="text-align: left; border: 1px solid; border-radius: 10px; padding: 10px; margin-right: auto; width: fit-content; max-width: 80%; background-color: #F2D0D0; color: black; margin-bottom: 15px;">
                {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    # API 키가 입력되지 않았을 경우 경고 메시지 표시
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # OpenAI 클라이언트 초기화
    client = OpenAI(api_key=openai_api_key)
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()})
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 5px;">
            <div style="font-size: 12px; color: gray; margin-right: 10px;">{formatted_timestamp}</div>
            <div style="text-align: right; margin-right: 10px; font-size: 20px;">🤔</div>
        </div>
        <div style="text-align: right; border: 1px solid; border-radius: 10px; padding: 10px; margin-left: auto; width: fit-content; max-width: 80%; background-color: #D0E8F2; color: black; margin-bottom: 15px;">
            {prompt}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 챗봇 응답 생성
    with st.spinner("챗봇이 응답을 생성 중입니다..."):
        response = chat_with_gpt(st.session_state.messages)
    
    # 챗봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()})
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 5px;">
            <div style="text-align: left; margin-right: 10px; font-size: 20px;">🤖</div>
            <div style="font-size: 12px; color: gray; margin-left: 10px;">{formatted_timestamp}</div>
        </div>
        <div style="text-align: left; border: 1px solid; border-radius: 10px; padding: 10px; margin-right: auto; width: fit-content; max-width: 80%; background-color: #F2D0D0; color: black; margin-bottom: 15px;">
            {response}
        </div>
        """,
        unsafe_allow_html=True
    )
