# Jarvis — Personal Voice Assistant

Jarvis is a lightweight personal assistant written in Python. It listens for voice commands, can speak responses, and perform simple tasks (open websites, answer basic questions, etc.). This README explains how to install, run, and troubleshoot Jarvis on a Linux system.

## Features

- Voice input using microphone (SpeechRecognition + PyAudio)
- Text-to-speech responses (pyttsx3)
- Simple command handling (open URLs, respond to queries)
- Keyboard input fallback when microphone or PyAudio are unavailable

## Requirements

- Python 3.8+ (project used in a virtual environment)
- Packages: SpeechRecognition, pyttsx3, pyaudio (or system PyAudio), webbrowser
- System dependencies for audio: PortAudio (libportaudio), PulseAudio/ALSA

## Recommended install (Debian/Ubuntu)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install system audio deps and Python wheel helper:

```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio build-essential libasound2-dev
```

3. Install Python dependencies in your venv:

```bash
pip install --upgrade pip
pip install SpeechRecognition pyttsx3 pyaudio
```

Notes:

- If `python3-pyaudio` is available through apt, it may be easier to install the system package. Otherwise, install `portaudio19-dev` and then `pip install pyaudio`.

## Run Jarvis

From the project folder (`.venv/project2-Jarvis`) with the virtual environment activated:

```bash
python main.py
```

You should see "Jarvis is online." Jarvis will attempt to access your microphone. If the microphone or PyAudio is not available, Jarvis will fall back to keyboard input.

## Usage

- Say or type `jarvis` to activate.
- Try commands such as `open youtube`, `what is your name`, or other commands implemented in `main.py`.

## Troubleshooting

- Error: "Could not find PyAudio; check installation" or `ModuleNotFoundError: No module named 'pyaudio'`

  - Install system package `python3-pyaudio` or install `portaudio19-dev` then `pip install pyaudio` in your venv.

- ALSA / JACK warnings like `jack server is not running` or `unable to open slave`

  - These are usually warnings from the audio backend when PulseAudio/JACK isn't running or no device is present. They are not fatal. Install and configure PulseAudio or ensure your audio interface is available.

- If you run Jarvis on a headless server or in CI where no microphone exists, Jarvis will fall back to keyboard input. You can also run it non-interactively by modifying `main.py` to read commands from a file or network source.

## Development notes

- The `listen()` function in `main.py` attempts to use `sr.Microphone()` and falls back to `input()` if unavailable. You can set `sr.Microphone(device_index=IDX)` to choose a specific device after inspecting `sr.Microphone.list_microphone_names()`.
- To add commands, edit the command handling loop in `main.py`.

## Contribution

Feel free to open issues or submit pull requests. Keep changes small and focused. Document new dependencies and commands in this README.

## License

This project inherits the repository license. See the top-level `LICENSE` file.
