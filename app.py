import streamlit as st
import os, requests, numpy as np
from gtts import gTTS

# ---------- IMPORTANT: IMAGEMAGICK PATH ----------
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

# ---------- GROQ ----------
from groq import Groq
from api_key import GROQ_API_KEY

# ---------- PAGE ----------
st.set_page_config(page_title="AI Video Generator", page_icon="🎬")
st.title("🎬 AI Video Generator")

topic = st.text_input("Enter topic for video")

# ---------- GROQ SCRIPT ----------
def generate_script(topic):
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role":"user",
            "content":f"Write a short engaging YouTube video script about {topic} in 5 small paragraphs."
        }]
    )

    return response.choices[0].message.content


# ---------- IMAGE GENERATOR ----------
def generate_image(prompt, filename):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        r = requests.get(url, timeout=60)

        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            return True
        else:
            return False
    except:
        return False


# ---------- BUTTON ----------
if st.button("Generate Video"):

    if topic == "":
        st.warning("Enter topic first")
        st.stop()

    # ---------- TEXT ----------
    st.info("Generating script....")
    script = generate_script(topic)
    st.success("Script generated")

    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    paragraphs = paragraphs[:5]

    os.makedirs("audio", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    clips = []

    for i, para in enumerate(paragraphs, start=1):

        st.write(f"Processing Scene {i}")

        img_path = f"images/img{i}.jpg"
        audio_path = f"audio/voice{i}.mp3"

        # ---------- IMAGE ----------
        ok = generate_image(para, img_path)
        if ok:
            st.success("Image generated")
        else:
            st.warning("Image Genarating")
            img_path = "https://picsum.photos/1280/720"

        # ---------- AUDIO ----------
        gTTS(text=para).save(audio_path)
        audio_clip = AudioFileClip(audio_path)

        # ---------- IMAGE CLIP ----------
        image_clip = ImageClip(img_path).set_duration(audio_clip.duration)
        image_clip = image_clip.set_audio(audio_clip)

        # ---------- TEXT ON VIDEO ----------
        txt_clip = TextClip(
            para,
            fontsize=38,
            color="white",
            font="Arial",
            size=image_clip.size,
            method="caption"
        ).set_duration(audio_clip.duration).set_position("center")

        final_clip = CompositeVideoClip([image_clip, txt_clip])
        clips.append(final_clip)

    # ---------- FINAL VIDEO ----------
    st.info("Rendering final video (30-60 sec)...")
    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(
        "final_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    st.success("✅ Video Generated Successfully!")
    st.video("final_video.mp4")
