import streamlit as st
import asyncio
import edge_tts
import google.generativeai as genai
import io

# 1. Gemini 설정 (Streamlit Secrets 사용 예정)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API 키 설정이 필요합니다.")

model = genai.GenerativeModel('gemini-1.5-flash') # 무료 속도가 빠른 모델

st.title("🎯 AI 영어 트레이너")
st.write("한글 문장을 입력하면 원어민 표현으로 바꾸고 음성을 생성합니다.")

# 2. 사용자 입력
kor_text = st.text_input("한글 문장 입력:", placeholder="예: 나만의 브랜드를 만들고 싶어.")

if kor_text:
    with st.spinner('AI가 문장을 다듬고 있습니다...'):
        # 3. Gemini로 자연스러운 영작
        prompt = f"Translate the following Korean into natural, conversational English: '{kor_text}'. Provide ONLY the English sentence."
        response = model.generate_content(prompt)
        eng_text = response.text.strip()
        
        st.subheader(f"🗣 연습 문장: {eng_text}")

        # 4. Edge TTS 음성 생성 (메모리 방식)
        async def get_audio():
            communicate = edge_tts.Communicate(eng_text, "en-US-GuyNeural")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        audio_bytes = asyncio.run(get_audio())

        # 5. 재생 및 다운로드
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="MP3 다운로드",
            data=audio_bytes,
            file_name=f"{eng_text[:20]}.mp3",
            mime="audio/mp3"
        )
