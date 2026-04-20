import streamlit as st
import asyncio
import edge_tts
from googletrans import Translator
import io

# 페이지 설정
st.set_page_config(page_title="AI 영어 트레이너", page_icon="🎯")
st.title("🎯 AI 영어 트레이너")
st.markdown("---")

# 번역기 초기화
translator = Translator()

# 1단계: 입력
st.subheader("1단계: 훈련하고 싶은 한글 문장 입력")
kor_text = st.text_input(
    label="훈련 문장 입력", 
    placeholder="예: 나이가 많아 회사에서 나가라고 해. 나만의 브랜드를 만들고 싶어.",
    label_visibility="collapsed"
)

if kor_text:
    with st.spinner('문장을 영어로 변환하고 음성을 생성 중입니다...'):
        try:
            # 2단계: 구글 번역 (한 -> 영)
            # 수평적 사고: 구글 번역은 직역 느낌이 날 수 있으므로, 결과가 나오면 낭독 훈련에 집중합니다.
            translation = translator.translate(kor_text, src='ko', dest='en')
            eng_text = translation.text
            
            st.success("영어 문장이 준비되었습니다!")
            st.subheader(f"🗣 연습 문장: {eng_text}")

            # 3단계: Edge TTS 음성 생성
            async def get_audio_data(text):
                # 트레이닝을 위해 속도를 5% 낮췄습니다.
                communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="-5%")
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            audio_bytes = asyncio.run(get_audio_data(eng_text))

            # 4단계: 재생 및 다운로드
            st.markdown("### 2단계: 음성을 듣고 낭독 훈련하기")
            st.audio(audio_bytes, format="audio/mp3")
            
            # 파일명 정리
            safe_filename = f"{eng_text[:40]}...".strip() if len(eng_text) > 40 else eng_text
            
            st.download_button(
                label="📥 훈련용 MP3 파일 다운로드",
                data=audio_bytes,
                file_name=f"{safe_filename}.mp3",
                mime="audio/mp3"
            )
            
            st.info("💡 팁: 음성을 듣고 원어민의 리듬을 따라 최소 5번 이상 소리 내어 읽어보세요!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.info("잠시 후 다시 시도해 주세요.")

# 하단 정보
st.markdown("---")
st.caption("Developed by AI English Trainer | Powered by Google Translate & Edge TTS")
