import json
import os
from datetime import date, datetime
from pathlib import Path

import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "cuemed_data.json"

st.set_page_config(page_title="CueMed", page_icon="💊", layout="wide")
st.title("💊 CueMed")
st.caption("A simple medicine organiser, dose log, and health-notes app")
st.info(
    "CueMed is an organiser, not a medical professional. It does not diagnose or decide "
    "which medicines or doses you should take. Follow your prescription and ask a pharmacist "
    "or clinician if you are unsure."
)

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"medicines": [], "dose_log": [], "notes": []}

def save_data():
    DATA_FILE.write_text(
        json.dumps(st.session_state.data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def get_gemini_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")

def ask_gemini(prompt, history=None):
    key = get_gemini_key()
    if not key:
        return (
            "Gemini is not connected yet. Follow the API-key steps in "
            "README_BEGINNER.md. The built-in FAQ works without Gemini."
        )
    if genai is None:
        return "The Gemini library is missing. In Terminal, run: python3 -m pip install -r requirements.txt"
    try:
        client = genai.Client(api_key=key)
        contents = []
        for item in (history or [])[-10:]:
            contents.append({"role": item["role"], "parts": [{"text": item["text"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config={
                "system_instruction": (
                    "You are CueMed Assistant, a friendly FAQ and general health-information helper. "
                    "Explain things simply. Do not diagnose, prescribe, recommend starting/stopping "
                    "medicines, or decide a personal dose. For medicine-specific concerns, advise "
                    "the user to ask a qualified pharmacist or clinician. Do not claim to know the "
                    "user's medical record. For emergencies, advise contacting local emergency services."
                ),
                "temperature": 0.4,
            },
        )
        return response.text or "I couldn't generate a reply. Please try again."
    except Exception as exc:
        return (
            "I couldn't connect to Gemini. Check the API key, internet connection, and API access. "
            f"Technical detail: {type(exc).__name__}: {exc}"
        )

if "data" not in st.session_state:
    st.session_state.data = load_data()
if "chat" not in st.session_state:
    st.session_state.chat = []

data = st.session_state.data

with st.sidebar:
    st.header("🧭 Menu")
    page = st.radio(
        "Choose a page",
        ["Dashboard", "My Medicines", "Dose Log", "Doctor's Notes", "Gemini Assistant", "About CueMed"]
    )
    st.divider()
    st.caption("Tracker data is saved locally in cuemed_data.json.")
    st.caption("Avoid entering sensitive medical details into the chatbot.")

if page == "Dashboard":
    st.subheader("Your dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Medicines saved", len(data["medicines"]))
    c2.metric("Dose log entries", len(data["dose_log"]))
    c3.metric("Notes saved", len(data["notes"]))
    st.markdown("### Quick start")
    st.markdown(
        "1. Open **My Medicines** to save medicine details from your prescription or packaging.\n"
        "2. Use **Dose Log** to record what happened.\n"
        "3. Use **Doctor's Notes** to organise appointment questions.\n"
        "4. Open **Gemini Assistant** for CueMed FAQs or general information."
    )
    st.warning("This starter app does not send notifications or automatic reminders.")

elif page == "My Medicines":
    st.subheader("💊 My Medicines")
    st.write("Enter details exactly as shown on your prescription or medicine packaging.")
    with st.form("add_medicine", clear_on_submit=True):
        name = st.text_input("Medicine name *")
        strength = st.text_input("Strength (as written on the package, optional)")
        instructions = st.text_input("Instructions (copy from your prescription, optional)")
        note = st.text_area("Extra note (optional)")
        submitted = st.form_submit_button("Save medicine")
        if submitted:
            if not name.strip():
                st.error("Please enter a medicine name.")
            else:
                data["medicines"].append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": name.strip(),
                    "strength": strength.strip(),
                    "instructions": instructions.strip(),
                    "notes": note.strip(),
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data()
                st.success("Medicine saved.")
                st.rerun()
    st.divider()
    if not data["medicines"]:
        st.info("No medicines saved yet.")
    for med in data["medicines"][:]:
        with st.container(border=True):
            st.markdown(f"**{med['name']}**")
            if med.get("strength"):
                st.write(f"Strength: {med['strength']}")
            if med.get("instructions"):
                st.write(f"Prescription instructions: {med['instructions']}")
            if med.get("notes"):
                st.write(f"Note: {med['notes']}")
            if st.button("Delete this entry", key=f"delete_med_{med['id']}"):
                data["medicines"] = [m for m in data["medicines"] if m["id"] != med["id"]]
                save_data()
                st.rerun()

elif page == "Dose Log":
    st.subheader("🗓️ Dose Log")
    st.write("This is a record only; it does not advise whether or when to take a dose.")
    names = [m["name"] for m in data["medicines"]]
    with st.form("dose_log_form", clear_on_submit=True):
        if names:
            selected = st.selectbox("Medicine", names)
        else:
            selected = st.text_input("Medicine name (you can add it under My Medicines first)")
        log_date = st.date_input("Date", value=date.today())
        status = st.selectbox("Record", ["Taken", "Missed", "Skipped on clinician's advice", "Other"])
        details = st.text_input("Optional note")
        submitted = st.form_submit_button("Save log entry")
        if submitted:
            if not selected.strip():
                st.error("Enter or select a medicine name.")
            else:
                data["dose_log"].insert(0, {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "medicine": selected,
                    "date": str(log_date),
                    "status": status,
                    "details": details.strip(),
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data()
                st.success("Log entry saved.")
                st.rerun()
    st.divider()
    if not data["dose_log"]:
        st.info("No dose log entries yet.")
    for entry in data["dose_log"]:
        with st.container(border=True):
            st.markdown(f"**{entry['medicine']}** — {entry['date']}")
            st.write(f"Record: {entry['status']}")
            if entry.get("details"):
                st.write(entry["details"])
            if st.button("Delete log entry", key=f"delete_log_{entry['id']}"):
                data["dose_log"] = [e for e in data["dose_log"] if e["id"] != entry["id"]]
                save_data()
                st.rerun()

elif page == "Doctor's Notes":
    st.subheader("📝 Doctor's Notes")
    with st.form("notes_form", clear_on_submit=True):
        title = st.text_input("Title (for example, questions for next appointment) *")
        body = st.text_area("Note *")
        submitted = st.form_submit_button("Save note")
        if submitted:
            if not title.strip() or not body.strip():
                st.error("Please enter both a title and a note.")
            else:
                data["notes"].insert(0, {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "title": title.strip(),
                    "body": body.strip(),
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data()
                st.success("Note saved.")
                st.rerun()
    st.divider()
    if not data["notes"]:
        st.info("No notes saved yet.")
    for note in data["notes"]:
        with st.container(border=True):
            st.markdown(f"**{note['title']}**")
            st.caption(note["created"])
            st.write(note["body"])
            if st.button("Delete note", key=f"delete_note_{note['id']}"):
                data["notes"] = [n for n in data["notes"] if n["id"] != note["id"]]
                save_data()
                st.rerun()

elif page == "Gemini Assistant":
    st.subheader("✨ CueMed Gemini Assistant")
    st.write("Ask how to use CueMed or ask for general health information. Avoid sharing sensitive personal details.")
    with st.expander("CueMed FAQ"):
        st.markdown("""
**How do I add a medicine?** Choose **My Medicines**, fill in the details from your prescription or package, and save.

**How do I record a dose?** Choose **Dose Log**, select a medicine, choose the date and record, then save.

**Where are entries stored?** In `cuemed_data.json` in this project folder on this computer.

**Does CueMed send reminders?** No. This version does not send notifications.

**Can the assistant decide my dose?** No. Ask a pharmacist or clinician about personal dosing questions.
""")
    if not get_gemini_key():
        st.warning("Gemini API key not found. Follow README_BEGINNER.md to connect it. The FAQ works without Gemini.")
    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])
    prompt = st.chat_input("Ask CueMed Assistant…")
    if prompt:
        st.session_state.chat.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer = ask_gemini(prompt, st.session_state.chat[:-1])
            st.markdown(answer)
        st.session_state.chat.append({"role": "assistant", "text": answer})

elif page == "About CueMed":
    st.subheader("About this beginner project")
    st.markdown("""
- **Interface:** Streamlit
- **Language:** Python
- **Storage:** local JSON file (`cuemed_data.json`)
- **AI assistant:** Google Gemini, when a key is configured
- **Internet:** needed for Gemini chat; tracker pages work locally

### Privacy tips
This is a learning prototype, not encrypted medical storage. Anyone with access to your computer account or project folder may be able to read the saved JSON file. Do not upload real patient data or API keys to public repositories.
""")
    st.download_button(
        "Download a backup of my data",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name="cuemed_backup.json",
        mime="application/json"
    )
    if st.button("Clear ALL saved data"):
        st.session_state.confirm_clear = True
    if st.session_state.get("confirm_clear", False):
        st.error("This permanently removes all medicines, dose log entries, and notes.")
        left, right = st.columns(2)
        if left.button("Yes, clear everything"):
            st.session_state.data = {"medicines": [], "dose_log": [], "notes": []}
            save_data()
            st.session_state.confirm_clear = False
            st.rerun()
        if right.button("Cancel"):
            st.session_state.confirm_clear = False
            st.rerun()
