import re  # 상단에 re 모듈 추가
import streamlit as st
import asyncio
import edge_tts
from googletrans import Translator
import io

# 1. 페이지 설정
st.set_page_config(page_title="영어 문장 mp3 생성기", page_icon="🎯")
st.title("🎯 영문장 mp3생성기")
st.markdown("---")

# 2. 사이드바 설정 (목소리 및 속도)
st.sidebar.header("🎙 트레이닝 설정")

# 목소리 옵션 맵 (이름: Voice ID)
voice_map = {
    "미국 남성 1 (Guy)": "en-US-GuyNeural",
    "미국 남성 2 (Christopher)": "en-US-ChristopherNeural",
    "미국 여성 1 (Aria)": "en-US-AriaNeural",
    "미국 여성 2 (Jenny)": "en-US-JennyNeural",
    "영국 남성 (Ryan)": "en-GB-RyanNeural",
    "영국 여성 (Sonia)": "en-GB-SoniaNeural"
}

voice_name = st.sidebar.selectbox("원어민 목소리 선택", list(voice_map.keys()))
selected_voice = voice_map[voice_name]

# 속도 조절 슬라이더 (-50% ~ +50%)
speech_rate = st.sidebar.slider("말하기 속도 조절 (%)", -50, 50, -5, step=5)
rate_str = f"{speech_rate:+d}%"

# 3. 번역기 및 입력 섹션
translator = Translator()

st.subheader("1단계: 훈련하고 싶은 한글 문장 입력")
kor_text = st.text_input(
    label="훈련 문장 입력", 
    placeholder="예: 나만의 브랜드를 만들려고 노력 중이야.",
    label_visibility="collapsed"
)

# 4. 핵심 실행 로직
if kor_text:
    # 한국어 포함 여부 체크 (한글 음절 범위: 가-힣)
    has_korean = re.search('[가-힣]', kor_text)
    
    if not has_korean:
        # 한국어가 없으면 경고 메시지 출력 후 정지
        st.warning("⚠️ 문장에 한국어가 포함되어 있지 않습니다. 한국어로 입력해 주세요!")
        st.stop()  # 이후 로직(번역, TTS) 실행 안 함

    with st.spinner('문장을 변환하고 음성을 생성 중입니다...'):
        try:
            # [Step 1] 구글 번역 (한 -> 영)
            translation = translator.translate(kor_text, src='ko', dest='en')
            eng_text = translation.text
            
            st.success("영어 문장이 준비되었습니다!")
            st.subheader(f"🗣 연습 문장: {eng_text}")

            # [Step 2] Edge TTS 음성 데이터 생성 함수 (비동기)
            async def get_audio_data(text, voice, rate):
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            # 실행
            audio_bytes = asyncio.run(get_audio_data(eng_text, selected_voice, rate_str))

            # [Step 3] 재생 및 다운로드 UI
            st.markdown("---")
            st.markdown("### 2단계: 음성을 듣고 낭독 훈련하기")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio(audio_bytes, format="audio/mp3")
            with col2:
                # 파일명 길이 제한 및 정리
                safe_filename = f"{eng_text[:30]}...".strip() if len(eng_text) > 30 else eng_text
                st.download_button(
                    label="📥 MP3 다운로드",
                    data=audio_bytes,
                    file_name=f"{safe_filename}.mp3",
                    mime="audio/mp3"
                )
            
            st.info(f"💡 현재 설정: **{voice_name}** / 속도 **{rate_str}**")
            st.write("안내: 원어민의 리듬과 억양을 따라 최소 5번 이상 소리 내어 읽어보세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.info("잠시 후 다시 시도해 주세요.")

# 5. 하단 정보
st.markdown("---")
st.caption("Developed by AI English Trainer | Powered by Google Translate & Edge TTS")
