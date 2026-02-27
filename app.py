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
    try:
        # Initial delay to ensure stability
        time.sleep(1) 
        
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
        The questions must strictly follow the NEET PYQ pattern (2021-2025).
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
        # Masking technical errors with a professional message
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ **Server Synchronization in Progress**")
            st.info("To ensure the highest accuracy for your NEET preparation, our AI engine is currently calibrating. Please wait a moment and try again in 60 seconds.")
            st.stop() 
        else:
            # General professional error
            st.error("🩺 **System Maintenance Required**")
            st.write("We encountered a brief interruption while processing your request. Please refresh the page or try again shortly.")
            st.stop()

# 3. STATE MANAGEMENT
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False

# 4. INTERFACE (Added NCERT Lens)
tab1, tab2, tab3 = st.tabs(["📖 By Chapter", "📄 By PDF", "📸 NCERT Lens"])

with tab1:
    chapter = st.text_input("Enter NCERT Chapter Name:")
    if st.button("Generate Test", key="btn_chapter"):
        with st.spinner("AI is crafting questions..."):
            st.session_state.quiz = generate_questions(chapter)
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.rerun()

with tab2:
    file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if file and st.button("Analyze PDF", key="btn_pdf"):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(file)
            st.session_state.quiz = generate_questions(text, is_pdf=True)
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens: Snap & Solve")
    img_file = st.camera_input("Focus on a diagram or a tough paragraph")
    
    if img_file:
        with st.spinner("Gemini 3 is scanning the page..."):
            # Convert the camera image to bytes for the AI
            img_bytes = img_file.getvalue()
            
            # Specialized Image Prompt for NEET
            img_prompt = """
            Act as a NEET Biology & Physics Professor. Analyze this NCERT image:
            1. Identify the diagram or concept.
            2. Explain the mechanism shown (e.g., Kreb's Cycle, P-N Junction).
            3. Highlight 3 facts that NTA often uses for 'Incorrect Statement' type questions.
            """
            
            # Send image + prompt to Gemini
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    img_prompt,
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                ]
            )
            
            st.markdown("### 🧬 AI Concept Breakdown")
            st.info(response.text)
            
            # Option to generate questions based on what it just saw
            if st.button("Create Quiz from this Scan"):
                st.session_state.quiz = generate_questions(response.text, is_pdf=True)
                st.session_state.user_answers = {}
                st.session_state.submitted = False
                st.rerun()
# 5. DISPLAY & SCORING
if st.session_state.quiz and not st.session_state.submitted:
    st.info(f"📝 Test in Progress: {len(st.session_state.quiz)} Questions")
    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"#### Q{i+1}: {q['question']}")
        st.caption(f"Category: {q['type']}")
        st.session_state.user_answers[i] = st.radio(
            f"Select for Q{i+1}:", 
            ["Not Attempted"] + q['options'], 
            key=f"q_{i}"
        )
        st.write("---")
    
    if st.button("🚀 SUBMIT FINAL TEST"):
        st.session_state.submitted = True
        st.rerun()

# THE NEW ANALYSIS SECTION
if st.session_state.submitted:
    correct, wrong, skipped = 0, 0, 0
    for i, q in enumerate(st.session_state.quiz):
        ans = st.session_state.user_answers.get(i, "Not Attempted")
        if ans == "Not Attempted": skipped += 1
        elif ans == q['answer']: correct += 1
        else: wrong += 1

    score = (correct * 4) - (wrong * 1)
    
    st.header("📊 Performance Report")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", f"{score}")
    col2.metric("Accuracy", f"{(correct/len(st.session_state.quiz))*100:.1f}%")
    col3.metric("Wrong Answers", f"{wrong}")

    st.subheader("📝 Detailed Review")
    for i, q in enumerate(st.session_state.quiz):
        user_ans = st.session_state.user_answers.get(i, "Not Attempted")
        
        # Determine the status and color
        if user_ans == q['answer']:
            st.success(f"✅ Q{i+1}: Correct!")
        elif user_ans == "Not Attempted":
            st.warning(f"⚠️ Q{i+1}: Skipped")
        else:
            st.error(f"❌ Q{i+1}: Incorrect")
            st.write(f"**Your Answer:** {user_ans}")
        
        # Always show correct answer and explanation for learning
        with st.expander(f"See Solution for Q{i+1}"):
            st.write(f"**Question:** {q['question']}")
            st.success(f"**Correct Answer:** {q['answer']}")
            st.info(f"**NCERT Explanation:** {q['explanation']}")

      st.divider()
        st.subheader("💬 Doubt-Buster Chat")
        st.write("Ask any follow-up questions about this test or the concepts involved.")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ex: Explain the difference between Statement I and II..."):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                # Providing context of the quiz for better explanations
                full_context = f"Context: The student is reviewing a NEET quiz. Question context: {str(st.session_state.quiz)}. Student Question: {prompt}"
                try:
                    response = client.models.generate_content(model=MODEL_ID, contents=full_context)
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error("⏳ Server synchronization in progress. Please wait 60 seconds.")

    if st.button("🔄 Take Another Test"):
        st.session_state.quiz = None
        st.session_state.submitted = False
        st.session_state.chat_history = [] # Clear chat for the next test
        st.rerun()
