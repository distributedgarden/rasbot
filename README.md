# Description
Bot

# OS Dependencies
## Raspberry Pi OS "Bookworm" (Ubuntu)
### apt
```
> sudo apt update
> sudo apt install portaudio19-dev ffmpeg alsa-utils

# confirm the microphone and speaker are detected
> arecord -l     # microphone 
> aplay -l       # speaker

# speaker volume
> alsamixer
```
- `portaudio19-dev`: `pyaudio` dependency.
- `ffmpeg`: play mp3's.
- `alsa-utils`: audio control package.

### .bashrc
Add your OpenAI API key
```
OPENAI_API_KEY="..."
```

# Run Speech POC
```
> cd rasbot

> python3 -m venv env
> source env/bin/activate
> python3 -m pip install -r requirements.txt

> python3 scripts/poc_speech.py
```