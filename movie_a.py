import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import google.generativeai as genai
from gtts import gTTS
import os

# === CONFIGURATION ===
genai.configure(api_key="AIzaSyCTYADQs05BL9dwiE-WKidWOnfLnSLr3sw")  # Replace with your real key

# === PAGE SETTINGS ===
st.set_page_config(page_title="🎬 AI Movie Scene Creator", layout="wide", page_icon="🎥")
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
        border-radius: 10px;
    }
    .stTextArea textarea {
        font-size: 16px;
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #ff6f61;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        padding: 10px 24px;
    }
    </style>
""", unsafe_allow_html=True)

# === TITLE ===
st.title("🎥 AI Movie Scene Creator")
st.subheader("Generate screenwriting-quality movie scenes using AI")

# === INPUT FIELDS ===
col1, col2 = st.columns(2)
with col1:
    character = st.text_input("🎭 Main Character (e.g., ‘Evelyn, a fearless space pilot’)")
with col2:
    plot = st.text_area("🧠 Plot/Premise (e.g., ‘Evelyn crash-lands on an alien planet…’)", height=200)

# === GEMINI FUNCTION ===
def generate_scene(character, plot):
    prompt = f"""
You are a professional screenwriter.

Write a short movie scene formatted in **Hollywood screenplay style** (Final Draft standard).

Inputs:
Character: {character}
Plot/Premise: {plot}

🎬 Instructions:
- Format as a **screenplay**, with:
    - Scene headings (e.g., INT. LOCATION - TIME)
    - Action lines in **third person present tense**
    - CHARACTER names in **ALL CAPS**, **centered**
    - Dialogues **indented**, **no quotation marks**
    - Parentheticals under character names when needed
- Emphasize **visual storytelling and natural dialogue**
- Keep the scene **2–3 minutes long**, around **1–2 pages**
- Keep line breaks and formatting true to screenwriting standards

✍️ Make it cinematic, emotional, and engaging — like a real movie scene someone could shoot tomorrow.
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# === PDF GENERATOR ===
def create_pdf(script_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    for line in script_text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line.strip())
        y -= 14
    c.save()
    buffer.seek(0)
    return buffer

# === TEXT TO SPEECH ===
def text_to_speech(text, filename="scene.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename

# === DISPLAY GENERATED SCENE IF EXISTS ===
if "scene_output" in st.session_state:
    st.markdown("### 🎭 Generated Movie Scene")
    st.markdown(f"```markdown\n{st.session_state['scene_output']}\n```")


# === GENERATE SCENE ===
if st.button("🎬 Generate Movie Scene"):
    if not character.strip() or not plot.strip():
        st.warning("Please fill in both character and plot.")
    else:
        with st.spinner("Creating cinematic magic... 🎞️"):
            try:
                scene_output = generate_scene(character, plot)
                st.session_state["scene_output"] = scene_output
                st.success("✅ Scene generated!")

                st.markdown("### 🎭 Generated Movie Scene")
                st.markdown(f"```markdown\n{scene_output}\n```")

                # Download as PDF
                pdf = create_pdf(scene_output)
                st.download_button(
                    label="📥 Download Scene as PDF",
                    data=pdf,
                    file_name="movie_scene.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

# === LISTEN TO SCENE ===
if st.button("🔊 Listen to Scene"):
    if "scene_output" in st.session_state:
        speech_file = text_to_speech(st.session_state["scene_output"])
        audio_file = open(speech_file, "rb")
        st.audio(audio_file.read(), format="audio/mp3")
    else:
        st.warning("Please generate a scene first.")

# === CLEAR ===
if st.button("❌ Clear Scene"):
    st.session_state.pop("scene_output", None)
