# Jarvis for Termux

An open-source voice assistant for Android, built with Termux, Termux:API and the Gemini API.

## What it can do

- Listen to your voice and speak back
- Answer questions using Gemini
- Set alarms (asks you to confirm first)
- Call contacts (asks you to confirm first)
- Send SMS (reads the message back and asks you to confirm first)
- Read world headlines from the BBC RSS feed
- Open Chrome, Gmail, Maps and WhatsApp using links
- Tell the time and battery level, and turn on the flashlight

## What it cannot do

- No "Hey Jarvis" wake word. You start it by typing `jarvis` in Termux.
- Cannot read or reply to emails.
- Does not work while a call or online class is using the microphone.
- Does not have full control of the phone. Android blocks that on purpose.
- Gemini only answers questions. All real actions come from code in this file.

## Requirements

- Android phone
- Termux and Termux:API, both installed from F-Droid
- A free Gemini API key from Google AI Studio

## Setup

1. Install Termux and Termux:API from F-Droid.
2. In Termux run: `pkg install python termux-api curl`
3. Allow microphone, contacts, phone and SMS permissions for Termux:API.
4. Save your API key as an environment variable named `GEMINI_API_KEY` in `~/.bashrc`.
5. Download `jarvis.py` and run: `python jarvis.py`

## Safety

- Your API key is never stored in the code. Never upload it to GitHub.
- Calls, SMS and alarms always ask for confirmation.
- Anything Jarvis does not recognise is sent to Google's Gemini servers. Do not say passwords or private details.
- Never trust an AI saying an action is done. Check your messages app or clock yourself.

## Known issues

- Model names change. If answers fail, update the `MODEL` line.
- Some phones, such as Xiaomi, block apps from opening other apps.

## License

MIT
