import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time
import datetime

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET with AI", page_icon="🩺", layout="wide")

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

def generate_questions(content, subject=None, topic=None, is_pdf=False, custom_input=False):
    try:
        time.sleep(1)
        if custom_input:
            # User typed a custom chapter/topic — treat content as the topic name itself
            prompt = f"""
            Act as a Senior NTA NEET Paper Setter.
            Generate 10 High-Yield MCQs strictly on this topic: "{content}".
            Do NOT deviate to any other chapter or subject. Every question must be directly about: "{content}".
            Follow NEET 2021-2025 patterns. Include Standard, Assertion-Reason, and Statement-based questions.
            RETURN ONLY A JSON LIST with keys: "type", "question", "options", "answer", "explanation".
            """
        elif is_pdf or (subject is None):
            # PDF or image content — extract from the provided text
            prompt = f"""
            Act as a Senior NTA NEET Paper Setter.
            Using the provided NCERT CONTENT below, generate 10 High-Yield MCQs.
            Follow NEET 2021-2025 patterns. Include Standard, A-R, and Statement-based questions.
            RETURN ONLY A JSON LIST with keys: "type", "question", "options", "answer", "explanation".
            CONTENT: {content[:8000]}
            """
        else:
            # Dropdown subject + topic selected
            prompt = f"""
            Act as a Senior NTA NEET Paper Setter.
            Subject: {subject}. Topic: {topic}.
            Generate 10 High-Yield MCQs strictly on "{topic}" from NCERT {subject}.
            Do NOT mix in other topics. Every question must be from: {subject} → {topic}.
            Follow NEET 2021-2025 patterns. Include Standard, A-R, and Statement-based questions.
            RETURN ONLY A JSON LIST with keys: "type", "question", "options", "answer", "explanation".
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

def generate_flashcards(content, custom_input=False):
    try:
        time.sleep(1)
        source = f'the NEET topic: "{content}"' if custom_input else f"the following NCERT content:\n{content[:6000]}"
        prompt = f"""
        You are a NEET revision expert. Generate 15 high-yield flashcards from {source}.
        Each flashcard must be exam-focused: front = concise question or term, back = precise NEET answer.
        Cover definitions, values, comparisons, mechanisms, and mnemonics.
        RETURN ONLY a JSON list of objects with keys: "front", "back", "category"
        where "category" is one of: Definition, Value/Formula, Mechanism, Comparison, Mnemonic
        """
        response = client.models.generate_content(
            model=MODEL_ID, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ Server busy. Please wait 60 seconds."); st.stop()
        else:
            st.error(f"🩺 Could not generate flashcards."); st.stop()

def generate_formula_sheet(topic, subject):
    try:
        time.sleep(1)
        prompt = f"""
        You are a NEET expert. Generate a thorough quick-revision cheat sheet for:
        Subject: {subject}, Topic: {topic}
        Include ALL important formulas, reactions, values, and facts needed for NEET.
        RETURN ONLY a JSON object with:
        {{
          "title": "topic name",
          "subject": "{subject}",
          "sections": [
            {{
              "heading": "section name e.g. Key Formulas / Important Reactions / Must-Know Values / Key Facts",
              "items": [
                {{"label": "name", "content": "formula/value/reaction", "note": "NEET tip or trick"}}
              ]
            }}
          ]
        }}
        Generate at least 4 sections with at least 5 items each. Be thorough and NEET-specific.
        """
        response = client.models.generate_content(
            model=MODEL_ID, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ Server busy. Please wait 60 seconds."); st.stop()
        else:
            st.error(f"🩺 Could not generate formula sheet."); st.stop()

def generate_daily_challenge():
    try:
        today = datetime.date.today().strftime("%d %B %Y")
        prompt = f"""
        Today is {today}. Generate exactly 1 high-yield NEET MCQ as the "Daily Challenge".
        Pick a random NEET subject (Physics/Chemistry/Botany/Zoology) and a tricky but fair question.
        RETURN ONLY a single JSON object (not a list) with keys:
        "subject", "topic", "question", "options" (list of 4), "answer", "explanation", "fun_fact"
        where "fun_fact" is an interesting NEET-relevant fact related to the question.
        """
        response = client.models.generate_content(
            model=MODEL_ID, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⏳ Server busy. Please wait 60 seconds."); st.stop()
        else:
            st.error(f"🩺 Could not generate daily challenge."); st.stop()

def check_and_update_streak():
    today = datetime.date.today()
    last  = st.session_state.last_challenge_date
    if last is None:
        st.session_state.streak = 1
    elif (today - last).days == 1:
        st.session_state.streak += 1
    elif (today - last).days > 1:
        st.session_state.streak = 1
    st.session_state.last_challenge_date = today
    # Award badges
    badges = st.session_state.badges
    streak = st.session_state.streak
    if streak >= 3  and "🔥 3-Day Streak"   not in badges: badges.append("🔥 3-Day Streak")
    if streak >= 7  and "⚡ 7-Day Warrior"  not in badges: badges.append("⚡ 7-Day Warrior")
    if streak >= 14 and "🏆 14-Day Champion" not in badges: badges.append("🏆 14-Day Champion")
    if streak >= 30 and "👑 30-Day Legend"   not in badges: badges.append("👑 30-Day Legend")

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
    "current_q_idx": 0,
    "review_q_idx": 0,
    "flashcards": None,
    "flashcard_idx": 0,
    "flashcard_flipped": False,
    "formula_sheet": None,
    "daily_challenge": None,
    "daily_answered": False,
    "daily_selected": None,
    "streak": 0,
    "last_challenge_date": None,
    "badges": [],
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
  ">NEET with AI</h1>
  <p style="color:#7a8ba0;font-size:1rem;margin:8px 0 0 0;font-family:'DM Sans',sans-serif;">
    Your AI-powered NEET preparation engine &nbsp;·&nbsp; Tests · PYQs · Flashcards · Daily Challenge · Formula Sheets
  </p>
</div>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📖 By Chapter", "📄 By PDF", "📸 NCERT Lens",
    "🎯 PYQ Mode", "🗓️ Study Planner", "📊 Full Analytics",
    "🃏 Flashcards", "⚗️ Formula Sheet", "🔥 Daily Challenge"
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

    if custom_chapter.strip():
        st.info(f"💡 Custom topic detected: **\"{custom_chapter.strip()}\"** — questions will be generated strictly on this topic.")

    if st.button("🚀 Generate Test", key="btn_chapter"):
        with st.spinner("AI is crafting questions..."):
            if custom_chapter.strip():
                # User typed custom — ignore dropdowns entirely
                st.session_state.quiz = generate_questions(
                    custom_chapter.strip(),
                    custom_input=True
                )
                st.session_state.current_subject = selected_subject
                st.session_state.current_topic = custom_chapter.strip()
            else:
                # Use dropdown subject + topic
                st.session_state.quiz = generate_questions(
                    f"{selected_subject} - {selected_topic}",
                    subject=selected_subject,
                    topic=selected_topic
                )
                st.session_state.current_subject = selected_subject
                st.session_state.current_topic = selected_topic
            st.session_state.user_answers, st.session_state.submitted, st.session_state.chat_history = {}, False, []
            st.session_state.current_q_idx, st.session_state.review_q_idx = 0, 0
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
                    st.session_state.current_q_idx, st.session_state.review_q_idx = 0, 0
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
                        st.session_state.current_q_idx, st.session_state.review_q_idx = 0, 0
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
                    st.session_state.current_q_idx, st.session_state.review_q_idx = 0, 0
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
            st.session_state.current_q_idx, st.session_state.review_q_idx = 0, 0
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
                cols[4].metric("Skipped ⏭️", attempt["skipped"])


# --- TAB 7: Flashcard Generator ---
with tab7:
    st.subheader("🃏 Smart Flashcard Generator")
    st.caption("AI-generated revision flashcards — flip to reveal answers")

    fc_col1, fc_col2 = st.columns(2)
    with fc_col1:
        fc_subject = st.selectbox("Subject:", list(SUBJECTS.keys()),
                                  format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}", key="fc_subj")
    with fc_col2:
        fc_topic = st.selectbox("Topic:", SUBJECTS[fc_subject], key="fc_topic")

    fc_custom = st.text_input("Or type a custom topic:", key="fc_custom")

    if st.button("🃏 Generate Flashcards", key="btn_fc", use_container_width=True):
        with st.spinner("Generating flashcards..."):
            if fc_custom.strip():
                st.session_state.flashcards = generate_flashcards(fc_custom.strip(), custom_input=True)
            else:
                st.session_state.flashcards = generate_flashcards(
                    f"{fc_subject} - {fc_topic} NCERT standard", custom_input=True
                )
            st.session_state.flashcard_idx = 0
            st.session_state.flashcard_flipped = False
            st.rerun()

    if st.session_state.flashcards:
        cards = st.session_state.flashcards
        cidx  = st.session_state.flashcard_idx
        card  = cards[cidx]
        flipped = st.session_state.flashcard_flipped

        CATEGORY_COLORS = {
            "Definition":   ("#00d4ff", "rgba(0,212,255,0.08)"),
            "Value/Formula":("#00ff9d", "rgba(0,255,157,0.08)"),
            "Mechanism":    ("#7b5ea7", "rgba(123,94,167,0.12)"),
            "Comparison":   ("#ffb347", "rgba(255,179,71,0.08)"),
            "Mnemonic":     ("#ff4d6d", "rgba(255,77,109,0.08)"),
        }
        cat = card.get("category", "Definition")
        accent, bg = CATEGORY_COLORS.get(cat, ("#00d4ff", "rgba(0,212,255,0.08)"))

        # Progress dots
        fdots = "".join([
            f'<span style="display:inline-block;width:{"24px" if d==cidx else "8px"};height:6px;'
            f'background:{"#00d4ff" if d==cidx else "#1e2d45"};border-radius:4px;margin:0 2px;"></span>'
            for d in range(len(cards))
        ])
        st.markdown(f'<div style="margin-bottom:16px;display:flex;align-items:center;flex-wrap:wrap;">{fdots}</div>', unsafe_allow_html=True)

        # Card counter + category badge
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-family:Syne,sans-serif;font-weight:700;color:#7a8ba0;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.06em;">
            Card {cidx+1} of {len(cards)}
          </span>
          <span style="background:{bg};border:1px solid {accent}44;color:{accent};border-radius:8px;padding:4px 14px;font-size:0.82rem;font-weight:600;">
            {cat}
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Flashcard face
        face_label = "💡 Answer" if flipped else "❓ Question"
        face_content = card["back"] if flipped else card["front"]
        face_color = accent if flipped else "#e8edf5"
        st.markdown(f"""
        <div style="
          background:{bg};
          border:2px solid {accent}44;
          border-left:4px solid {accent};
          border-radius:18px;
          padding:40px 36px;
          margin-bottom:20px;
          min-height:160px;
          display:flex;
          flex-direction:column;
          justify-content:center;
          text-align:center;
          cursor:pointer;
          transition:all 0.3s ease;
        ">
          <div style="font-family:DM Sans,sans-serif;font-size:0.75rem;color:#7a8ba0;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">{face_label}</div>
          <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:{face_color};line-height:1.5;">{face_content}</div>
        </div>
        """, unsafe_allow_html=True)

        # Flip + nav buttons
        btn1, btn2, btn3, btn4 = st.columns([1, 2, 1, 1])
        with btn1:
            if cidx > 0:
                if st.button("← Prev", key="fc_prev", use_container_width=True):
                    st.session_state.flashcard_idx -= 1
                    st.session_state.flashcard_flipped = False
                    st.rerun()
        with btn2:
            flip_label = "👁️ Show Question" if flipped else "💡 Flip to Answer"
            if st.button(flip_label, key="fc_flip", use_container_width=True):
                st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
                st.rerun()
        with btn3:
            if cidx < len(cards) - 1:
                if st.button("Next →", key="fc_next", use_container_width=True):
                    st.session_state.flashcard_idx += 1
                    st.session_state.flashcard_flipped = False
                    st.rerun()
        with btn4:
            if st.button("🔀 Shuffle", key="fc_shuffle", use_container_width=True):
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.flashcard_idx = 0
                st.session_state.flashcard_flipped = False
                st.rerun()

        st.divider()
        with st.expander("📋 View All Flashcards at Once"):
            for i, c in enumerate(cards):
                acc2, bg2 = CATEGORY_COLORS.get(c.get("category","Definition"), ("#00d4ff","rgba(0,212,255,0.08)"))
                st.markdown(f"""
                <div style="background:{bg2};border:1px solid {acc2}33;border-radius:12px;padding:14px 18px;margin-bottom:8px;">
                  <div style="font-size:0.75rem;color:{acc2};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">
                    #{i+1} · {c.get('category','—')}
                  </div>
                  <div style="font-weight:600;color:#e8edf5;margin-bottom:6px;">{c['front']}</div>
                  <div style="color:#a0aec0;font-size:0.9rem;">→ {c['back']}</div>
                </div>
                """, unsafe_allow_html=True)


# --- TAB 8: Formula & Reaction Sheet ---
with tab8:
    st.subheader("⚗️ Formula & Reaction Sheet")
    st.caption("AI-generated quick-revision cheat sheet for any NEET topic")

    fs_col1, fs_col2 = st.columns(2)
    with fs_col1:
        fs_subject = st.selectbox("Subject:", list(SUBJECTS.keys()),
                                  format_func=lambda s: f"{SUBJECT_ICONS[s]} {s}", key="fs_subj")
    with fs_col2:
        fs_topic = st.selectbox("Topic:", SUBJECTS[fs_subject], key="fs_topic")

    fs_custom = st.text_input("Or type a custom topic:", key="fs_custom")

    if st.button("⚗️ Generate Cheat Sheet", key="btn_fs", use_container_width=True):
        final_topic   = fs_custom.strip() if fs_custom.strip() else fs_topic
        final_subject = fs_subject
        with st.spinner("Generating formula sheet..."):
            st.session_state.formula_sheet = generate_formula_sheet(final_topic, final_subject)
            st.rerun()

    if st.session_state.formula_sheet:
        fs = st.session_state.formula_sheet
        icon_fs = SUBJECT_ICONS.get(fs.get("subject", ""), "⚗️")

        st.markdown(f"""
        <div style="
          background:linear-gradient(135deg,rgba(0,255,157,0.07),rgba(0,212,255,0.07));
          border:1px solid rgba(0,255,157,0.2);
          border-radius:16px;padding:22px 28px;margin-bottom:24px;
        ">
          <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;color:#00ff9d;">
            {icon_fs} {fs.get('title','Formula Sheet')}
          </div>
          <div style="color:#7a8ba0;font-size:0.88rem;margin-top:4px;">{fs.get('subject','')} · Quick Revision Cheat Sheet</div>
        </div>
        """, unsafe_allow_html=True)

        SECTION_COLORS = ["#00d4ff","#00ff9d","#ffb347","#7b5ea7","#ff4d6d","#00d4ff"]
        for si, section in enumerate(fs.get("sections", [])):
            sc = SECTION_COLORS[si % len(SECTION_COLORS)]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:20px 0 12px 0;">
              <div style="width:4px;height:22px;background:{sc};border-radius:4px;"></div>
              <span style="font-family:Syne,sans-serif;font-weight:700;font-size:1rem;color:{sc};">
                {section.get('heading','')}
              </span>
            </div>
            """, unsafe_allow_html=True)

            for item in section.get("items", []):
                note_html = f'<div style="color:#7a8ba0;font-size:0.8rem;margin-top:4px;">💡 {item["note"]}</div>' if item.get("note") else ""
                st.markdown(f"""
                <div style="
                  background:#121a28;border:1px solid #1e2d45;border-left:3px solid {sc};
                  border-radius:10px;padding:12px 18px;margin-bottom:8px;
                ">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                    <span style="font-family:DM Sans,sans-serif;font-weight:600;color:#c5d0df;font-size:0.9rem;">{item.get('label','')}</span>
                    <code style="background:rgba({('0,212,255' if sc=='#00d4ff' else '0,255,157' if sc=='#00ff9d' else '255,179,71' if sc=='#ffb347' else '123,94,167')},0.12);color:{sc};padding:3px 10px;border-radius:6px;font-size:0.9rem;">{item.get('content','')}</code>
                  </div>
                  {note_html}
                </div>
                """, unsafe_allow_html=True)

        # Download as text
        sheet_text = f"NEET Formula Sheet: {fs.get('title','')}\n{'='*50}\n\n"
        for section in fs.get("sections", []):
            sheet_text += f"\n{section.get('heading','')}\n{'-'*30}\n"
            for item in section.get("items", []):
                sheet_text += f"  {item.get('label','')}: {item.get('content','')}"
                if item.get("note"): sheet_text += f"  [Tip: {item['note']}]"
                sheet_text += "\n"
        st.divider()
        st.download_button("⬇️ Download Cheat Sheet as TXT", data=sheet_text.encode(),
                           file_name=f"neet_formula_{fs.get('title','sheet').replace(' ','_').lower()}.txt",
                           mime="text/plain", use_container_width=True)


# --- TAB 9: Daily Challenge ---
with tab9:
    st.subheader("🔥 Daily Challenge")
    st.caption("One fresh NEET question every day — build your streak & earn badges")

    today_str = datetime.date.today().strftime("%A, %d %B %Y")

    # Streak + badges display
    streak = st.session_state.streak
    badges = st.session_state.badges

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("🔥 Current Streak", f"{streak} day{'s' if streak != 1 else ''}")
    sc2.metric("📅 Today", datetime.date.today().strftime("%d %b %Y"))
    sc3.metric("🏅 Badges Earned", len(badges))

    if badges:
        st.markdown("**Your Badges:** " + "  ".join(badges))

    st.divider()

    # Load today's challenge
    already_today = (
        st.session_state.last_challenge_date == datetime.date.today()
        and st.session_state.daily_challenge is not None
    )

    if not already_today and st.session_state.daily_challenge is None:
        if st.button("🎯 Load Today's Challenge", key="btn_daily", use_container_width=True):
            with st.spinner("Fetching today's challenge..."):
                st.session_state.daily_challenge = generate_daily_challenge()
                st.session_state.daily_answered = False
                st.session_state.daily_selected = None
                st.rerun()

    if st.session_state.daily_challenge:
        dc = st.session_state.daily_challenge
        dc_icon = SUBJECT_ICONS.get(dc.get("subject",""), "🎯")

        st.markdown(f"""
        <div style="
          background:linear-gradient(135deg,rgba(255,77,109,0.07),rgba(255,179,71,0.07));
          border:1px solid rgba(255,77,109,0.2);
          border-radius:16px;padding:20px 26px;margin-bottom:20px;
          display:flex;align-items:center;justify-content:space-between;
        ">
          <div>
            <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;color:#ff4d6d;">
              🔥 Daily Challenge — {today_str}
            </div>
            <div style="color:#7a8ba0;font-size:0.85rem;margin-top:4px;">
              {dc_icon} {dc.get('subject','')} · {dc.get('topic','')}
            </div>
          </div>
          <div style="font-size:2rem;">{dc_icon}</div>
        </div>
        """, unsafe_allow_html=True)

        # Question
        st.markdown(f"""
        <div style="
          background:#121a28;border:1px solid #1e2d45;
          border-left:4px solid #ff4d6d;
          border-radius:14px;padding:24px 28px;margin-bottom:20px;
        ">
          <p style="font-family:DM Sans,sans-serif;font-size:1.05rem;color:#e8edf5;line-height:1.65;margin:0;">
            {dc.get('question','')}
          </p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.daily_answered:
            dc_ans = st.radio("Choose your answer:", dc.get("options", []), key="dc_radio")
            if st.button("✅ Submit Answer", key="btn_dc_submit", use_container_width=True):
                st.session_state.daily_selected = dc_ans
                st.session_state.daily_answered = True
                check_and_update_streak()
                st.rerun()
        else:
            correct = dc.get("answer", "")
            chosen  = st.session_state.daily_selected
            is_right = chosen == correct

            for opt in dc.get("options", []):
                if opt == correct and opt == chosen:
                    bg2, bd2, fc2, tag2 = "rgba(0,255,157,0.08)","#00ff9d44","#00ff9d","✅ Your answer · Correct"
                elif opt == correct:
                    bg2, bd2, fc2, tag2 = "rgba(0,255,157,0.06)","#00ff9d33","#00ff9d","✅ Correct answer"
                elif opt == chosen:
                    bg2, bd2, fc2, tag2 = "rgba(255,77,109,0.08)","#ff4d6d44","#ff4d6d","❌ Your answer · Wrong"
                else:
                    bg2, bd2, fc2, tag2 = "rgba(255,255,255,0.02)","#1e2d4566","#7a8ba0",""
                st.markdown(f"""
                <div style="background:{bg2};border:1px solid {bd2};border-radius:10px;
                  padding:12px 18px;margin-bottom:8px;font-family:DM Sans,sans-serif;
                  font-size:0.95rem;color:{fc2};display:flex;justify-content:space-between;align-items:center;">
                  <span>{opt}</span><span style="font-size:0.8rem;">{tag2}</span>
                </div>
                """, unsafe_allow_html=True)

            result_color = "#00ff9d" if is_right else "#ff4d6d"
            result_msg   = "🎉 Correct! +1 to your streak!" if is_right else "😤 Incorrect! Better luck tomorrow."
            st.markdown(f"""
            <div style="background:rgba({('0,255,157' if is_right else '255,77,109')},0.08);
              border:1px solid rgba({('0,255,157' if is_right else '255,77,109')},0.25);
              border-radius:12px;padding:16px 20px;margin:16px 0;
              font-family:DM Sans,sans-serif;font-weight:600;color:{result_color};font-size:1rem;">
              {result_msg}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
              border-radius:10px;padding:14px 18px;margin-bottom:12px;
              font-family:DM Sans,sans-serif;font-size:0.9rem;color:#c5d0df;line-height:1.6;">
              📖 <strong style="color:#00d4ff;">Explanation:</strong>&nbsp; {dc.get('explanation','')}
            </div>
            """, unsafe_allow_html=True)

            if dc.get("fun_fact"):
                st.markdown(f"""
                <div style="background:rgba(255,179,71,0.06);border:1px solid rgba(255,179,71,0.2);
                  border-radius:10px;padding:14px 18px;
                  font-family:DM Sans,sans-serif;font-size:0.88rem;color:#ffb347;line-height:1.6;">
                  🌟 <strong>Fun Fact:</strong>&nbsp; {dc.get('fun_fact','')}
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.badges:
                newly = st.session_state.badges[-1]
                st.success(f"🏅 New badge unlocked: **{newly}**!")

            st.info(f"🔥 Current streak: **{st.session_state.streak} day(s)** — come back tomorrow to keep it going!")


# 6. QUIZ DISPLAY & SCORING
if st.session_state.quiz:
    st.divider()
    quiz     = st.session_state.quiz
    total_qs = len(quiz)

    # ── QUIZ IN PROGRESS (one question at a time) ──────────────────────────
    if not st.session_state.submitted:
        idx         = st.session_state.current_q_idx
        q           = quiz[idx]
        subj_label  = st.session_state.current_subject or "Custom"
        topic_label = st.session_state.current_topic or ""

        # Header bar
        st.markdown(f"""
        <div style="
          background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,94,167,0.08));
          border: 1px solid rgba(0,212,255,0.2);
          border-radius: 14px;
          padding: 14px 22px;
          margin-bottom: 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        ">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.5rem;">{SUBJECT_ICONS.get(subj_label,'📘')}</span>
            <div>
              <div style="font-family:Syne,sans-serif;font-weight:700;color:#e8edf5;font-size:1rem;">
                {subj_label} — {topic_label}
              </div>
              <div style="color:#7a8ba0;font-size:0.8rem;margin-top:2px;">
                📝 Test in Progress &nbsp;·&nbsp; +4 / −1 Marking
              </div>
            </div>
          </div>
          <div style="
            font-family:Syne,sans-serif;font-weight:800;
            font-size:1.4rem;color:#00d4ff;
            background:rgba(0,212,255,0.1);
            border:1px solid rgba(0,212,255,0.25);
            border-radius:10px;padding:6px 18px;
          ">{idx+1} / {total_qs}</div>
        </div>
        """, unsafe_allow_html=True)

        # Progress dots
        dots = ""
        for d in range(total_qs):
            if d == idx:
                dots += '<span style="display:inline-block;width:28px;height:6px;background:#00d4ff;border-radius:4px;margin:0 2px;"></span>'
            elif d in st.session_state.user_answers and st.session_state.user_answers[d] != "Not Attempted":
                dots += '<span style="display:inline-block;width:10px;height:6px;background:#7b5ea7;border-radius:4px;margin:0 2px;"></span>'
            else:
                dots += '<span style="display:inline-block;width:10px;height:6px;background:#1e2d45;border-radius:4px;margin:0 2px;"></span>'
        st.markdown(f'<div style="margin-bottom:20px;display:flex;align-items:center;flex-wrap:wrap;">{dots}</div>', unsafe_allow_html=True)

        # Question card
        year_badge = f'<span style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.25);color:#00d4ff;border-radius:6px;padding:2px 10px;font-size:0.78rem;margin-left:8px;">{q.get("year","")}</span>' if q.get("year") else ""
        diff = q.get("difficulty", "")
        diff_color = {"Easy": "#00ff9d", "Medium": "#ffb347", "Hard": "#ff4d6d"}.get(diff, "")
        diff_dot = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(diff, "")
        diff_badge = f'<span style="background:rgba(255,255,255,0.04);border:1px solid {diff_color}44;color:{diff_color};border-radius:6px;padding:2px 10px;font-size:0.78rem;margin-left:6px;">{diff_dot} {diff}</span>' if diff else ""

        st.markdown(f"""
        <div style="
          background:#121a28;
          border:1px solid #1e2d45;
          border-left:3px solid #00d4ff;
          border-radius:14px;
          padding:24px 28px;
          margin-bottom:20px;
        ">
          <div style="display:flex;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:6px;">
            <span style="font-family:Syne,sans-serif;font-weight:700;color:#7a8ba0;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.06em;">Question {idx+1}</span>
            {year_badge}{diff_badge}
          </div>
          <p style="font-family:DM Sans,sans-serif;font-size:1.05rem;color:#e8edf5;line-height:1.65;margin:0;">{q['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Answer options
        current_ans = st.session_state.user_answers.get(idx, "Not Attempted")
        options_list = ["Not Attempted"] + q['options']
        safe_index = options_list.index(current_ans) if current_ans in options_list else 0
        answer = st.radio(
            "Choose your answer:",
            options_list,
            index=safe_index,
            key=f"q_radio_{idx}"
        )
        st.session_state.user_answers[idx] = answer

        # Navigation buttons
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        is_last = (idx == total_qs - 1)

        if is_last:
            nav_col1, nav_col2 = st.columns([1, 2])
            with nav_col1:
                if idx > 0:
                    if st.button("← Previous", key="q_prev", use_container_width=True):
                        st.session_state.current_q_idx -= 1
                        st.rerun()
            with nav_col2:
                if st.button("🚀 Submit Final Test", key="q_submit", use_container_width=True):
                    st.session_state.submitted = True
                    st.session_state.review_q_idx = 0
                    st.rerun()
        else:
            nav_col1, nav_col2 = st.columns([1, 1])
            with nav_col1:
                if idx > 0:
                    if st.button("← Previous", key="q_prev", use_container_width=True):
                        st.session_state.current_q_idx -= 1
                        st.rerun()
            with nav_col2:
                if st.button("Next →", key="q_next", use_container_width=True):
                    st.session_state.current_q_idx += 1
                    st.rerun()

    # ── RESULTS & REVIEW ──────────────────────────────────────────────────
    else:
        # Score calculation
        correct_count = wrong_count = skipped_count = 0
        for i, q in enumerate(quiz):
            c_ans = q.get('answer') or q.get('correct_answer') or q.get('correct')
            u_ans = st.session_state.user_answers.get(i)
            if u_ans == c_ans: correct_count += 1
            elif u_ans == "Not Attempted": skipped_count += 1
            else: wrong_count += 1

        score    = (correct_count * 4) - (wrong_count * 1)
        accuracy = (correct_count / total_qs) * 100

        already_saved = st.session_state.get("_last_saved_score") == (score, st.session_state.current_topic)
        if not already_saved:
            save_attempt(
                st.session_state.current_subject,
                st.session_state.current_topic,
                score, accuracy, correct_count, wrong_count, skipped_count, total_qs
            )
            st.session_state["_last_saved_score"] = (score, st.session_state.current_topic)

        subj = st.session_state.current_subject or "Custom"
        icon = SUBJECT_ICONS.get(subj, "📘")

        # Result banner
        feedback_color = "#00ff9d" if accuracy >= 75 else "#ffb347" if accuracy >= 50 else "#ff4d6d"
        feedback_msg   = "🎉 Excellent performance!" if accuracy >= 75 else "📈 Good effort, keep revising!" if accuracy >= 50 else "🔴 Focus on NCERT fundamentals."
        st.markdown(f"""
        <div style="
          background: linear-gradient(135deg, rgba(0,212,255,0.07), rgba(123,94,167,0.07));
          border: 1px solid rgba(0,212,255,0.18);
          border-radius: 18px;
          padding: 28px 32px;
          margin-bottom: 24px;
          position: relative;
          overflow: hidden;
        ">
          <div style="position:absolute;right:28px;top:50%;transform:translateY(-50%);font-size:4rem;opacity:0.07;">{icon}</div>
          <div style="font-family:Syne,sans-serif;font-weight:800;font-size:2.2rem;color:#00d4ff;margin-bottom:4px;">
            {score} Marks
          </div>
          <div style="font-family:DM Sans,sans-serif;color:#7a8ba0;font-size:0.95rem;">
            {subj} &nbsp;·&nbsp; {st.session_state.current_topic or ''}
          </div>
          <div style="margin-top:12px;font-family:DM Sans,sans-serif;color:{feedback_color};font-size:1rem;font-weight:500;">
            {feedback_msg}
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score", score)
        c2.metric("Accuracy", f"{accuracy:.1f}%")
        c3.metric("Correct ✅", correct_count)
        c4.metric("Wrong ❌", wrong_count)
        st.progress(accuracy / 100)

        # ── Review: one question at a time ─────────────────────────────────
        st.divider()
        st.markdown("### 📋 Question Review")

        ridx  = st.session_state.review_q_idx
        rq    = quiz[ridx]
        c_ans = rq.get('answer') or rq.get('correct_answer') or rq.get('correct')
        u_ans = st.session_state.user_answers.get(ridx, "Not Attempted")

        if u_ans == c_ans:
            r_color = "#00ff9d"; r_icon = "✅"; r_label = "Correct"
            rgb = "0,255,157"
        elif u_ans == "Not Attempted":
            r_color = "#ffb347"; r_icon = "⏭️"; r_label = "Skipped"
            rgb = "255,179,71"
        else:
            r_color = "#ff4d6d"; r_icon = "❌"; r_label = "Incorrect"
            rgb = "255,77,109"

        # Review progress dots
        rdots = ""
        for d in range(total_qs):
            q_c = quiz[d].get('answer') or quiz[d].get('correct_answer') or quiz[d].get('correct')
            q_u = st.session_state.user_answers.get(d, "Not Attempted")
            if d == ridx:
                dc, dw = "#00d4ff", "28px"
            elif q_u == q_c:
                dc, dw = "#00ff9d", "10px"
            elif q_u == "Not Attempted":
                dc, dw = "#ffb347", "10px"
            else:
                dc, dw = "#ff4d6d", "10px"
            rdots += f'<span style="display:inline-block;width:{dw};height:6px;background:{dc};border-radius:4px;margin:0 2px;"></span>'
        st.markdown(f'<div style="margin-bottom:16px;display:flex;align-items:center;flex-wrap:wrap;">{rdots}</div>', unsafe_allow_html=True)

        # Review header
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <span style="font-family:Syne,sans-serif;font-weight:700;color:#7a8ba0;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.06em;">
            Reviewing Question {ridx+1} of {total_qs}
          </span>
          <span style="background:rgba({rgb},0.12);border:1px solid rgba({rgb},0.3);color:{r_color};border-radius:8px;padding:4px 14px;font-family:DM Sans,sans-serif;font-size:0.85rem;font-weight:600;">
            {r_icon} {r_label}
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Question text
        st.markdown(f"""
        <div style="
          background:#121a28;border:1px solid #1e2d45;
          border-left:3px solid {r_color};border-radius:14px;
          padding:22px 26px;margin-bottom:18px;
        ">
          <p style="font-family:DM Sans,sans-serif;font-size:1.05rem;color:#e8edf5;line-height:1.65;margin:0;">{rq['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Options
        for opt in rq.get('options', []):
            if opt == c_ans and opt == u_ans:
                bg, bd, fc, tag = "rgba(0,255,157,0.08)", "#00ff9d44", "#00ff9d", "✅ Your answer · Correct"
            elif opt == c_ans:
                bg, bd, fc, tag = "rgba(0,255,157,0.06)", "#00ff9d33", "#00ff9d", "✅ Correct answer"
            elif opt == u_ans:
                bg, bd, fc, tag = "rgba(255,77,109,0.08)", "#ff4d6d44", "#ff4d6d", "❌ Your answer · Wrong"
            else:
                bg, bd, fc, tag = "rgba(255,255,255,0.02)", "#1e2d4566", "#7a8ba0", ""
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {bd};border-radius:10px;padding:12px 18px;margin-bottom:8px;
              font-family:DM Sans,sans-serif;font-size:0.95rem;color:{fc};
              display:flex;justify-content:space-between;align-items:center;">
              <span>{opt}</span>
              <span style="font-size:0.8rem;opacity:0.9;">{tag}</span>
            </div>
            """, unsafe_allow_html=True)

        # Explanation
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
          border-radius:10px;padding:14px 18px;margin-top:14px;
          font-family:DM Sans,sans-serif;font-size:0.9rem;color:#c5d0df;line-height:1.6;">
          📖 <strong style="color:#00d4ff;">NCERT Explanation:</strong>&nbsp; {rq.get('explanation', 'Refer to NCERT.')}
        </div>
        """, unsafe_allow_html=True)

        # Review navigation
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        r_is_last = (ridx == total_qs - 1)

        if r_is_last:
            rn1, rn2 = st.columns([1, 2])
            with rn1:
                if ridx > 0:
                    if st.button("← Previous", key="r_prev", use_container_width=True):
                        st.session_state.review_q_idx -= 1
                        st.rerun()
            with rn2:
                if st.button("🔄 Start New Test", key="r_new", use_container_width=True):
                    st.session_state.quiz = None
                    st.session_state.submitted = False
                    st.session_state.current_q_idx = 0
                    st.session_state.review_q_idx = 0
                    st.session_state["_last_saved_score"] = None
                    st.rerun()
        else:
            rn1, rn2 = st.columns([1, 1])
            with rn1:
                if ridx > 0:
                    if st.button("← Previous", key="r_prev", use_container_width=True):
                        st.session_state.review_q_idx -= 1
                        st.rerun()
            with rn2:
                if st.button("Next →", key="r_next", use_container_width=True):
                    st.session_state.review_q_idx += 1
                    st.rerun()

        # Doubt-Buster Chat
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
                        contents=f"Quiz context: {str(quiz)}. Question: {prompt}"
                    )
                    st.markdown(res.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
                except:
                    st.error("⏳ Server busy.")
