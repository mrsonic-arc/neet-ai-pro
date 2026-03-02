import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time
import datetime

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
  --bg:      #080c14;
  --surface: #0e1420;
  --card:    #121a28;
  --border:  #1e2d45;
  --accent:  #00d4ff;
  --accent2: #7b5ea7;
  --accent3: #00ff9d;
  --danger:  #ff4d6d;
  --warn:    #ffb347;
  --text:    #e8edf5;
  --muted:   #7a8ba0;
  --glow:    0 0 24px rgba(0,212,255,0.25);
}

html, body, .stApp {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 10%, rgba(0,212,255,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(123,94,167,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 60% 40%, rgba(0,255,157,0.04) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

h1 {
  font-family: 'Syne', sans-serif !important;
  font-weight: 800 !important;
  font-size: 2.8rem !important;
  background: linear-gradient(135deg, #00d4ff 0%, #7b5ea7 50%, #00ff9d 100%) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  letter-spacing: -0.03em !important;
}
h2, h3 {
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  letter-spacing: -0.02em !important;
}
h4 { font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; color: #c5d0df !important; }
h2::after {
  content: '';
  display: block;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border-radius: 4px;
  margin-top: 6px;
}

/* TABS */
[data-testid="stTabs"] [role="tablist"] {
  background: var(--surface) !important;
  border-radius: 14px !important;
  padding: 5px !important;
  border: 1px solid var(--border) !important;
  gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  color: var(--muted) !important;
  border-radius: 10px !important;
  padding: 8px 16px !important;
  border: none !important;
  background: transparent !important;
  transition: all 0.2s ease !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--text) !important; background: rgba(0,212,255,0.07) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,94,167,0.15)) !important;
  color: var(--accent) !important;
  border: 1px solid rgba(0,212,255,0.25) !important;
  box-shadow: var(--glow) !important;
}

/* BUTTONS */
.stButton > button {
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,94,167,0.1)) !important;
  color: var(--accent) !important;
  border: 1px solid rgba(0,212,255,0.3) !important;
  border-radius: 10px !important;
  padding: 10px 22px !important;
  transition: all 0.25s ease !important;
  letter-spacing: 0.02em !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(123,94,167,0.22)) !important;
  border-color: var(--accent) !important;
  box-shadow: var(--glow) !important;
  transform: translateY(-1px) !important;
  color: #fff !important;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  padding: 10px 14px !important;
  transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: var(--glow) !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* METRICS */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 18px 20px !important;
  position: relative !important;
  overflow: hidden !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover { border-color: rgba(0,212,255,0.3) !important; box-shadow: var(--glow) !important; }
[data-testid="stMetric"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: var(--accent) !important;
}

/* EXPANDERS */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  margin-bottom: 8px !important;
  overflow: hidden !important;
  transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(0,212,255,0.25) !important; }
[data-testid="stExpander"] summary {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  padding: 14px 18px !important;
  background: transparent !important;
}
[data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

/* PROGRESS BAR */
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3)) !important;
  border-radius: 8px !important;
}
[data-testid="stProgress"] > div > div {
  background: var(--border) !important;
  border-radius: 8px !important;
  height: 8px !important;
}

/* RADIO */
[data-testid="stRadio"] > div { gap: 8px !important; }
[data-testid="stRadio"] label {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 10px 16px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}
[data-testid="stRadio"] label:hover {
  border-color: var(--accent) !important;
  background: rgba(0,212,255,0.06) !important;
  color: var(--accent) !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarContent"] { padding: 20px 16px !important; }

/* DATAFRAME */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* DIVIDER */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 24px 0 !important; }

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
  background: var(--card) !important;
  border: 2px dashed var(--border) !important;
  border-radius: 14px !important;
  padding: 20px !important;
  transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* SLIDER */
[data-testid="stSlider"] > div > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* CHAT */
[data-testid="stChatMessage"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  margin-bottom: 8px !important;
}
[data-testid="stChatInput"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stChatInput"] input { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }

/* MULTISELECT */
[data-testid="stMultiSelect"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[data-baseweb="tag"] {
  background: rgba(0,212,255,0.15) !important;
  border: 1px solid rgba(0,212,255,0.3) !important;
  color: var(--accent) !important;
  border-radius: 6px !important;
}

/* DOWNLOAD BUTTON */
[data-testid="stDownloadButton"] button {
  background: linear-gradient(135deg, rgba(0,255,157,0.1), rgba(0,212,255,0.1)) !important;
  color: var(--accent3) !important;
  border-color: rgba(0,255,157,0.3) !important;
}
[data-testid="stDownloadButton"] button:hover {
  background: linear-gradient(135deg, rgba(0,255,157,0.22), rgba(0,212,255,0.22)) !important;
  border-color: var(--accent3) !important;
  box-shadow: 0 0 20px rgba(0,255,157,0.2) !important;
  color: #fff !important;
}

/* CAPTIONS */
small, .stCaption, [data-testid="stCaptionContainer"] {
  color: var(--muted) !important;
  font-size: 0.8rem !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("🔑 API Key Missing! Set 'GEMINI_KEY' in Streamlit Secrets.")

MODEL_ID = "gemini-3-flash-preview"

SUBJECTS = {
    "Physics": ["Mechanics", "Thermodynamics", "Optics", "Electrostatics", "Magnetism", "Modern Physics", "Waves & Sound", "Fluid Mechanics"],
    "Chemistry": ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Biomolecules", "Polymers", "Environmental Chemistry", "Electrochemistry", "Chemical Kinetics"],
    "Biology (Botany)": ["Cell Biology", "Plant Physiology", "Reproduction in Plants", "Genetics & Evolution", "Ecology", "Plant Morphology", "Photosynthesis", "Biotechnology"],
    "Biology (Zoology)": ["Human Physiology", "Animal Kingdom", "Reproduction in Animals", "Genetics", "Evolution", "Human Health & Disease", "Biotechnology", "Neural Control"],
}

SUBJECT_ICONS = {
    "Physics": "⚛️",
    "Chemistry": "🧪",
    "Biology (Botany)": "🌿",
    "Biology (Zoology)": "🧬",
}

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() for page in reader.pages])

def generate_datatable(content):
    try:
        time.sleep(1)
        prompt = f"""
        You are a NEET NCERT Expert. Your job is to read the EXACT text provided below and extract 
        structured factual data ONLY from that text. 
        
        STRICT RULES:
        - Do NOT use any outside knowledge or memory.
        - Do NOT invent, assume, or add any information not explicitly present in the text.
        - ONLY extract facts, terms, comparisons, values, or classifications that are directly stated in the text.
        - The table title MUST reflect the actual topic of the provided text (e.g. if the text is about tissues, 
          the title must be about tissues — NOT hormones, NOT unrelated topics).
        - Choose the most logical column headers based on what the text actually contains 
          (e.g. "Tissue Type | Location | Function | Key Features" for a tissues chapter).
        - Extract at least 10 rows directly from the content.
        - Each row must have exactly the same number of cells as there are columns.
        
        RETURN ONLY a JSON object with:
        - "title": exact topic title derived from the text
        - "columns": list of 3-5 column header strings
        - "rows": list of rows (each row = list of strings matching column count)
        
        TEXT TO EXTRACT FROM:
        {content[:8000]}
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
            st.info("Please wait 60 seconds and try again.")
            st.stop()
        else:
            st.error(f"🩺 **Could not generate table:** {str(e)}")
            st.stop()

def generate_questions(content, subject=None, topic=None, is_pdf=False):
    try:
        time.sleep(1)
        subject_context = f"Subject: {subject}. Topic: {topic}." if subject else ""
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter. {subject_context}
        Using the provided NCERT CONTENT, generate 10 High-Yield MCQs.
        Follow NEET 2021-2025 patterns. Include Standard, A-R, and Statement-based questions.
        RETURN ONLY A JSON LIST with keys: "type", "question", "options", "answer", "explanation".
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
            st.info("To ensure accuracy, our engine is calibrating. Please wait 60 seconds.")
            st.stop()
        else:
            st.error("🩺 **System Maintenance Required**")
            st.stop()

def generate_pyq(subject, topic, year):
    try:
        time.sleep(1)
        year_context = f"from NEET {year}" if year != "All Years (2020–2024)" else "from NEET exams between 2020 and 2024"
        prompt = f"""
        Act as a Senior NTA NEET Paper Setter with access to previous year question papers.
        Generate 10 MCQs that are styled and patterned EXACTLY like real NEET Previous Year Questions 
        {year_context} for the topic: {subject} - {topic}.
        
        Each question must:
        - Feel like a real PYQ (precise, factual, single best answer)
        - Include the approximate year it was asked or could have been asked
        - Cover different difficulty levels (easy, medium, hard)
        - Include Assertion-Reason and Statement types where appropriate
        
        RETURN ONLY A JSON LIST with keys:
        "type", "question", "options", "answer", "explanation", "year", "difficulty"
        Where "difficulty" is one of: "Easy", "Medium", "Hard"
        And "year" is the NEET exam year (e.g. "NEET 2022" or "NEET Pattern")
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ **Server busy.** Please wait 60 seconds.")
            st.stop()
        else:
            st.error("🩺 **Could not generate PYQs.**")
            st.stop()

def generate_study_plan(duration_days, weak_subjects, strong_subjects, target_score, hours_per_day):
    try:
        time.sleep(1)
        prompt = f"""
        You are an expert NEET counselor and study strategist. Create a highly personalized, 
        actionable NEET 2026 study plan.

        Student Profile:
        - Study Duration: {duration_days} days
        - Daily Study Time: {hours_per_day} hours/day
        - Weak Subjects: {', '.join(weak_subjects) if weak_subjects else 'None specified'}
        - Strong Subjects: {', '.join(strong_subjects) if strong_subjects else 'None specified'}
        - Target NEET Score: {target_score}

        Generate a structured plan. RETURN ONLY A JSON object with:
        {{
          "overview": "2-3 sentence motivational summary of the plan",
          "strategy": "2-3 sentence core strategy based on weak/strong areas",
          "weekly_breakdown": [
            {{
              "week_range": "Week 1-2 (or similar range)",
              "theme": "Phase name e.g. Foundation Building",
              "focus": ["Subject - Topic", ...],
              "daily_targets": "Brief daily target description",
              "revision": "Revision strategy for this phase"
            }}
          ],
          "subject_hours": {{
            "Physics": number,
            "Chemistry": number,
            "Biology (Botany)": number,
            "Biology (Zoology)": number
          }},
          "daily_schedule": [
            {{"time": "e.g. 6:00 AM - 7:30 AM", "activity": "description"}}
          ],
          "milestones": [
            {{"day": number, "goal": "measurable goal"}}
          ],
          "tips": ["tip1", "tip2", "tip3", "tip4", "tip5"]
        }}
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ **Server busy.** Please wait 60 seconds.")
            st.stop()
        else:
            st.error("🩺 **Could not generate study plan.**")
            st.stop()

def save_attempt(subject, topic, score, accuracy, correct, wrong, skipped, total):
    """Save a test attempt to session history."""
    attempt = {
        "timestamp": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "subject": subject or "Custom PDF/Image",
        "topic": topic or "—",
        "score": score,
        "accuracy": round(accuracy, 1),
        "correct": correct,
        "wrong": wrong,
        "skipped": skipped,
        "total": total,
    }
    st.session_state.history.append(attempt)

def get_subject_stats():
    """Aggregate stats per subject from history."""
    stats = {}
    for attempt in st.session_state.history:
        subj = attempt["subject"]
        if subj not in stats:
            stats[subj] = {"attempts": 0, "total_score": 0, "total_correct": 0,
                           "total_wrong": 0, "total_skipped": 0, "total_qs": 0, "accuracies": []}
        stats[subj]["attempts"] += 1
        stats[subj]["total_score"] += attempt["score"]
        stats[subj]["total_correct"] += attempt["correct"]
        stats[subj]["total_wrong"] += attempt["wrong"]
        stats[subj]["total_skipped"] += attempt["skipped"]
        stats[subj]["total_qs"] += attempt["total"]
        stats[subj]["accuracies"].append(attempt["accuracy"])
    return stats

# 3. STATE MANAGEMENT
defaults = {
    "quiz": None,
    "user_answers": {},
    "submitted": False,
    "chat_history": [],
    "history": [],
    "current_subject": None,
    "current_topic": None,
    "camera_active": False,
    "datatable": None,
    "pdf_text_cache": None,
    "study_plan": None,
    "pyq_questions": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 4. SIDEBAR — Analytics Panel
with st.sidebar:
    st.markdown("## 📊 Performance Dashboard")

    if not st.session_state.history:
        st.info("Complete a test to see your analytics here!")
    else:
        history = st.session_state.history
        total_tests = len(history)
        overall_accuracy = sum(a["accuracy"] for a in history) / total_tests
        best_score = max(a["score"] for a in history)
        total_correct = sum(a["correct"] for a in history)
        total_wrong = sum(a["wrong"] for a in history)

        st.markdown(f"**Tests Taken:** {total_tests}")
        st.markdown(f"**Overall Accuracy:** {overall_accuracy:.1f}%")
        st.markdown(f"**Best Score:** {best_score} marks")
        st.progress(overall_accuracy / 100)

        st.divider()
        st.markdown("### 📚 Subject-wise Breakdown")
        stats = get_subject_stats()
        for subj, data in stats.items():
            icon = SUBJECT_ICONS.get(subj, "📘")
            avg_acc = sum(data["accuracies"]) / len(data["accuracies"])
            with st.expander(f"{icon} {subj}"):
                st.metric("Avg Accuracy", f"{avg_acc:.1f}%")
                st.metric("Tests Done", data["attempts"])
                st.metric("Total Correct", data["total_correct"])
                st.metric("Total Wrong", data["total_wrong"])
                # Strength indicator
                if avg_acc >= 75:
                    st.success("💪 Strong Area")
                elif avg_acc >= 50:
                    st.warning("📈 Needs Practice")
                else:
                    st.error("🔴 Weak Area — Focus Here!")

        st.divider()
        st.markdown("### 🕓 Recent Tests")
        for attempt in reversed(history[-5:]):
            icon = SUBJECT_ICONS.get(attempt["subject"], "📄")
            st.markdown(
                f"**{icon} {attempt['subject']}** — {attempt['topic']}\n\n"
                f"Score: `{attempt['score']}` | Accuracy: `{attempt['accuracy']}%` | {attempt['timestamp']}"
            )
            st.markdown("---")

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

# 5. MAIN INTERFACE
st.markdown("""
<div class="hero-banner" style="
  background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(123,94,167,0.08) 50%, rgba(0,255,157,0.05) 100%);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 20px;
  padding: 32px 36px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
">
  <div style="position:absolute;right:32px;top:50%;transform:translateY(-50%);font-size:5rem;opacity:0.07;">🩺</div>
  <h1 style="
    font-family: Syne, sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    background: linear-gradient(135deg, #00d4ff 0%, #7b5ea7 50%, #00ff9d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.03em;
  ">NEET AI Master 2026</h1>
  <p style="color:#7a8ba0;font-size:1rem;margin:8px 0 0 0;font-family:'DM Sans',sans-serif;">
    Your AI-powered NEET preparation engine &nbsp;·&nbsp; Smart tests, PYQs, study plans & analytics
  </p>
</div>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 By Chapter", "📄 By PDF", "📸 NCERT Lens",
    "🎯 PYQ Mode", "🗓️ Study Planner", "📊 Full Analytics"
])

# --- TAB 1: By Chapter (with subject + topic picker) ---
with tab1:
    st.subheader("Generate by Subject & Topic")

    col1, col2 = st.columns(2)
    with col1:
        selected_subject = st.selectbox("Select Subject:", list(SUBJECTS.keys()),
                                        format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}")
    with col2:
        selected_topic = st.selectbox("Select Topic:", SUBJECTS[selected_subject])

    custom_chapter = st.text_input("Or type a custom chapter/topic name (optional):")
    content_to_use = custom_chapter if custom_chapter.strip() else f"{selected_subject} - {selected_topic} (NCERT standard)"

    if st.button("🚀 Generate Test", key="btn_chapter"):
        with st.spinner("AI is crafting questions..."):
            st.session_state.quiz = generate_questions(content_to_use, subject=selected_subject, topic=selected_topic)
            st.session_state.current_subject = selected_subject
            st.session_state.current_topic = selected_topic if not custom_chapter.strip() else custom_chapter
            st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
            st.rerun()

# --- TAB 2: By PDF ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        pdf_subject = st.selectbox("Tag Subject (for analytics):", ["— Untagged —"] + list(SUBJECTS.keys()),
                                   format_func=lambda s: s if s == "— Untagged —" else f"{SUBJECT_ICONS[s]} {s}",
                                   key="pdf_subj")
    with col2:
        pdf_topic = st.text_input("Tag Topic (optional):", key="pdf_topic_input")

    file = st.file_uploader("Upload NCERT PDF", type="pdf")

    if file:
        st.markdown("#### 🛠️ What would you like to generate?")
        gen_col1, gen_col2 = st.columns(2)

        with gen_col1:
            if st.button("📝 Generate MCQ Test", key="btn_pdf", use_container_width=True):
                with st.spinner("Reading PDF & crafting questions..."):
                    text = extract_text_from_pdf(file)
                    st.session_state.pdf_text_cache = text
                    st.session_state.datatable = None
                    st.session_state.quiz = generate_questions(text, is_pdf=True)
                    st.session_state.current_subject = None if pdf_subject == "— Untagged —" else pdf_subject
                    st.session_state.current_topic = pdf_topic or "PDF Upload"
                    st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
                    st.rerun()

        with gen_col2:
            if st.button("📊 Generate Data Table", key="btn_datatable", use_container_width=True):
                with st.spinner("Extracting key facts & building table..."):
                    text = extract_text_from_pdf(file)
                    st.session_state.pdf_text_cache = text
                    st.session_state.datatable = generate_datatable(text)
                    st.rerun()

    # --- Display Data Table if generated ---
    if st.session_state.datatable:
        dt = st.session_state.datatable
        st.markdown(f"### 📋 {dt.get('title', 'Extracted Data Table')}")
        st.caption("All high-yield NEET facts extracted from your PDF")

        columns = dt.get("columns", [])
        rows = dt.get("rows", [])

        if columns and rows:
            import pandas as pd
            # Sanitize rows: ensure each row matches column count
            clean_rows = []
            for row in rows:
                if len(row) < len(columns):
                    row = row + ["—"] * (len(columns) - len(row))
                elif len(row) > len(columns):
                    row = row[:len(columns)]
                clean_rows.append(row)

            df = pd.DataFrame(clean_rows, columns=columns)
            df.index += 1  # Start index from 1

            # Search filter
            search = st.text_input("🔍 Search table:", placeholder="Type to filter rows...")
            if search:
                mask = df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")
            else:
                filtered_df = df

            st.dataframe(filtered_df, use_container_width=True, height=450)

            # Download as CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Table as CSV",
                data=csv,
                file_name=f"neet_datatable_{dt.get('title', 'data').replace(' ', '_').lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.divider()
            # Also offer to generate quiz from the same PDF
            if st.session_state.pdf_text_cache:
                if st.button("📝 Also Generate MCQ Test from this PDF", use_container_width=True):
                    with st.spinner("Crafting questions from same PDF..."):
                        st.session_state.quiz = generate_questions(st.session_state.pdf_text_cache, is_pdf=True)
                        st.session_state.current_subject = None if pdf_subject == "— Untagged —" else pdf_subject
                        st.session_state.current_topic = pdf_topic or "PDF Upload"
                        st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
                        st.rerun()
        else:
            st.warning("⚠️ Could not extract structured data from this PDF. Try a more content-rich NCERT chapter.")

# --- TAB 3: NCERT Lens ---
with tab3:
    st.subheader("📸 NCERT Lens")

    col1, col2 = st.columns(2)
    with col1:
        lens_subject = st.selectbox("Tag Subject:", ["— Untagged —"] + list(SUBJECTS.keys()),
                                    format_func=lambda s: s if s == "— Untagged —" else f"{SUBJECT_ICONS[s]} {s}",
                                    key="lens_subj")

    if not st.session_state.camera_active:
        st.info("Click the button below to activate your camera and scan NCERT diagrams.")
        if st.button("🔌 Activate Camera"):
            st.session_state.camera_active = True
            st.rerun()
    else:
        if st.button("❌ Close Camera"):
            st.session_state.camera_active = False
            st.rerun()

        img_file = st.camera_input("Position the diagram within the frame")

        if img_file:
            with st.spinner("Analyzing diagram..."):
                img_bytes = img_file.getvalue()
                img_prompt = "Identify this NCERT diagram and explain 3 high-yield points for NEET 2026."
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[img_prompt, types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")]
                )
                st.markdown("### 🧬 AI Analysis")
                st.info(response.text)

                if st.button("Create Quiz from Scan"):
                    st.session_state.quiz = generate_questions(response.text, is_pdf=True)
                    st.session_state.current_subject = None if lens_subject == "— Untagged —" else lens_subject
                    st.session_state.current_topic = "NCERT Lens Scan"
                    st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
                    st.session_state.camera_active = False
                    st.rerun()

# --- TAB 4: PYQ Mode ---
with tab4:
    st.subheader("🎯 Previous Year Questions Mode")
    st.caption("Practice questions styled after real NEET PYQs from 2020–2024")

    col1, col2, col3 = st.columns(3)
    with col1:
        pyq_subject = st.selectbox("Subject:", list(SUBJECTS.keys()),
                                   format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}",
                                   key="pyq_subj")
    with col2:
        pyq_topic = st.selectbox("Topic:", SUBJECTS[pyq_subject], key="pyq_topic")
    with col3:
        pyq_year = st.selectbox("Year Filter:", [
            "All Years (2020–2024)", "NEET 2024", "NEET 2023",
            "NEET 2022", "NEET 2021", "NEET 2020"
        ], key="pyq_year")

    if st.button("🎯 Load PYQs", key="btn_pyq", use_container_width=True):
        with st.spinner(f"Fetching {pyq_year} style questions for {pyq_topic}..."):
            st.session_state.pyq_questions = generate_pyq(pyq_subject, pyq_topic, pyq_year)
            st.session_state.quiz = st.session_state.pyq_questions
            st.session_state.current_subject = pyq_subject
            st.session_state.current_topic = f"PYQ — {pyq_topic} ({pyq_year})"
            st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
            st.rerun()

    if st.session_state.pyq_questions and not st.session_state.quiz:
        st.info("PYQs loaded! Scroll down to attempt the test.")

# --- TAB 5: Smart Study Planner ---
with tab5:
    st.subheader("🗓️ AI Smart Study Planner")
    st.caption("Get a personalized day-by-day NEET 2026 study plan based on your performance")

    # Auto-detect weak/strong from history
    auto_weak, auto_strong = [], []
    if st.session_state.history:
        stats_for_plan = get_subject_stats()
        for subj, data in stats_for_plan.items():
            avg = sum(data["accuracies"]) / len(data["accuracies"])
            if avg < 50: auto_weak.append(subj)
            elif avg >= 75: auto_strong.append(subj)

    col1, col2 = st.columns(2)
    with col1:
        plan_duration = st.selectbox("Study Duration:", ["30 Days", "60 Days", "90 Days"], index=1)
        plan_hours = st.slider("Daily Study Hours:", min_value=4, max_value=14, value=8, step=1)
        plan_target = st.selectbox("Target Score:", ["600+", "620+", "640+", "660+", "680+", "700+"], index=3)

    with col2:
        all_subjects = list(SUBJECTS.keys())
        plan_weak = st.multiselect(
            "Your Weak Subjects:",
            all_subjects,
            default=auto_weak,
            format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}"
        )
        plan_strong = st.multiselect(
            "Your Strong Subjects:",
            all_subjects,
            default=auto_strong,
            format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}"
        )

    if auto_weak:
        st.info(f"💡 Auto-detected weak areas from your test history: **{', '.join(auto_weak)}**")
    if auto_strong:
        st.success(f"💪 Auto-detected strong areas: **{', '.join(auto_strong)}**")

    if st.button("🗓️ Generate My Study Plan", key="btn_plan", use_container_width=True):
        with st.spinner("AI is crafting your personalized study plan..."):
            days = int(plan_duration.split()[0])
            st.session_state.study_plan = generate_study_plan(
                days, plan_weak, plan_strong, plan_target, plan_hours
            )

    if st.session_state.study_plan:
        plan = st.session_state.study_plan
        st.divider()

        # Overview & Strategy
        st.markdown("### 🚀 Your Personalized NEET Plan")
        st.info(f"📋 **Overview:** {plan.get('overview', '')}")
        st.warning(f"🧠 **Strategy:** {plan.get('strategy', '')}")

        st.divider()

        # Subject Hours Allocation
        st.markdown("### ⏱️ Recommended Subject Hours Allocation")
        hours_data = plan.get("subject_hours", {})
        if hours_data:
            h_cols = st.columns(4)
            for idx, (subj, hrs) in enumerate(hours_data.items()):
                icon = SUBJECT_ICONS.get(subj, "📘")
                h_cols[idx % 4].metric(f"{icon} {subj}", f"{hrs} hrs")

        st.divider()

        # Weekly Breakdown
        st.markdown("### 📅 Week-by-Week Breakdown")
        weekly = plan.get("weekly_breakdown", [])
        for week in weekly:
            with st.expander(f"📆 {week.get('week_range', '')} — {week.get('theme', '')}"):
                st.markdown(f"**🎯 Focus Topics:**")
                for f in week.get("focus", []):
                    st.markdown(f"  - {f}")
                st.markdown(f"**📋 Daily Target:** {week.get('daily_targets', '')}")
                st.markdown(f"**🔁 Revision:** {week.get('revision', '')}")

        st.divider()

        # Daily Schedule
        st.markdown("### 🕐 Recommended Daily Schedule")
        schedule = plan.get("daily_schedule", [])
        if schedule:
            for slot in schedule:
                col_t, col_a = st.columns([1, 3])
                col_t.markdown(f"**{slot.get('time', '')}**")
                col_a.markdown(slot.get("activity", ""))

        st.divider()

        # Milestones
        st.markdown("### 🏁 Key Milestones")
        milestones = plan.get("milestones", [])
        if milestones:
            m_cols = st.columns(min(len(milestones), 3))
            for idx, m in enumerate(milestones):
                with m_cols[idx % 3]:
                    st.metric(f"Day {m.get('day', '')}", "🎯 Goal")
                    st.caption(m.get("goal", ""))

        st.divider()

        # Pro Tips
        st.markdown("### 💡 Pro Tips from Your AI Mentor")
        tips = plan.get("tips", [])
        for tip in tips:
            st.success(f"✅ {tip}")

        # Download plan as text
        plan_text = f"NEET 2026 Study Plan\n{'='*40}\n\n"
        plan_text += f"Overview: {plan.get('overview','')}\n\nStrategy: {plan.get('strategy','')}\n\n"
        for week in weekly:
            plan_text += f"\n{week.get('week_range','')} — {week.get('theme','')}\n"
            plan_text += f"Focus: {', '.join(week.get('focus',[]))}\n"
            plan_text += f"Daily Target: {week.get('daily_targets','')}\n"
        plan_text += "\nMilestones:\n"
        for m in milestones:
            plan_text += f"  Day {m.get('day','')}: {m.get('goal','')}\n"
        plan_text += "\nTips:\n" + "\n".join(f"- {t}" for t in tips)

        st.download_button(
            "⬇️ Download Study Plan as TXT",
            data=plan_text.encode("utf-8"),
            file_name="neet_2026_study_plan.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- TAB 6: Full Analytics ---
with tab6:
    st.subheader("📊 Full Performance Analytics")

    if not st.session_state.history:
        st.info("No tests completed yet. Take a test to see your analytics!")
    else:
        history = st.session_state.history
        stats = get_subject_stats()

        # --- Overall Summary Cards ---
        st.markdown("### 🏆 Overall Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tests Taken", len(history))
        c2.metric("Overall Accuracy", f"{sum(a['accuracy'] for a in history)/len(history):.1f}%")
        c3.metric("Best Score", f"{max(a['score'] for a in history)} marks")
        c4.metric("Total Questions", sum(a['total'] for a in history))

        st.divider()

        # --- Subject Performance Table ---
        st.markdown("### 📚 Subject-wise Performance")
        for subj, data in stats.items():
            icon = SUBJECT_ICONS.get(subj, "📘")
            avg_acc = sum(data["accuracies"]) / len(data["accuracies"])
            st.markdown(f"#### {icon} {subj}")
            cols = st.columns(5)
            cols[0].metric("Tests", data["attempts"])
            cols[1].metric("Avg Accuracy", f"{avg_acc:.1f}%")
            cols[2].metric("Correct", data["total_correct"])
            cols[3].metric("Wrong", data["total_wrong"])
            cols[4].metric("Skipped", data["total_skipped"])
            st.progress(avg_acc / 100)
            if avg_acc >= 75:
                st.success(f"💪 Strong Area in {subj}")
            elif avg_acc >= 50:
                st.warning(f"📈 {subj} needs more practice")
            else:
                st.error(f"🔴 {subj} is a weak area — revise NCERT thoroughly!")
            st.markdown("")

        st.divider()

        # --- Accuracy Trend (simple text-based sparkline) ---
        st.markdown("### 📈 Accuracy Trend (Last 10 Tests)")
        recent = history[-10:]
        trend_cols = st.columns(len(recent))
        for idx, attempt in enumerate(recent):
            icon = SUBJECT_ICONS.get(attempt["subject"], "📄")
            with trend_cols[idx]:
                st.metric(
                    label=f"{icon} T{idx+1}",
                    value=f"{attempt['accuracy']}%",
                    delta=f"{attempt['accuracy'] - (recent[idx-1]['accuracy'] if idx > 0 else attempt['accuracy']):.1f}%" if idx > 0 else None
                )

        st.divider()

        # --- Full History Table ---
        st.markdown("### 🕓 Complete Test History")
        for i, attempt in enumerate(reversed(history)):
            icon = SUBJECT_ICONS.get(attempt["subject"], "📄")
            with st.expander(f"#{len(history)-i} | {icon} {attempt['subject']} — {attempt['topic']} | {attempt['timestamp']}"):
                cols = st.columns(5)
                cols[0].metric("Score", attempt["score"])
                cols[1].metric("Accuracy", f"{attempt['accuracy']}%")
                cols[2].metric("Correct ✅", attempt["correct"])
                cols[3].metric("Wrong ❌", attempt["wrong"])
                cols[4].metric("Skipped ⏭️", attempt["skipped"])

# 6. QUIZ DISPLAY & SCORING
if st.session_state.quiz:
    st.divider()
    if not st.session_state.submitted:
        subj_label = st.session_state.current_subject or "Custom"
        topic_label = st.session_state.current_topic or ""
        st.markdown(f"""
        <div style="
          background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,94,167,0.08));
          border: 1px solid rgba(0,212,255,0.2);
          border-radius: 14px;
          padding: 16px 22px;
          margin-bottom: 20px;
          display: flex;
          align-items: center;
          gap: 12px;
        ">
          <span style="font-size:1.6rem;">{SUBJECT_ICONS.get(subj_label,'📘')}</span>
          <div>
            <div style="font-family:Syne,sans-serif;font-weight:700;color:#e8edf5;font-size:1.1rem;">
              {subj_label} — {topic_label}
            </div>
            <div style="color:#7a8ba0;font-size:0.85rem;margin-top:2px;">
              📝 Test in Progress &nbsp;·&nbsp; {len(st.session_state.quiz)} Questions &nbsp;·&nbsp; +4 / −1 Marking
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quiz):
            year_badge = f" `{q.get('year','')}` " if q.get('year') else ""
            diff = q.get('difficulty', '')
            diff_badge = f"{'🟢' if diff=='Easy' else '🟡' if diff=='Medium' else '🔴' if diff=='Hard' else ''} {diff}" if diff else ""
            st.markdown(f"#### Q{i+1}: {q['question']} {year_badge} {diff_badge}")
            st.session_state.user_answers[i] = st.radio(
                f"Select for Q{i+1}:", ["Not Attempted"] + q['options'], key=f"q_{i}"
            )
        if st.button("🚀 SUBMIT FINAL TEST"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Scoring
        correct_count = wrong_count = skipped_count = 0
        for i, q in enumerate(st.session_state.quiz):
            c_ans = q.get('answer') or q.get('correct_answer') or q.get('correct')
            u_ans = st.session_state.user_answers.get(i)
            if u_ans == c_ans: correct_count += 1
            elif u_ans == "Not Attempted": skipped_count += 1
            else: wrong_count += 1

        score = (correct_count * 4) - (wrong_count * 1)
        total = len(st.session_state.quiz)
        accuracy = (correct_count / total) * 100

        # Auto-save attempt
        already_saved = st.session_state.get("_last_saved_score") == (score, st.session_state.current_topic)
        if not already_saved:
            save_attempt(
                st.session_state.current_subject,
                st.session_state.current_topic,
                score, accuracy, correct_count, wrong_count, skipped_count, total
            )
            st.session_state["_last_saved_score"] = (score, st.session_state.current_topic)

        subj = st.session_state.current_subject or "Custom"
        icon = SUBJECT_ICONS.get(subj, "📘")
        st.header(f"{icon} Results: {score} Marks — {subj}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score", score)
        c2.metric("Accuracy", f"{accuracy:.1f}%")
        c3.metric("Correct ✅", correct_count)
        c4.metric("Wrong ❌", wrong_count)
        st.progress(accuracy / 100)

        # Personalized Feedback
        if accuracy >= 75:
            st.success(f"🎉 Excellent! You're strong in {subj}. Keep it up!")
        elif accuracy >= 50:
            st.warning(f"📈 Good effort! Revise weak topics in {subj} for better results.")
        else:
            st.error(f"🔴 Needs improvement. Focus on NCERT {subj} thoroughly.")

        st.divider()
        st.markdown("### 📋 Detailed Question Review")
        for i, q in enumerate(st.session_state.quiz):
            c_ans = q.get('answer') or q.get('correct_answer') or q.get('correct')
            u_ans = st.session_state.user_answers.get(i)

            if u_ans == c_ans:
                status_icon = "✅"
                status_label = "Correct"
            elif u_ans == "Not Attempted":
                status_icon = "⏭️"
                status_label = "Skipped"
            else:
                status_icon = "❌"
                status_label = "Incorrect"

            with st.expander(f"{status_icon} Q{i+1}: {q['question'][:80]}{'...' if len(q['question']) > 80 else ''}  —  {status_label}"):
                # Full question
                st.markdown(f"**📌 Question:**")
                st.markdown(f"> {q['question']}")

                st.markdown("**🔘 All Options:**")
                for opt in q.get('options', []):
                    if opt == c_ans and opt == u_ans:
                        st.markdown(f"- ✅ **{opt}** ← Your answer (Correct)")
                    elif opt == c_ans:
                        st.markdown(f"- ✅ **{opt}** ← Correct answer")
                    elif opt == u_ans:
                        st.markdown(f"- ❌ ~~{opt}~~ ← Your answer (Wrong)")
                    else:
                        st.markdown(f"- {opt}")

                st.divider()
                if u_ans == "Not Attempted":
                    st.warning("⏭️ You skipped this question.")
                    st.markdown(f"**✅ Correct Answer:** `{c_ans}`")
                elif u_ans == c_ans:
                    st.success(f"✅ You answered correctly: `{c_ans}`")
                else:
                    st.error(f"❌ Your Answer: `{u_ans}`")
                    st.success(f"✅ Correct Answer: `{c_ans}`")

                st.info(f"📖 **NCERT Explanation:** {q.get('explanation', 'Refer to NCERT.')}")

        st.divider()
        st.subheader("💬 Doubt-Buster Chat")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a follow-up doubt..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    res = client.models.generate_content(
                        model=MODEL_ID,
                        contents=f"Quiz context: {str(st.session_state.quiz)}. Question: {prompt}"
                    )
                    st.markdown(res.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
                except:
                    st.error("⏳ Server busy.")

        if st.button("🔄 New Test"):
            st.session_state.quiz = None
            st.session_state.submitted = False
            st.session_state["_last_saved_score"] = None
            st.rerun()
