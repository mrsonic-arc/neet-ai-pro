import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time
from datetime import datetime, timedelta

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

if "GEMINI_KEY" not in st.secrets:
    st.error("Missing API Key! Add 'GEMINI_KEY' to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
MODEL_ID = "gemini-2.0-flash" 

# 2. CORE HELPER FUNCTIONS (Must be at the top)
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return ""

def generate_questions(content, subject="Biology"):
    prompt = f"""
    Role: Senior NTA Paper Setter for NEET 2026.
    Content: {content[:10000]} 
    Task: Generate 10 MCQs (4 Statement-based, 3 Assertion-Reason, 3 Standard).
    Subject Style: {subject}.
    Format: Return ONLY a JSON list of objects with: question, options (list of 4), answer, explanation.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"NTA Engine Busy: {e}")
        return None

# 3. STATE MANAGEMENT
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'camera_active' not in st.session_state: st.session_state.camera_active = False

# 4. INTERFACE
st.title("🩺 NEET AI Master 2026")
tab1, tab2, tab3, tab4 = st.tabs(["📖 Chapter", "📄 PDF Master", "📸 NCERT Lens", "📅 NTA Tracker"])

with tab1:
    col_in, col_sub = st.columns([3, 1])
    chapter = col_in.text_input("Enter Topic (e.g., 'Genetics')")
    subject = col_sub.selectbox("Subject", ["Biology", "Physics", "Chemistry"], key="tab1_sub")
    
    if st.button("Generate Test", use_container_width=True):
        with st.spinner("Analyzing NCERT..."):
            st.session_state.quiz = generate_questions(chapter, subject)
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.rerun()

with tab2:
    uploaded_file = st.file_uploader("Upload NCERT PDF", type="pdf")
    if uploaded_file:
        if st.button("Extract MCQs from PDF"):
            with st.spinner("Reading PDF..."):
                full_text = extract_text_from_pdf(uploaded_file)
                st.session_state.quiz = generate_questions(full_text, "PDF-Based")
                st.session_state.submitted = False
                st.session_state.user_answers = {}
                st.rerun()

with tab3:
    st.subheader("📸 NCERT Lens")
    cam_toggle = st.toggle("Power Camera", value=st.session_state.camera_active)
    st.session_state.camera_active = cam_toggle
    
    if st.session_state.camera_active:
        img = st.camera_input("Scan any NCERT Diagram")
        if img:
            with st.spinner("Analyzing..."):
                res = client.models.generate_content(
                    model=MODEL_ID,
                    contents=["Label this diagram and give 3 NEET tips.", types.Part.from_bytes(data=img.getvalue(), mime_type="image/jpeg")]
                )
                st.info(res.text)

with tab4:
    st.header("📅 NTA Exam Roadmap")
    st.info("Plan your path to 720/720. Success in NEET 2026 requires strict revision cycles.")

    # 1. Syllabus Input Methods
    input_mode = st.radio("Input Method:", ["Type My Own", "Scan Syllabus PDF", "Full NCERT List"])
    
    selected_topics = []

    if input_mode == "Type My Own":
        custom_input = st.text_area("Enter chapters (one per line):", placeholder="Example:\nRotational Motion\nChemical Bonding\nHuman Reproduction")
        selected_topics = [line.strip() for line in custom_input.split('\n') if line.strip()]

    elif input_mode == "Scan Syllabus PDF":
        s_file = st.file_uploader("Upload Coaching Syllabus PDF", type="pdf", key="syllabus_upload")
        if s_file:
            with st.spinner("🔍 AI is filtering your Syllabus..."):
                raw_text = extract_text_from_pdf(s_file)
                clean_text = " ".join(raw_text.split())[:6000] 
                
                if not clean_text.strip():
                    st.error("Could not read text. This PDF might be an image-only scan.")
                else:
                    try:
                        extraction_prompt = f"""
                        Extract ONLY the names of NEET chapters/topics from this coaching schedule.
                        Ignore dates, test codes (like M-1, PT-2), and room numbers.
                        Return them as a simple list separated by commas.
                        Text: {clean_text}
                        """
                        res = client.models.generate_content(model=MODEL_ID, contents=extraction_prompt)
                        
                        if res.text:
                            extracted_list = [t.strip() for t in res.text.split(',') if len(t.strip()) > 2]
                            selected_topics = st.multiselect("Confirm/Edit Chapters Found:", extracted_list, default=extracted_list)
                        else:
                            st.warning("AI couldn't find distinct topics. Please use 'Manual Type'.")
                    except Exception as e:
                        st.error("AI Extraction failed due to PDF complexity.")

    else: # Full NCERT List
        major_units = [
            "Physics: Mechanics", "Physics: Thermodynamics", "Physics: Optics", "Physics: Modern Physics",
            "Chemistry: Organic (GOC)", "Chemistry: Inorganic (p-Block)", "Chemistry: Physical",
            "Biology: Human Physiology", "Biology: Genetics & Evolution", "Biology: Ecology"
        ]
        selected_topics = st.multiselect("Select Units to Cover:", major_units)

    # 2. Date and Plan Generation
    test_date = st.date_input("Target Date for Test:", datetime(2026, 5, 3))
    
    if st.button("🚀 Create Roadmap", use_container_width=True):
        today = datetime.now().date()
        days_left = (test_date - today).days
        
        if days_left > 0 and selected_topics:
            st.subheader(f"🔥 {days_left}-Day Execution Plan")
            
            # This string will hold the data for our downloadable file
            roadmap_text = f"NEET 2026 ROADMAP\nTarget Date: {test_date}\nGenerated on: {today}\n" + "="*30 + "\n\n"
            
            for i in range(days_left):
                plan_date = today + timedelta(days=i)
                date_str = plan_date.strftime('%d %b (%a)')
                
                if (i + 1) % 4 == 0:
                    st.warning(f"🔄 **{date_str}: REVISION DAY**")
                    roadmap_text += f"{date_str}: REVISION & MOCK TEST\n"
                else:
                    topic = selected_topics[i % len(selected_topics)]
                    st.success(f"🎯 **{date_str}: {topic}**")
                    roadmap_text += f"{date_str}: {topic}\n"
                    
                    # NTA subject hacks for specific topics
                    if any(word in topic.lower() for word in ["physic", "motion", "mechanic"]):
                        
                    elif any(word in topic.lower() for word in ["bio", "plant", "human", "cell"]):
                        

            # 3. DOWNLOAD BUTTON
            st.divider()
            st.download_button(
                label="📥 Download Roadmap as Text File",
                data=roadmap_text,
                file_name=f"NEET_Roadmap_{test_date}.txt",
                mime="text/plain"
            )
            st.balloons()
        else:
            st.error("Please select topics and ensure the Target Date is in the future!")
            
# 5. SHARED QUIZ DISPLAY & SCORING
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
        correct = 0
        report_card = []
        for i, q in enumerate(st.session_state.quiz):
            u_ans = st.session_state.user_answers.get(i)
            is_correct = u_ans == q['answer']
            if is_correct: correct += 1
            report_card.append({"Q": i+1, "Your Ans": u_ans, "Correct": q['answer'], "Result": "✅" if is_correct else "❌"})
        
        st.metric("Score", f"{correct}/{len(st.session_state.quiz)}")
        st.table(report_card)
        
        with st.expander("Show Explanations"):
            for i, q in enumerate(st.session_state.quiz):
                st.write(f"**Q{i+1}:** {q['explanation']}")
        
        if st.button("Restart Test"):
            st.session_state.quiz = None
            st.rerun()
