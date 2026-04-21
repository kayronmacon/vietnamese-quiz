# Vietnamese Learning Quiz

A terminal quiz for learning everyday Vietnamese (Southern accent). ~280 words and phrases across 18 categories, with fuzzy answer matching, automatic audio playback, daily streak tracking, and a weak-words review mode so you can come back day after day.

## Features

- **18 categories**: numbers, addressing people by age, daily phrases, question words, common verbs, adjectives, ordering, food, shopping, family, emotions, body parts, colors, time, weather, places, transportation, directions
- **Auto-play audio** — hear each Vietnamese word when the question appears
- **Fuzzy answer matching** — typos and short variants ("how r u" for "How are you?") still count
- **Daily Practice mode** — auto-mixes weak words with new ones
- **Review Weak Words** — focuses on anything below 70% accuracy
- **Daily streak** tracked across sessions

---

## Setup from scratch (no Python installed yet)

### 1. Install Python

#### Windows
1. Go to [python.org/downloads](https://www.python.org/downloads/) and click the yellow **Download Python** button.
2. Run the installer. **IMPORTANT:** on the first screen, tick the box that says **"Add python.exe to PATH"**, then click **Install Now**.
3. When it finishes, open a new **Command Prompt** (Start menu → type `cmd`) and run:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x`. If not, restart your computer and try again.

#### macOS
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the macOS installer.
2. Run the `.pkg` file and follow the prompts.
3. Open **Terminal** (Spotlight → "Terminal") and run:
   ```
   python3 --version
   ```

#### Linux (Ubuntu / Debian)
```
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Download this app

**Option A — Download as ZIP (easiest):**
1. On this repo's GitHub page, click the green **Code** button → **Download ZIP**.
2. Unzip it wherever you want (e.g. Desktop).

**Option B — If you have git installed:**
```
git clone https://github.com/YOUR-USERNAME/vietnamese-quiz.git
cd vietnamese-quiz
```

### 3. Install the audio libraries

Open a terminal inside the app folder (in Windows: hold Shift + right-click the folder → "Open in Terminal") and run:

```
pip install gTTS pygame
```

On macOS/Linux you may need `pip3` instead of `pip`.

> **Note:** the quiz works without these libraries — you just won't hear audio. If `pip install` fails, skip it and use the quiz silently.

### 4. Run the quiz

From the same terminal, in the app folder:

```
python vietnamese_quiz.py
```

(On macOS/Linux use `python3 vietnamese_quiz.py`.)

You should see the main menu. Pick **d** for Daily Practice and you're off.

---

## In-quiz commands

| Type this | What it does |
|---|---|
| (the English translation) | Submit your answer |
| `hint` | Show the pronunciation guide |
| `say` | Replay the Vietnamese audio |
| `skip` | Skip the question (counts as wrong) |
| `quit` / `menu` | End the quiz early and go back to the main menu |

## Your progress

Your streak, words seen, and accuracy are saved to `vietnamese_progress.json` next to the script. Delete that file to start fresh.

## Updating the app

New words and features get added over time. Here's how to pull them in without losing your streak:

### If you cloned with git
From inside the app folder:
```
git pull
```
Your `vietnamese_progress.json` is ignored by git, so it stays untouched.

### If you downloaded the ZIP
1. **Save your progress file first.** Copy `vietnamese_progress.json` out of the app folder (to your Desktop, say).
2. Re-download the latest ZIP from the repo's GitHub page → **Code** → **Download ZIP**.
3. Unzip it, replacing the old folder.
4. Copy your saved `vietnamese_progress.json` back into the new folder.

> **Tip:** If you plan to update often, cloning with git is much easier — one `git pull` and you're current.

### After updating
If a new version adds new audio dependencies or libraries, re-run:
```
pip install -r requirements.txt
```
(If there's no `requirements.txt`, just re-run `pip install gTTS pygame` to make sure you're current.)

## Troubleshooting

- **"No audio plays"** — make sure you ran `pip install gTTS pygame` for the same Python you're running the script with. gTTS also needs an internet connection to fetch audio. If you see an error message when you type `say`, it will tell you what went wrong.
- **"'python' is not recognized"** (Windows) — you missed the "Add to PATH" checkbox during install. Reinstall Python and tick it, or try `py vietnamese_quiz.py` instead.
- **Unicode / diacritics look broken in the terminal** — use Windows Terminal, iTerm, or any modern terminal instead of the legacy Windows Console.
