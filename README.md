# Description
Conversational LLM-based tool-using agent with a robot chassis, sensors for vision and audio, actuators for motion and audio.

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
```
# Add OpenAI API Key
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

# Run Vision POC
```
> cd rasbot

> python3 -m venv env
> source env/bin/activate
> python3 -m pip install -r requirements.txt

> python3 scripts/poc_vision.py
```
## mediapipe
- `http://<RPi IP>:5000/capture_mediapipe`

## OpenCV
- `http://<RPi IP>:5000/download_files`: dependencies for Haar Cascades object recognition
- `http://<RPi IP>:5000/capture_haar`

# Run Motor POC
```
> cd rasbot

> python3 -m venv env
> source env/bin/activate
> python3 -m pip install -r requirements.txt

> python3 scripts/poc_motor.py
```

# Hardware
- Raspberry Pi 4 Model B - 2GB RAM: https://www.adafruit.com/product/4292
    - v4 or v5 will work.
    - 2GB-8GB RAM will work -- 435Mi used.
- SanDisk 128GB Ultra USB 3.0 Flash Drive
    - ~20% used.
- Pi Camera Module 3: https://www.adafruit.com/product/5657
- Mini External USB Stereo Speaker: https://www.adafruit.com/product/3369
- Mini USB Microphone: https://www.adafruit.com/product/3367
- Adafruit CRICKIT HAT: https://www.adafruit.com/product/3957
- Mini 3-Layer Round Robot Chassis Kit: https://www.adafruit.com/product/3244
- Anker PowerCore Select 10000 Portable Charger: https://www.walmart.com/ip/Anker-PowerCore-Select-10000-Portable-Charger-Black-Ultra-Compact-High-Speed-Charging-Technology-Phone-Charger-for-iPhone-Samsung-and-More/211593977