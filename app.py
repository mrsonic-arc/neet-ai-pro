import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time
from datetime import datetime, timedelta

# 1. SETUP
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

# Standardizing the 2026 Client
if "GEMINI_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
MODEL_ID = "gemini-2.0-flash" # The 2026 standard for speed/accuracy

# 2. STATE INITIALIZATION
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'camera_active' not in st.session_state: st.session_state.camera_active = False

# 3. CORE FUNCTIONS
def generate_questions(content, subject="Biology"):
    # Tailoring the prompt for the NTA 2026 Pattern
    prompt = f"""
    Role: Senior NTA Paper Setter for NEET 2026.
    Content: {content[:10000]} 
    Task: Generate 10 MCQs (4 Statement-based, 3 Assertion-Reason, 3 Standard).
    Subject Style: {subject} (If Physics, include numericals; if Bio, include NCERT line-specific traps).
    Format: Return ONLY a JSON list of objects with: question, options (list of 4), answer (must match one option exactly), explanation.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"NTA Engine Busy. Error: {str(e)}")
        return None

# 4. INTERFACE
st.title("🩺 NEET AI Master 2026")
tab1, tab2, tab3, tab4 = st.tabs(["📖 Chapter", "📄 PDF Master", "📸 NCERT Lens", "📅 NTA Tracker"])

with tab1:
    col_in, col_sub = st.columns([3, 1])
    chapter = col_in.text_input("Enter Topic (e.g., 'Morphology of Flowering Plants')")
    subject = col_sub.selectbox("Subject", ["Biology", "Physics", "Chemistry"], key="tab1_sub")
    
    if st.button("Generate Test", use_container_width=True):
        with st.spinner("Analyzing NCERT Syllabus..."):
            st.session_state.quiz = generate_questions(chapter, subject)
            st.session_state.submitted = False
            st.rerun()

with tab2:
    uploaded_file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        full_text = "".join([p.extract_text() for p in reader.pages])
        if st.button("Extract MCQs from PDF"):
            st.session_state.quiz = generate_questions(full_text, "PDF-Based")
            st.session_state.submitted = False
            st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens")
    # Improved Camera Toggle Logic
    cam_toggle = st.toggle("Power Camera", value=st.session_state.camera_active)
    st.session_state.camera_active = cam_toggle
    
    if st.session_state.camera_active:
        img = st.camera_input("Scan any NCERT Diagram")
        if img:
            with st.spinner("Identifying labels..."):
                res = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        "Label this diagram and give 3 NEET 'Tricky points' from NCERT.",
                        types.Part.from_bytes(data=img.getvalue(), mime_type="image/jpeg")
                    ]
                )
                st.info(res.text)

with tab4:
    st.subheader("📅 NTA Exam Roadmap")
    target_date = st.date_input("When is your next Test?", datetime(2026, 5, 3))
    topics = st.multiselect("Select Chapters", ["Genetics", "Ray Optics", "Thermodynamics", "p-Block"])
    
    if st.button("Generate Roadmap"):
        days_left = (target_date - datetime.now().date()).days
        if days_left > 0:
            st.write(f"### 🗓️ {days_left} Days Remaining")
            for i in range(days_left):
                day_label = (datetime.now() + timedelta(days=i)).strftime("%A, %d %b")
                if (i + 1) % 4 == 0:
                    st.warning(f"🔄 {day_label}: Revision Day (Full Mock)")
                else:
                    topic = topics[i % len(topics)] if topics else "General Revision"
                    st.success(f"🎯 {day_label}: Target - {topic}")

# 5. SHARED QUIZ DISPLAY
if st.session_state.quiz:
    st.divider()
    if not st.session_state.submitted:
        st.subheader("📝 Live Test")
        for idx, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{idx+1}: {q['question']}**")
            st.session_state.user_answers[idx] = st.radio(f"Select Answer {idx}", q['options'], key=f"q_{idx}")
        
        if st.button("Submit Test"):
            st.session_state.submitted = True
            st.rerun()
    else:
        st.subheader("📊 Result Analysis")
        # Logic for score calculation
        correct = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) == q['answer'])
        st.metric("Score", f"{correct}/{len(st.session_state.quiz)}")
        if st.button("Restart Test"):
            st.session_state.quiz = None
            st.rerun()
