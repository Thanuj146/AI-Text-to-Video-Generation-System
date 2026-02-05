import streamlit as st
import os
import requests
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq
from api_key import GROQ_API_KEY

# ---------------------------------------------------
# PAGE CONFIG (UI UPGRADE)
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Text to Video Generator",
    page_icon="🎬",
    layout="centered"
)

# Header
st.markdown("""
<h1 style='text-align: center;'>🎬 AI Video Generator</h1>
<p style='text-align: center; color: gray;'>
Generate cinematic videos using AI script + images + voice
</p>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------
with st.container():
    st.subheader("📌 Enter Topic")
    topic = st.text_input(
        "Video topic",
        placeholder="Example: Future of Artificial Intelligence",
        label_visibility="collapsed"
    )

    generate_btn = st.button("🚀 Generate Video", use_container_width=True)

st.divider()

# ---------------------------------------------------
# GROQ TEXT GENERATION (same logic)
# ---------------------------------------------------
def generate_script(topic):
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role":"user",
            "content":f"""
            Write a clean video script about {topic}.
            5 short paragraphs.
            No titles.
            No symbols.
            Only meaningful spoken content.
            """
        }]
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------
# IMAGE GENERATOR (same logic)
# ---------------------------------------------------
def generate_image(prompt, filename):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        r = requests.get(url, timeout=60)

        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            return True
        return False
    except:
        return False


# ---------------------------------------------------
# MAIN ACTION
# ---------------------------------------------------
if generate_btn:

    if topic == "":
        st.warning("⚠️ Please enter a topic")
        st.stop()

    # Progress UI
    progress = st.progress(0)
    status = st.empty()

    # -------- SCRIPT --------
    status.info("✍️ Generating script using AI...")
    script = generate_script(topic)
    progress.progress(20)

    paragraphs = [p.strip() for p in script.split("\n") if p.strip()][:5]

    os.makedirs("audio", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    clips = []

    # -------- VIDEO BUILD --------
    for i, para in enumerate(paragraphs, start=1):

        status.info(f"🎬 Processing Scene {i}/5")

        img_path = f"images/img{i}.jpg"
        audio_path = f"audio/voice{i}.mp3"

        # IMAGE
        ok = generate_image(para, img_path)
        if not ok:
            img_path = "https://picsum.photos/1280/720"

        # AUDIO
        gTTS(text=para).save(audio_path)
        audio_clip = AudioFileClip(audio_path)

        # VIDEO
        clip = ImageClip(img_path)\
            .set_duration(audio_clip.duration)\
            .set_audio(audio_clip)

        clips.append(clip)

        progress.progress(20 + i * 10)

    # -------- FINAL VIDEO --------
    status.info("🎞️ Rendering final video...")
    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(
        "final_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    progress.progress(100)
    status.success("✅ Video generated successfully!")

    st.divider()

    # OUTPUT UI
    st.subheader("🎥 Final Output")
    st.video("final_video.mp4")

    with open("final_video.mp4", "rb") as f:
        st.download_button(
            "⬇️ Download Video",
            f,
            file_name="ai_video.mp4",
            use_container_width=True
        )
