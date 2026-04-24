# Ideas & Planned Features

A scratchpad for features, modes, and improvements being considered for the Vietnamese Learning Quiz. Nothing here is committed to — it's a brainstorm.

## Typing mode (type the Vietnamese)

Reverse-direction practice: the prompt is English, the user types the Vietnamese with full diacritics.

- **Prerequisite:** a Vietnamese keyboard layout installed on the machine.
  - Windows built-in: Settings → Time & language → Language & region → Add Vietnamese → toggle with `Win + Space`.
  - Or install [Unikey](https://www.unikey.org/) — more flexible, lets you pick Telex / VNI / VIQR.
- **Scoring sketch:**
  - ✓ Exact match (with all tones) = correct.
  - ≈ Same letters but wrong or missing tones = "close" with feedback on which tones were off — counts as wrong for progress purposes but educational.
  - ✗ Different letters = incorrect.
- **UX notes:**
  - Show a one-time intro that explains the keyboard requirement and links to setup instructions.
  - Don't auto-play audio on first show (it's a giveaway).
  - Keep `hint` (pronunciation) and `say` (play audio) as on-demand helpers.
  - Consider tracking typing progress separately from recognition progress — knowing what `phở` means and being able to spell it are different skills.

## Listen-only mode

Hide the Vietnamese text, play the audio only, user types the English. Pure ear training — most valuable once a learner has seen each word a couple of times.

- Could be gated to "words you've seen at least twice" to avoid pure guessing.
- Otherwise reuses the existing English-answer flow.

## Other ideas (smaller)

- **Multiple-choice mode** — 4 English options, pick with a single keypress. Lower-friction reps for warming up.
- **Single-keypress menu navigation** — press `d` and go, no Enter (Windows: `msvcrt.getch`).
- **Richer terminal UI** with [`rich`](https://github.com/Textualize/rich) — live progress bar, colored diffs on wrong answers, cleaner menus. Biggest polish jump but adds a dependency.
- **Proper spaced repetition** (Leitner box or SM-2) replacing the current "accuracy < 0.7" weak-words heuristic. Bigger learning gain, more code.
