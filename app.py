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
    st.header("📅 NTA Exam Roadmap")
    st.info("Plan your path to 720/720. Upload a syllabus PDF or type your custom targets.")

    # 1. Syllabus Input Methods
    input_mode = st.radio("Syllabus Input Method:", ["Type My Own", "Scan Syllabus PDF", "Full NCERT List"])
    
    selected_topics = []

    if input_mode == "Type My Own":
        custom_input = st.text_area("Enter chapters (one per line):", placeholder="Example:\nRotational Motion\nChemical Bonding\nHuman Reproduction")
        selected_topics = [line.strip() for line in custom_input.split('\n') if line.strip()]

    elif input_mode == "Scan Syllabus PDF":
        syllabus_file = st.file_uploader("Upload Syllabus/Schedule PDF", type="pdf", key="syllabus_pdf")
        if syllabus_file:
            with st.spinner("AI is extracting topics from PDF..."):
                raw_text = extract_text_from_pdf(syllabus_file)
                # Ask AI to extract just the topic names
                extraction_prompt = f"Extract a clean list of NEET chapter names from this text. Return ONLY the names separated by commas: {raw_text[:5000]}"
                res = client.models.generate_content(model=MODEL_ID, contents=extraction_prompt)
                extracted_list = res.text.split(',')
                selected_topics = st.multiselect("Confirm Extracted Topics:", extracted_list, default=extracted_list)

    else: # Full NCERT List
        major_units = [
            "Physics: Mechanics", "Physics: Electrodynamics", "Physics: Optics", "Physics: Modern Physics",
            "Chemistry: Physical", "Chemistry: Organic", "Chemistry: Inorganic",
            "Biology: Diversity", "Biology: Genetics", "Biology: Physiology", "Biology: Ecology"
        ]
        selected_topics = st.multiselect("Select Units to Cover:", major_units)

    # 2. Date and Plan Generation
    test_date = st.date_input("Target Test Date:", datetime(2026, 5, 3))
    
    if st.button("🚀 Create My Personalized Roadmap"):
        today = datetime.now().date()
        days_left = (test_date - today).days
        
        if days_left > 0 and selected_topics:
            st.subheader(f"🔥 {days_left}-Day Execution Plan")
            
            # Progress Bar for Motivation
            st.write("Current Progress")
            st.progress(0)

            for i in range(days_left):
                plan_date = today + timedelta(days=i)
                st.markdown("---")
                
                # NTA Spaced Repetition Logic (Revision every 4th day)
                if (i + 1) % 4 == 0:
                    st.warning(f"🔄 **{plan_date.strftime('%d %b')}: Revision & Mock Test**")
                    st.caption("🧠 Brain Tip: Re-solve 'Incorrect' questions from Tab 2. No new theory today.")
                else:
                    # Assign topics from the list
                    topic = selected_topics[i % len(selected_topics)]
                    st.success(f"🎯 **{plan_date.strftime('%d %b')}: Target - {topic}**")
                    
                    # Subject-Specific Study Hacks
                    if "Physic" in topic or "Motion" in topic or "Mechanic" in topic:
                        st.write("💡 **NTA Hack:** Physics is about application. Solve 20 Numericals today.")
                        
                    elif "Bio" in topic or "Plant" in topic or "Human" in topic:
                        st.write("💡 **NTA Hack:** Biology is about NCERT lines. Read Statement-based MCQs.")
                        
                    else:
                        st.write("💡 **NTA Hack:** Chemistry needs memory + logic. Write down all reaction mechanisms.")

            st.balloons()
        else:
            st.error("Please provide topics and a valid future date!")
            
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
