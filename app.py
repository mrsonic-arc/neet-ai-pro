import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time # Fixed: Added missing import

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key not found. Please set 'GEMINI_KEY' in Streamlit Secrets.")

MODEL_ID = "gemini-3-flash-preview"

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() for page in reader.pages])

def generate_questions(content, is_pdf=False):
    try:
        time.sleep(1) # Safety delay for free tier
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
        The questions must strictly follow the NEET PYQ pattern (2021-2025).
        Include Standard, A-R, and Statement-based questions.
        RETURN ONLY A JSON LIST.
        CONTENT: {content[:8000]}
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ **Server Synchronization in Progress**")
            st.info("To ensure the highest accuracy, our AI engine is calibrating. Please try again in 60 seconds.")
            st.stop()
        else:
            st.error("🩺 **System Maintenance Required**")
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
    chapter = st.text_input("Enter NCERT Chapter Name:")
    if st.button("Generate Test", key="btn_chapter"):
        with st.spinner("AI is crafting questions..."):
            st.session_state.quiz = generate_questions(chapter)
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.chat_history = []
            st.rerun()

with tab2:
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file and st.button("Analyze PDF", key="btn_pdf"):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(file)
            st.session_state.quiz = generate_questions(text, is_pdf=True)
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.chat_history = []
            st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens: Snap & Solve")
    img_file = st.camera_input("Focus on a diagram or page")
    if img_file:
        with st.spinner("Scanning..."):
            img_bytes = img_file.getvalue()
            img_prompt = "Analyze this NCERT image. Identify the diagram/concept and explain 3 key points NTA asks."
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[img_prompt, types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
            )
            st.info(response.text)
            if st.button("Create Quiz from this Scan"):
                st.session_state.quiz = generate_questions(response.text, is_pdf=True)
                st.session_state.user_answers = {}
                st.session_state.submitted = False
                st.rerun()

# 5. DISPLAY & SCORING
if st.session_state.quiz:
    if not st.session_state.submitted:
        st.info(f"📝 Test in Progress: {len(st.session_state.quiz)} Questions")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"#### Q{i+1}: {q['question']}")
            st.session_state.user_answers[i] = st.radio(f"Select for Q{i+1}:", ["Not Attempted"] + q['options'], key=f"q_{i}")
        
        if st.button("🚀 SUBMIT FINAL TEST"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Scoring Logic
        correct = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) == q['answer'])
        wrong = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.user_answers.get(i) != q['answer'] and st.session_state.user_answers.get(i) != "Not Attempted")
        
        st.header(f"📊 Score: {(correct*4)-(wrong*1)}")
        col1, col2 = st.columns(2)
        col1.metric("Accuracy", f"{(correct/len(st.session_state.quiz))*100:.1f}%")
        col2.metric("Correct", f"{correct}")

        for i, q in enumerate(st.session_state.quiz):
            with st.expander(f"Review Q{i+1}"):
                st.write(f"**Your Answer:** {st.session_state.user_answers.get(i)}")
                st.write(f"**Correct Answer:** {q['answer']}")
                st.info(f"**NCERT Reference:** {q['explanation']}")

        # Doubt-Buster (Correctly placed OUTSIDE the loop)
        st.divider()
        st.subheader("💬 Doubt-Buster Chat")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about these questions..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                context = f"Student is reviewing NEET questions: {str(st.session_state.quiz)}. Doubt: {prompt}"
                try:
                    response = client.models.generate_content(model=MODEL_ID, contents=context)
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except:
                    st.error("⏳ Server busy. Try again in 60s.")

        if st.button("🔄 Take Another Test"):
            st.session_state.quiz = None
            st.session_state.submitted = False
            st.session_state.chat_history = []
            st.rerun()
