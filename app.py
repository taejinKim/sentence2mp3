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

# 기존: model = genai.GenerativeModel('gemini-1.5-flash')
# 수정: 모델의 전체 경로를 명시합니다.
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-1.5-flash') # 대비책



st.title("🎯 AI 영어 트레이너")
st.write("한글 문장을 입력하면 원어민 표현으로 바꾸고 음성을 생성합니다.")

# 2. 사용자 입력
kor_text = st.text_input("한글 문장 입력:", placeholder="예: 나만의 브랜드를 만들고 싶어.")

if kor_text:
    with st.spinner('AI가 문장을 다듬고 있습니다...'):
        try:
            # 3. Gemini로 자연스러운 영작
            prompt = f"Translate the following Korean into natural, conversational English: '{kor_text}'. Provide ONLY the English sentence."
            response = model.generate_content(prompt)
            # response.text를 가져올 때 발생할 수 있는 오류 방지
            if response and response.text:
                eng_text = response.text.strip()
            else:
                st.error("AI로부터 응답을 받지 못했습니다.")
                st.stop()
        except Exception as e:
            st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")
            st.info("Tip: API 키가 정확한지, 혹은 지원되지 않는 모델 이름인지 확인해 보세요.")
            st.stop()             

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
