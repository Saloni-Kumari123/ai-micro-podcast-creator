import asyncio
import edge_tts
from io import BytesIO
import tempfile
import os
from pydub import AudioSegment

# 🎙️ Voices
MALE_VOICE = "en-US-GuyNeural"
FEMALE_VOICE = "en-US-JennyNeural"

# ⏱️ Natural pause (in ms)
PAUSE = AudioSegment.silent(duration=500)


# ---------------- DUAL VOICE ----------------
async def generate_dual_voice_audio(script: str) -> BytesIO:
    combined_audio = AudioSegment.empty()
    lines = script.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 🎯 Detect speaker
        if line.lower().startswith("host:"):
            voice = MALE_VOICE
            text = line.replace("Host:", "").strip()

        elif line.lower().startswith("guest:"):
            voice = FEMALE_VOICE
            text = line.replace("Guest:", "").strip()

        else:
            voice = MALE_VOICE
            text = line

        if not text:
            continue

        try:
            # Temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name

            # 🎙️ Generate speech
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate="+5%",       # slightly faster (natural)
                pitch="+2Hz"      # subtle variation
            )

            await communicate.save(temp_path)

            # 🎧 Load audio
            segment = AudioSegment.from_file(temp_path, format="mp3")

            # 🔊 Slight volume boost for clarity
            segment = segment + 2

            combined_audio += segment
            combined_audio += PAUSE   # ✅ add pause between lines

            os.remove(temp_path)

        except Exception as e:
            print("⚠️ TTS line failed:", str(e))
            continue

    # Export final audio
    output = BytesIO()
    combined_audio.export(output, format="mp3")
    output.seek(0)

    return output


# ---------------- WRAPPER ----------------
def generate_podcast_audio(script: str) -> BytesIO:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(generate_dual_voice_audio(script))


# ---------------- BACKGROUND MUSIC ----------------
def add_background_music(voice_audio: BytesIO) -> BytesIO:
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        music_path = os.path.join(BASE_DIR, "backend", "assets", "bg_music.mp3")

        voice_audio.seek(0)

        voice = AudioSegment.from_file(voice_audio, format="mp3")
        music = AudioSegment.from_file(music_path, format="mp3")

        # 🎵 Lower music volume more for clarity
        music = music - 30

        # Loop music
        if len(music) < len(voice):
            times = int(len(voice) / len(music)) + 1
            music = music * times

        music = music[:len(voice)]

        final = voice.overlay(music)

        output = BytesIO()
        final.export(output, format="mp3")
        output.seek(0)

        return output

    except Exception as e:
        print("⚠️ Background music error:", str(e))
        return voice_audio  # fallback