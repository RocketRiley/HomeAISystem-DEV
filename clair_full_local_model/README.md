# Clair Local Model

Welcome to the **Clair Local Model**.  This bundle contains all of the
configuration files, personas, and demonstration scripts needed to run
Clair offline on your own computer.  Clair is a friendly and extremely
smart digital assistant who lives in Texas (with a neutral American
accent) and excels at robotics, biology, science, and history.  She
remembers your conversations, keeps track of her own moods, and can
proactively engage when something interesting happens at home.

## Contents

```
clair_full_local_model/
├── README.md               – this file
├── .env.example            – example environment configuration
├── requirements.txt        – Python dependencies for the demo scripts
├── persona/                – Clair's persona description and example lines
│   ├── persona_clair.json  – meta description of Clair
│   └── examples/           – example utterances grouped by state
├── emotion_pack/           – emotion, trait and relationship definitions
│   ├── emotions.json       – 50 immediate emotions
│   ├── traits.json         – 20 long‑term traits
│   ├── client_modifiers.json – 30 per‑person modifiers
│   └── config.json         – weights, TTS mapping and mode offsets
├── config/                 – state machine and initiator rules
│   ├── state_machine.json  – defines awake/sleep/DND states
│   ├── initiator_rules.json – rules for proactive behaviour
│   ├── opinions.json        – stored opinions about various topics
│   ├── memory.json          – episodic memory log
│   ├── contacts.json        – per‑person relationship store
│   ├── calendar_events.json – sample external calendar data
│   ├── clair_calendar.json – Clair’s personal calendar (auto‑generated)
│   ├── user_calendar.json – your personal calendar (auto‑generated)
│   └── tasks.json           – simple to‑do list
└── scripts/                – demo and stub programs
    ├── pad_demo.py         – shows how emotions map to PAD and TTS
    ├── osc_bridge_stub.py  – example OSC bridge to your VRM model
    ├── self_initiation.py  – simulates proactive events
    ├── speech_loop_stub.py – command line conversation loop with memory, contacts, tasks and calendar support
    ├── music_player.py    – opens YouTube for music playback
    ├── vision_watch_stub.py – simulated TV/show watcher
    ├── audio_interest_stub.py – simulated attention triggers
    ├── voice_loop_stub.py  – outline for a real wake‑word + STT + TTS loop
    ├── daily_rollup.py     – generate a daily memory summary (roll‑up)
    ├── status_board.py     – display a mini dashboard of tasks, calendar, mood and contact feelings
    ├── opinion_system.py   – opinion storage and update logic
    ├── filter_system.py    – content filtering pipeline
    ├── memory_manager.py   – episodic memory API
    ├── contact_manager.py  – per‑person relationship API
    ├── tasks_manager.py    – simple to‑do list API
    ├── calendar_integration_stub.py – stub calendar integration
    ├── personal_calendar_manager.py – manages Clair’s and the user’s own calendars
    ├── llm_adapter.py       – optional online LLM adapter
    ├── ui_launcher.py      – graphical launcher and settings panel
    └── task stub and helper modules used by the above
```

## Getting started

1. **Install Python** – Clair’s demonstration scripts require Python 3.8 or
   higher.  Make sure Python and pip are installed on your system.

2. **Create a virtual environment** (optional but recommended):

   ```bash
   cd clair_full_local_model
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:  The provided `requirements.txt` lists a
   minimal set of libraries used by the demonstration scripts.  Install
   them with:

   ```bash
   pip install -r requirements.txt
   ```

   These requirements include `python-osc` and `websockets` for the OSC
   bridge and event bus.  Additional packages such as local speech
   recognition (e.g. [openWakeWord](https://github.com/dylansden/openWakeWord) and [faster‑whisper](https://github.com/guillaumekln/faster-whisper)) and local
   speech synthesis (e.g. [Piper](https://github.com/rhasspy/piper) or
   [XTTS](https://github.com/coqui-ai/TTS)) are optional and not
   automatically installed.  See the comments in `speech_loop_stub.py` for
   tips on integrating those libraries.

4. **Configure environment**:  Copy `.env.example` to `.env` and edit
   the values to suit your setup.  At minimum you should set
   `OSC_HOST` and `OSC_PORT` if you plan to drive your VRM avatar via
   the OSC bridge.

5. **Set a content filter (optional)**:  Clair can self‑censor her
   responses according to various moderation levels.  To change the
   filter, edit your `.env` file and set the `FILTER_LEVEL` variable
   to one of the following values:

   - `twitch` – strictest filtering, aligned with Twitch's terms of service
   - `pg13`  – roughly PG‑13 movie rating
   - `enabled` – default, moderate filtering suitable for general audiences
   - `adult` – minimal filtering; some heavy profanity is still softened
   - `dev0` – no filtering at all

   If `FILTER_LEVEL` is not set or is invalid, Clair defaults to
   `enabled`.  See `scripts/filter_system.py` for details about what
   each level does.

   ```bash
   cp .env.example .env
   # then edit .env with your preferred settings
   ```

5. **Use memory, contacts and tasks**:  Clair keeps track of your
   conversations and your to‑dos locally.  The `speech_loop_stub.py`
   script automatically logs every user message to
   `config/memory.json`.  You can view recent events or summarise a
   day using the `memory last` and `memory summary` commands within
   the loop.  To generate a daily roll‑up for yesterday (or a
   specific date) without running the whole loop, call:

   ```bash
   python scripts/daily_rollup.py          # summarise yesterday
   python scripts/daily_rollup.py 2025-08-24  # summarise a specific date
   ```

   Per‑person relationship data is stored in
   `config/contacts.json`; update it with the `contact update`
   command.  Clair adjusts her tone based on these feelings: high
   valence and trust make her warmer and more playful, while lower
   scores make her more formal or assertive.  This affects the
   underlying mood and, ultimately, which example lines she chooses.

   A simple to‑do list lives in `config/tasks.json` – add
   tasks with `task add <due YYYY-MM-DD> <description>`.  When
   you add a task, Clair will automatically schedule it in her
   personal calendar on the due date at 09:00 (you can reschedule
   later via `calendar add`).  Mark tasks done with `task done <id>`,
   and list tasks with `task list [completed|incomplete]`.

   You can also view a summary of your current state at any time by
   running `python scripts/status_board.py` or by typing `status`
   inside the conversation loop.  The status board shows the active
   filter level, a simple mood estimate, the next calendar event,
   upcoming tasks within three days, and your relationship metrics.

   You can also create your own calendar events with
   `calendar add <clair|user> <date YYYY-MM-DD> <start HH:MM> <end HH:MM> <title>`.
   Clair maintains two personal calendars (one for herself and one
   for you) in `config/clair_calendar.json` and
   `config/user_calendar.json`.  The `calendar next` and
   `calendar day` commands combine personal and external events so
   you always know what’s coming up.

   For a bit of fun, try `music play <search terms>` inside the loop.
   Clair will open a YouTube search page for your query (or the URL
   if you provide one) so you can listen to music while working.

6. **Run the PAD demo**:  To see how emotions map to the PAD
   (Pleasure–Arousal–Dominance) space and TTS prosody, run:

   ```bash
   python scripts/pad_demo.py
   ```

   This script loads the emotion definitions from `emotion_pack/` and
   prints the evolving PAD values and suggested speech parameters.

7. **Test the OSC bridge**:  If your VRM model (e.g. in VSeeFace) is
   listening for OSC messages, start the bridge:

   ```bash
   python scripts/osc_bridge_stub.py
   ```

   The script will read your `.env` file and periodically send simple
   Joy/Angry/Sorrow/Fun values based on a sine wave.  You can modify
   the code to drive the VRM model with real PAD data.

8. **Experiment with proactive events**:  The `self_initiation.py`
   script shows how Clair can initiate interactions.  It reads
   `config/initiator_rules.json` and fires simulated events (for
   vision, audio, time and memory) to produce example utterances.  Run
   it with:

   ```bash
   python scripts/self_initiation.py
   ```

9. **Try a simple speech loop**:  Although a full local voice
   pipeline requires external models, the `speech_loop_stub.py` lets
   you type messages and see Clair respond in character.  It
   demonstrates state transitions (awake, sleep) and chooses reply
   lines based on emotional context.  Start it with:

   ```bash
   python scripts/speech_loop_stub.py
   ```

   While chatting you can use several commands:

   - `sleep`/`wake` – switch between awake and sleep modes.  In sleep
     mode Clair ignores all input except `wake`.
   - `set filter <level>` – change the output filter level on the fly
     (see *Set a content filter* above for available levels).
   - `opinion show <topic>` – print Clair’s current stance and
     confidence on a topic.
   - `opinion update <topic> <direction> <strength> <trust> <reason>` –
     nudge Clair’s opinion on a topic.  Direction, strength and trust
     are numbers between 0 and 1 (direction may be negative to
     indicate opposing evidence).  The reason is free‑text and will
     be logged.

   The stub does not integrate STT/TTS; it simply uses the terminal
   for demonstration.  For a complete voice pipeline, replace the
   placeholders in this script with calls to local speech
   recognition/tts libraries.

10. **Launch the graphical interface**:  For a point‑and‑click
    experience, run:

    ```bash
    python scripts/ui_launcher.py
    ```

    This opens a simple user interface where you can toggle **Online
    Mode** (to use OpenAI’s chat models), enable or disable Clair’s
    **self‑start** behaviour, choose a **content filter** level, enter
    your `OPENAI_API_KEY`, and launch the chat loop.  The settings are
    saved to `.env` so that they persist across runs.  You can also play
    music by entering a search term; Clair will open a YouTube search in
    your default browser.

    When you package this project as an application (see below), the
    launcher makes it behave like any other program on your PC.

11. **Run the voice loop (optional)**:  If you have installed
    `openWakeWord` for wake‑word detection, `faster‑whisper` for speech
    recognition, and `piper` or `xtts` for speech synthesis, you can try
    the voice‑driven loop.  The `voice_loop_stub.py` demonstrates how
    to wire these components together.  It waits for a wake word,
    records speech, transcribes it, and speaks a reply.  It uses
    placeholders for STT and TTS if those packages are not available.
    Run it with:

    ```bash
    python scripts/voice_loop_stub.py
    ```

    Before running, set the environment variables `WAKE_WORD_MODEL`
    (path to a `.tflite` model), `PIPER_VOICE` (path to a piper voice
    model) and optionally `PIPER_RATE` to control speech speed.  See
    the comments in `voice_loop_stub.py` for guidance on integrating
    your preferred STT and TTS engines.

### Enabling Online Mode (optional)

By default Clair runs completely offline, choosing responses from her
persona example files.  If you prefer, you can have Clair call an
online large language model in the same way that ChatGPT or Gemini
does.  To enable this **online mode**, set the environment variable
`ONLINE_MODE=true` (either in your `.env` file or via the GUI).

You must also supply an API key for the model provider; Clair uses
OpenAI’s API by default.  Set `OPENAI_API_KEY` in your `.env` or
enter it in the GUI.  You can optionally set `OPENAI_MODEL` to choose
a particular model (e.g. `gpt-3.5-turbo`).

When online mode is enabled and an API key is present, Clair sends
the latest user message along with a system prompt containing her
persona description to the OpenAI Chat API and uses the returned
reply instead of selecting a local example.  The call is made via the
`openai` Python library and is similar to the example shown in the
OpenAI developer documentation【940982572174291†L29-L60】.  If anything goes
wrong (no key, network failure, or disabled online mode), Clair will
fall back to her local examples automatically.

Online mode is disabled by default because it requires an internet
connection and consumes API credits.  Use it when you want Clair to
provide rich, generative responses beyond the curated examples.

### Packaging into an installer

To distribute Clair as a standalone desktop program, you can bundle it
into a single executable using [PyInstaller](https://pyinstaller.org/).
PyInstaller takes your Python scripts, their dependencies and the
Python interpreter itself, and produces a platform‑specific binary
(e.g. an `.exe` for Windows or an `.app` for macOS).  The Real Python
guide notes that PyInstaller “packages up your Python code into a
single folder or file that you can distribute to users, complete with
an embedded Python interpreter, so they don’t need to install Python
separately”【150485653265271†L170-L186】.

To create a GUI application from Clair, install PyInstaller (`pip
install pyinstaller`) and then run:

```bash
pyinstaller --onefile --windowed scripts/ui_launcher.py
```

The `--onefile` flag produces a single executable and `--windowed`
suppresses the console window on Windows and macOS.  After the build
completes, you will find the executable in the `dist/` directory.
You can double‑click this file to launch Clair’s GUI on your system.

For Linux you may omit `--windowed` or adjust options as needed.
PyInstaller generates platform‑specific executables, so you must run
the build on each target OS (Windows builds cannot be created on
Linux, for example).  See the PyInstaller documentation for more
advanced options such as custom icons and installers.

## Expanding the kit

This bundle is a starting point.  To create a fully fledged assistant:

- Populate the `persona/examples/` directory with many more example
  utterances per state.  The current files provide a handful of
  lines; you can add hundreds of lines in each state to diversify
  Clair’s speech.  Each file should contain a JSON array of strings.
- Adjust the weights and PAD mappings in `emotion_pack/config.json`
  to tune how quickly emotions rise and fall, and how they influence
  tone and mood.
- Define additional states in `config/state_machine.json` if you need
  finer control (e.g. an “intox” mode or separate “stream” mode).
- Implement real vision/audio integrations by replacing the stub code
  with calls into your camera feed, TV screen analysis or speech
  recognizer.  The rules in `config/initiator_rules.json` are designed
  to be human‑readable and easy to extend.
- When you are ready to add streaming features, integrate EventSub and
  IRC into the `self_initiation.py` logic.  For purely local use,
  those are disabled by default.

In addition, consider extending Clair’s personal assistant skills:

- **Richer memory summarisation**:  Replace the naive summariser in
  `memory_manager.py` with an embedding‑based retrieval and large
  language model to produce character‑aware daily digests.  The
  provided `daily_rollup.py` script uses this summariser to
  collate events for a given day; schedule it each evening (e.g. via
  cron) to generate digest files and have Clair review them with you
  the next morning.
- **Custom task workflows**:  Expand `tasks_manager.py` to handle
  recurring tasks, reminders, and deeper integration with your
  calendar.  Add hooks to `self_initiation.py` so that overdue or
  high‑priority tasks trigger proactive pings and check‑ins.
- **Deeper contact modelling**:  Use the data captured in
  `contacts.json` to personalise Clair’s responses.  At present the
  `speech_loop_stub.py` biases the mood values based on valence,
  trust and familiarity.  You can extend this by mapping those
  feelings into preferences for particular example sets (e.g. more
  supportive and playful with high‑trust contacts, more formal or
  focused with low‑trust ones).

We hope you enjoy building with Clair – a smart, kind and curious
digital companion who lives on your own machine.