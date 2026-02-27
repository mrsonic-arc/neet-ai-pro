import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader

# 1. SETUP - HIDDEN API KEY FOR GITHUB
# Instead of a visible key, we use Streamlit's secret manager
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key not found. Please set 'GEMINI_KEY' in Streamlit Secrets.")

MODEL_ID = "gemini-3-flash-preview"

st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")
st.title("🩺 NEET MCQ & Notes Analyzer")

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() for page in reader.pages])

def generate_questions(content, is_pdf=False):
    source_type = "notes" if is_pdf else f"chapter '{content}'"
    prompt = f"""
    Act as a Senior NTA NEET Paper Setter. Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
    The questions must strictly follow the NEET PYQ pattern (2021-2025).

    DISTRIBUTION OF TYPES:
    - 6 Standard MCQs
    - 2 Assertion-Reason (A-R)
    - 1 Match the Column
    - 1 Statement-based

    RETURN ONLY A JSON LIST:
    [
      {{
        "type": "Standard/AR/Match/Statement",
        "question": "..",
        "options": ["A", "B", "C", "D"],
        "answer": "Full string of correct option",
        "explanation": "Provide the exact NCERT reference."
      }}
    ]

    CONTENT: {content[:8000]}
    """
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

# 3. STATE MANAGEMENT
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False

# 4. INTERFACE
tab1, tab2 = st.tabs(["📖 By Chapter", "📄 By PDF"])

with tab1:
    chapter = st.text_input("Enter NCERT Chapter Name:")
    if st.button("Generate Test"):
        with st.spinner("AI is crafting questions..."):
            st.session_state.quiz = generate_questions(chapter)
            st.session_state.user_answers = {}
            st.session_state.submitted = False

with tab2:
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file and st.button("Analyze PDF & Generate"):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(file)
            st.session_state.quiz = generate_questions(text, is_pdf=True)
            st.session_state.user_answers = {}
            st.session_state.submitted = False

# 5. DISPLAY & SCORING
if st.session_state.quiz and not st.session_state.submitted:
    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"#### Q{i+1} ({q['type']})")
        st.write(q['question'])
        st.session_state.user_answers[i] = st.radio(f"Select Answer:", ["Not Attempted"] + q['options'], key=f"q_{i}")
        st.write("---")
    
    if st.button("🚀 SUBMIT TEST"):
        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted:
    correct, wrong = 0, 0
    for i, q in enumerate(st.session_state.quiz):
        user_ans = st.session_state.user_answers.get(i)
        if user_ans == q['answer']: correct += 1
        elif user_ans != "Not Attempted": wrong += 1
    
    score = (correct * 4) - (wrong * 1)
    st.header(f"📊 Your Score: {score} / {len(st.session_state.quiz)*4}")
    st.write(f"Correct: {correct} | Incorrect: {wrong}")
    
    for i, q in enumerate(st.session_state.quiz):
        with st.expander(f"Review Q{i+1}"):
            st.write(f"**Answer:** {q['answer']}")
            st.info(f"**Explantion:** {q['explanation']}")
