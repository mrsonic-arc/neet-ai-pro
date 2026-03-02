import streamlit as st
from google import genai
from google.genai import types
import json
from PyPDF2 import PdfReader
import time
import datetime

# 1. SETUP & CONFIG
st.set_page_config(page_title="NEET AI Master 2026", page_icon="🩺", layout="wide")

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
st.title("🩺 NEET AI Master 2026")
tab1, tab2, tab3, tab4 = st.tabs(["📖 By Chapter", "📄 By PDF", "📸 NCERT Lens", "📊 Full Analytics"])

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

# --- TAB 4: Full Analytics ---
with tab4:
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
        st.info(f"📝 Test in Progress: **{SUBJECT_ICONS.get(subj_label, '📘')} {subj_label} — {topic_label}** | {len(st.session_state.quiz)} Questions")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"#### Q{i+1}: {q['question']}")
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
