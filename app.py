import streamlit as st
import asyncio
import edge_tts
import google.generativeai as genai
import io

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="AI 영어 트레이너", page_icon="🎯")
st.title("🎯 AI 영어 트레이너")
st.markdown("---")

# 2. Gemini API 설정 (Streamlit Secrets 사용)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 1.5 flash 모델이 속도와 비용 면에서 가장 효율적입니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API 키 설정 확인 필요: {e}")
    st.stop()

# 3. 사용자 입력 섹션
st.subheader("1단계: 훈련하고 싶은 한글 문장 입력")
kor_text = st.text_input("", placeholder="예: 나이가 많아 회사에서 나가라고 해. 나만의 브랜드를 만들고 싶어.")

# 4. 핵심 로직 실행
if kor_text:
    with st.spinner('AI 트레이너가 문장을 원어민 표현으로 다듬고 있습니다...'):
        try:
            # 수평적 사고: 단순 번역이 아닌 '상황적 맥락'을 부여하는 프롬프트
            prompt = (
                f"Translate the following Korean into natural, conversational English "
                f"that a 20-year-old native speaker would use in daily life: '{kor_text}'. "
                f"Provide ONLY the English sentence without any explanation."
            )
            response = model.generate_content(prompt)
            eng_text = response.text.strip()
            
            # 결과 표시
            st.success("자연스러운 영어 문장이 완성되었습니다!")
            st.subheader(f"🗣 연습 문장: {eng_text}")

            # 5. Edge TTS 음성 생성 (메모리 방식)
            async def get_audio_data(text):
                communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="-5%")
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            audio_bytes = asyncio.run(get_audio_data(eng_text))

            # 6. 재생 및 다운로드 버튼
            st.markdown("### 2단계: 음성을 듣고 낭독 훈련하기")
            st.audio(audio_bytes, format="audio/mp3")
            
            # 파일명 길이 제한(50자) 및 정리
            safe_filename = f"{eng_text[:40]}...".strip() if len(eng_text) > 40 else eng_text
            
            st.download_button(
                label="📥 훈련용 MP3 파일 다운로드",
                data=audio_bytes,
                file_name=f"{safe_filename}.mp3",
                mime="audio/mp3"
            )
            
            st.info("💡 팁: 음성을 듣고 파형을 상상하며 최소 5번 이상 소리 내어 읽어보세요!")

        except Exception as e:
            st.error(f"작동 중 오류가 발생했습니다: {e}")
            st.info("Advanced Settings에서 API 키가 올바르게 입력되었는지 확인해 주세요.")

# 7. 하단 브랜드 메시지
st.markdown("---")
st.caption("Developed by AI English Trainer | Powered by Gemini & Edge TTS")
