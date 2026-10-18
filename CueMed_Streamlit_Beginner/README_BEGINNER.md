# CueMed — Beginner Setup Guide (Mac)

This is a new CueMed project made with **Python + Streamlit only**. It does not use Supabase.
Gemini is optional: the tracker and built-in FAQ work without it; Gemini chat needs an API key and internet.

## What is included?
- Dashboard
- My Medicines
- Dose Log
- Doctor's Notes
- Gemini Assistant with a built-in CueMed FAQ
- Local JSON storage and a backup download button

> **Health safety:** CueMed is an organiser, not a medical device or medical professional. It does not prescribe, diagnose, choose a dose, or send automatic reminders. Ask a pharmacist or clinician if you are unsure about medicine instructions.

## Part 1 — Extract the ZIP
1. Download `CueMed_Streamlit_Beginner.zip`.
2. Double-click it to extract it.
3. Open the extracted `CueMed_Streamlit_Beginner` folder.
4. Keep it somewhere easy to find, such as Downloads.

## Part 2 — Install the packages
1. Open **Terminal** on your Mac: Finder → Applications → Utilities → Terminal.
2. Go to the folder. If you extracted it into Downloads, type:

   ```bash
   cd ~/Downloads/CueMed_Streamlit_Beginner
   ```

   If this says the folder does not exist, type `cd ` (with a space), drag the extracted folder from Finder into Terminal, and press Return.

3. Install packages:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

Wait until installation finishes.

## Part 3 — Create a Gemini API key
You can skip this if you only want the tracker and FAQ.

1. Open Google AI Studio: https://aistudio.google.com/
2. Sign in with your Google account.
3. Find **Get API key** (the page wording may change).
4. Create an API key. Follow any prompts to select or create a project.
5. Copy the key and keep it private, like a password.
6. Check the usage limits and terms shown by Google; access and pricing can change.

## Part 4 — Connect the key to CueMed
Run these commands in Terminal **from inside the CueMed project folder**, one at a time:

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
open -e .streamlit/secrets.toml
```

The `touch` command creates the file first, so TextEdit can open it.

In TextEdit, paste this one line, replacing the sample text with your real key:

```toml
GEMINI_API_KEY = "paste_your_real_key_here"
```

Keep the quotation marks. Save with **Command + S**, then close TextEdit. Never share `secrets.toml`, and do not paste your key into `app.py`.

## Part 5 — Run CueMed
In Terminal, from the project folder, run:

```bash
python3 -m streamlit run app.py
```

A browser tab should open. If not, copy the local address shown in Terminal (usually `http://localhost:8501`) into your browser. Keep Terminal open while using the app.

To stop the app, click Terminal and press **Control + C**.

## Part 6 — Use Python IDLE (optional)
IDLE is useful for viewing and editing the code, but Streamlit must be launched from Terminal.

1. Open Python IDLE.
2. Choose **File → Open…** and select `app.py`.
3. Read or edit the code, then save with **Command + S**.
4. Run or restart the app in Terminal with `python3 -m streamlit run app.py`.

Do not use IDLE's **Run Module** to start the Streamlit website.

## Part 7 — Save and back up your work
- Entries are saved in `cuemed_data.json` inside the project folder.
- Use **About CueMed → Download a backup of my data** to download a backup.
- Keep the JSON file private. This starter app is not encrypted medical storage.

## Troubleshooting

### `cd: no such file or directory`
The folder is somewhere else or has a different name. Type `cd `, drag the extracted folder into Terminal, and press Return.

### `secrets.toml does not exist`
Run these commands in order, from the project folder:

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
open -e .streamlit/secrets.toml
```

### `streamlit: command not found`
Use:

```bash
python3 -m streamlit run app.py
```

### Gemini cannot connect
- Check the key is copied correctly into `.streamlit/secrets.toml`.
- Check the line is formatted as `GEMINI_API_KEY = "your-key"`.
- Stop CueMed with Control + C and restart it after changing the key.
- Check internet access, key status, API access, and usage limits.
- Never share your key in screenshots or public repositories.

### Package error
From the project folder, run:

```bash
python3 -m pip install -r requirements.txt
```

## Files in this project
- `app.py` — Streamlit application
- `requirements.txt` — packages to install
- `cuemed_data.json` — local tracker data
- `.streamlit/secrets.toml.example` — example key format
- `.gitignore` — helps avoid sharing secrets and local data accidentally
