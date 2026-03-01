import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

# Corrected API Initialization
if "GEMINI_KEY" not in st.secrets:
    st.error("🔑 API Key Missing! Set 'GEMINI_KEY' in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
MODEL_ID = "gemini-2.0-flash" # Stable 2026 Production Model

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def generate_questions(content):
    try:
        # Standardized prompt to ensure JSON keys are ALWAYS 'question', 'options', 'answer', 'explanation'
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. 
        CONTENT: {content[:8000]}
        Task: Generate 10 High-Yield MCQs (4 Statement-based, 3 A-R, 3 Standard).
        Rules: 1. Use ONLY NCERT data. 2. Trap students on small details (e.g. units, scientist names).
        JSON Format: [{{ "question": "", "options": ["", "", "", ""], "answer": "exact_option_text", "explanation": "" }}]
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Engine Error: {str(e)}")
        return None

# 3. STATE MANAGEMENT
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'camera_active' not in st.session_state: st.session_state.camera_active = False

# 4. INTERFACE
st.title("🩺 NEET AI Master 2026")
tab1, tab2, tab3 = st.tabs(["📖 By Chapter", "📄 By PDF", "📸 NCERT Lens"])

with tab1:
    chapter = st.text_input("Enter NCERT Chapter Name:", placeholder="e.g. Molecular Basis of Inheritance")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📝 Generate MCQ Test", key="btn_chapter", use_container_width=True):
            with st.spinner("Analyzing Syllabus..."):
                st.session_state.quiz = generate_questions(chapter)
                st.session_state.user_answers, st.session_state.submitted = {}, False
                st.rerun()
    with col_b:
        if st.button("✨ Revision Card", key="rev_card", use_container_width=True):
            with st.spinner("Summarizing..."):
                res = client.models.generate_content(model=MODEL_ID, contents=f"Create a NEET Revision Card for: {chapter}. Include a table of Scientists/Dates and 1 Mnemonic.")
                st.session_state.rev_card = res.text

    if 'rev_card' in st.session_state:
        st.info("📝 NCERT Revision Card")
        st.markdown(st.session_state.rev_card)
        if st.button("Clear Card"): del st.session_state.rev_card; st.rerun()

with tab2:
    st.subheader("📄 PDF Data Extractor")
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 Generate MCQ Test", use_container_width=True):
                text = extract_text_from_pdf(file)
                st.session_state.quiz = generate_questions(text)
                st.session_state.submitted = False
                st.rerun()
        with c2:
            if st.button("📊 Create Data Table", use_container_width=True):
                text = extract_text_from_pdf(file)
                res = client.models.generate_content(model=MODEL_ID, contents=f"Extract all numerical values, partial pressures, or scientist names from this text into a Markdown table: {text[:8000]}")
                st.session_state.data_table = res.text
                st.rerun()

    if 'data_table' in st.session_state:
        st.success("✅ High-Yield Data Table")
        st.markdown(st.session_state.data_table)
        if st.button("🗑️ Clear Table"): del st.session_state.data_table; st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens")
    cam_on = st.toggle("Activate Camera Scanner", value=st.session_state.camera_active)
    st.session_state.camera_active = cam_on
    
    if st.session_state.camera_active:
        img_file = st.camera_input("Scan Diagram")
        if img_file:
            with st.spinner("AI Analysis..."):
                img_bytes = img_file.getvalue()
                response = client.models.generate_content(
                    model=MODEL_ID, 
                    contents=["Identify this NCERT diagram and give 3 NEET tips.", types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
                )
                st.markdown("### 🧬 AI Analysis")
                st.info(response.text)
                

[Image of the human respiratory system diagram with labels for alveoli and bronchioles]


# 5. DISPLAY & SCORING
if st.session_state.quiz:
    st.divider()
    if not st.session_state.submitted:
        st.subheader("📝 Live Test")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            st.session_state.user_answers[i] = st.radio(f"Options for Q{i+1}:", ["Not Attempted"] + q['options'], key=f"ans_{i}")
        
        if st.button("🚀 SUBMIT FINAL TEST"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Scoring and Report logic
        correct = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) == q['answer'])
        wrong = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) not in [q['answer'], "Not Attempted"])
        
        st.header(f"📊 Results: {(correct*4) - (wrong)} Marks")
        st.metric("Accuracy", f"{(correct/len(st.session_state.quiz))*100:.1f}%")
        
        # Report Card Table
        report = []
        for i, q in enumerate(st.session_state.quiz):
            u = st.session_state.user_answers.get(i)
            report.append({"Q": i+1, "Your Ans": u, "Correct": q['answer'], "Result": "✅" if u == q['answer'] else "❌"})
        st.table(report)

        with st.expander("📖 View Detailed NCERT Explanations"):
            for i, q in enumerate(st.session_state.quiz):
                st.write(f"**Q{i+1} Explanation:** {q['explanation']}")
        
        if st.button("🔄 New Test"):
            st.session_state.quiz = None
            st.session_state.submitted = False
            st.rerun()
