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

MODEL_ID = "gemini-2.0-flash" 

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() for page in reader.pages if page.extract_text()])

def generate_questions(content, is_pdf=False):
    try:
        time.sleep(1) 
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
        Follow NEET 2021-2025 patterns. Include Standard, A-R, and Statement-based questions.
        RETURN ONLY A JSON LIST with keys: "question", "options", "answer", "explanation".
        CONTENT: {content[:8000]}
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        st.error("⏳ Server busy or quota reached. Please wait a moment.")
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
            st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
            st.rerun()

with tab2:
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file and st.button("Analyze PDF", key="btn_pdf"):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(file)
            st.session_state.quiz = generate_questions(text, is_pdf=True)
            st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
            st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens")
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False

    if not st.session_state.camera_active:
        if st.button("🔌 Activate Camera"):
            st.session_state.camera_active = True
            st.rerun()
    else:
        if st.button("❌ Close Camera"):
            st.session_state.camera_active = False
            st.rerun()
        img_file = st.camera_input("Scan Diagram")
        if img_file:
            with st.spinner("Analyzing diagram..."):
                img_bytes = img_file.getvalue()
                response = client.models.generate_content(
                    model=MODEL_ID, 
                    contents=["Identify this NCERT diagram and explain 3 points.", types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
                )
                st.info(response.text)
                if st.button("Create Quiz from Scan"):
                    st.session_state.quiz = generate_questions(response.text, is_pdf=True)
                    st.session_state.user_answers, st.session_state.submitted = {}, False
                    st.rerun()

# 5. DISPLAY & SCORING
if st.session_state.quiz:
    st.divider()
    if not st.session_state.submitted:
        st.info(f"📝 Test in Progress: {len(st.session_state.quiz)} Questions")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"#### Q{i+1}: {q['question']}")
            st.session_state.user_answers[i] = st.radio(f"Select for Q{i+1}:", ["Not Attempted"] + q['options'], key=f"q_{i}")
        if st.button("🚀 SUBMIT FINAL TEST"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Scoring
        correct_count = 0
        wrong_count = 0
        for i, q in enumerate(st.session_state.quiz):
            c_ans = q.get('answer') or q.get('correct')
            u_ans = st.session_state.user_answers.get(i)
            if u_ans == c_ans: correct_count += 1
            elif u_ans != "Not Attempted": wrong_count += 1
        
        score = (correct_count * 4) - (wrong_count * 1)
        st.header(f"📊 Results: {score} Marks")
        c1, c2, c3 = st.columns(3)
        c1.metric("Correct ✅", correct_count)
        c2.metric("Wrong ❌", wrong_count)
        c3.metric("Accuracy", f"{(correct_count/len(st.session_state.quiz))*100:.1f}%")

        st.divider()
        st.subheader("📝 Detailed Review")
        for i, q in enumerate(st.session_state.quiz):
            c_ans = q.get('answer') or q.get('correct')
            u_ans = st.session_state.user_answers.get(i)
            
            status = "✅ Correct" if u_ans == c_ans else ("⚠️ Skipped" if u_ans == "Not Attempted" else "❌ Incorrect")
            
            with st.expander(f"{status} - View Q{i+1}"):
                st.write(f"**Question:** {q['question']}")
                st.write(f"**Your Answer:** {u_ans}")
                st.write(f"**Correct Answer:** {c_ans}")
                st.info(f"💡 **NCERT Explanation:** {q.get('explanation', 'Check NCERT text for this topic.')}")

        st.divider()
        st.subheader("💬 Doubt-Buster Chat")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask a follow-up doubt..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                res = client.models.generate_content(model=MODEL_ID, contents=f"Context: {str(st.session_state.quiz)}. Query: {prompt}")
                st.markdown(res.text)
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})

        if st.button("🔄 New Test"):
            st.session_state.quiz = None
            st.session_state.submitted = False
            st.rerun()
