import os
import re
import time
import urllib.request

# -------------------------------------------------
# Tell MoviePy where ImageMagick is (Windows)
# -------------------------------------------------
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from gtts import gTTS
from moviepy.editor import *

# -------------------------------------------------
# Safe image download
# -------------------------------------------------
def download_image(url, filename, retries=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    request = urllib.request.Request(url, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                with open(filename, "wb") as f:
                    f.write(response.read())
            return
        except Exception:
            print(f"Image downloaded ({attempt + 1}/{retries})")
            time.sleep(1)
            if attempt == retries - 1:
                raise

# -------------------------------------------------
# Read generated text
# -------------------------------------------------
with open("generated_text.txt", "r", encoding="utf-8") as file:
    text = file.read()

# -------------------------------------------------
# Smart text grouping (prevents too many clips)
# -------------------------------------------------
sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

MAX_CLIPS = 5
MAX_CHARS = 220

paragraphs = []
current = ""

for s in sentences:
    if len(current) + len(s) <= MAX_CHARS:
        current += s + ". "
    else:
        paragraphs.append(current.strip())
        current = s + ". "
    if len(paragraphs) >= MAX_CLIPS:
        break

if current and len(paragraphs) < MAX_CLIPS:
    paragraphs.append(current.strip())

print(f"Total clips: {len(paragraphs)}")

# -------------------------------------------------
# Create folders
# -------------------------------------------------
os.makedirs("audio", exist_ok=True)
os.makedirs("images", exist_ok=True)

final_clips = []

# -------------------------------------------------
# Build clips (IN MEMORY — IMPORTANT)
# -------------------------------------------------
for i, para in enumerate(paragraphs, start=1):
    print(f"Processing clip {i}...")

    # ---------- IMAGE ----------
    try:
        image_url = f"https://source.unsplash.com/1024x1024/?{para.replace(' ', ',')}"
        image_path = f"images/image{i}.jpg"
        download_image(image_url, image_path)
    except Exception:
        image_url = "https://picsum.photos/1024/1024"
        image_path = f"images/image{i}.jpg"
        download_image(image_url, image_path)

    # ---------- AUDIO ----------
    audio_path = f"audio/voiceover{i}.mp3"
    gTTS(text=para, lang="en", slow=False).save(audio_path)

    audio_clip = AudioFileClip(audio_path)

    # ---------- IMAGE CLIP ----------
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
    image_clip = image_clip.set_audio(audio_clip)

    # ---------- TEXT ----------
    text_clip = TextClip(
        para,
        fontsize=40,
        color="white",
        size=image_clip.size,
        method="caption"
    ).set_duration(audio_clip.duration).set_pos("center")

    # ---------- COMPOSE ----------
    video_clip = CompositeVideoClip([image_clip, text_clip])

    final_clips.append(video_clip)
    time.sleep(1)

# -------------------------------------------------
# FINAL VIDEO (AUDIO PRESERVED)
# -------------------------------------------------
print("Creating final video with audio...")
final_video = concatenate_videoclips(final_clips, method="compose")

final_video.write_videofile(
    "final_video.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)

print("✅ Final video created with voiceover: final_video.mp4")
