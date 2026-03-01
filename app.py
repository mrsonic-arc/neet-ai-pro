import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("🔑 API Key Missing! Set 'GEMINI_KEY' in Streamlit Secrets.")

# Using stable model for better JSON reliability
MODEL_ID = "gemini-2.0-flash" 

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text.strip()
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def generate_questions(content, is_pdf=False):
    if not content or len(content) < 10:
        st.error("❌ Content too short or empty. AI cannot generate questions from this.")
        st.stop()
        
    try:
        # Strict Prompt to ensure JSON keys match the Review Section
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. 
        Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
        RETURN ONLY A JSON LIST with these EXACT keys: "question", "options", "answer", "explanation".
        CONTENT: {content[:8000]}
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2 # Lower temperature = more stable JSON
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"🩺 AI Error: {str(e)}")
        st.stop()

# 3. STATE MANAGEMENT
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

# 4. INTERFACE
st.title("🩺 NEET AI Master 2026")
tab1, tab2, tab3 = st.tabs(["📖 By Chapter", "📄 By PDF", "📸 NCERT Lens"])

with tab1:
    chapter = st.text_input("Enter NCERT Chapter Name (e.g. 'Photosynthesis'):")
    if st.button("Generate Test", key="btn_chapter"):
        with st.spinner("AI is crafting questions..."):
            st.session_state.quiz = generate_questions(chapter)
            st.session_state.user_answers, st.session_state.submitted = {}, False
            st.rerun()

with tab2:
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file and st.button("Analyze PDF", key="btn_pdf"):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(file)
            if text:
                st.session_state.quiz = generate_questions(text, is_pdf=True)
                st.session_state.user_answers, st.session_state.submitted = {}, False
                st.rerun()
            else:
                st.warning("⚠️ This PDF seems to be an image/scan. Try another file or use NCERT Lens.")

with tab3:
    st.subheader("📸 NCERT Lens")
    img_file = st.camera_input("Scan a diagram")
    if img_file:
        with st.spinner("Analyzing..."):
            img_bytes = img_file.getvalue()
            response = client.models.generate_content(
                model=MODEL_ID, 
                contents=["Identify this NCERT diagram and summarize 3 NEET points.", types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
            )
            st.info(response.text)
            if st.button("Create Quiz from Scan"):
                st.session_state.quiz = generate_questions(response.text)
                st.session_state.user_answers, st.session_state.submitted = {}, False
                st.rerun()

# 5. DISPLAY & SCORING
if st.session_state.quiz:
    st.divider()
    if not st.session_state.submitted:
        st.info(f"📝 Test in Progress: {len(st.session_state.quiz)} Questions")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"#### Q{i+1}: {q['question']}")
            # Use 'Not Attempted' as default
            st.session_state.user_answers[i] = st.radio(f"Select for Q{i+1}:", ["Not Attempted"] + q['options'], key=f"q_{i}")
        
        if st.button("🚀 SUBMIT FINAL TEST"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Logic for Review Section with Question Text
        correct_count = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) == q['answer'])
        score = (correct_count * 4) - ((len(st.session_state.quiz) - correct_count) * 1) # Simple score
        
        st.header(f"📊 Results: {score} Marks")
        
        st.subheader("📝 Detailed Review")
        for i, q in enumerate(st.session_state.quiz):
            u_ans = st.session_state.user_answers.get(i)
            c_ans = q['answer']
            
            is_correct = u_ans == c_ans
            status_icon = "✅" if is_correct else "❌"
            
            with st.expander(f"{status_icon} Q{i+1}: {status_icon}"):
                st.write(f"**Question:** {q['question']}") # Added question here as requested
                st.write(f"**Your Answer:** {u_ans}")
                st.write(f"**Correct Answer:** {c_ans}")
                st.info(f"💡 **NCERT Explanation:** {q.get('explanation', 'Refer to NCERT text.')}")

        if st.button("🔄 New Test"):
            st.session_state.quiz = None
            st.session_state.submitted = False
            st.rerun()
