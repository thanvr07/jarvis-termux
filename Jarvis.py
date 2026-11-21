import subprocess
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET

KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-3.5-flash-lite"

LINKS = {
    "whatsapp": "whatsapp://send",
    "chrome": "https://google.com",
    "gmail": "mailto:",
    "maps": "https://maps.google.com",
    "instagram": "https://instagram.com",
    "telegram": "https://t.me",
    "spotify": "https://open.spotify.com",
}

BRAIN_RULES = (
    "You are Jarvis, a voice assistant that only answers questions. "
    "Address the user as sir. Reply in one or two short sentences. "
    "You CANNOT send messages, make calls, set alarms, open apps or control the phone. "
    "Never say you did any action. If the user asks for an action, "
    "say that you cannot do that yet."
)

def speak(words):
    subprocess.run(["termux-tts-speak", words])

def listen():
    return subprocess.getoutput("termux-speech-to-text").lower()

def confirm(question):
    speak(question)
    answer = listen()
    print("Confirm:", answer)
    return "yes" in answer or "yeah" in answer or "confirm" in answer

def ask_gemini(question):
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL + ":generateContent?key=" + KEY
    body = {
        "systemInstruction": {"parts": [{"text": BRAIN_RULES}]},
        "contents": [{"parts": [{"text": question}]}]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "Sorry sir, my brain is not responding right now"

def get_news():
    try:
        with urllib.request.urlopen("https://feeds.bbci.co.uk/news/world/rss.xml", timeout=20) as r:
            root = ET.fromstring(r.read())
        titles = [t.text for t in root.findall("./channel/item/title")][:5]
    except Exception:
        speak("Sorry sir, I could not get the news right now")
        return
    if len(titles) == 0:
        speak("Sorry sir, there are no headlines right now")
        return
    speak("Here are the top world headlines, sir")
    for t in titles:
        print("News:", t)
        speak(t)

def open_app(text):
    for name in LINKS:
        if name in text:
            speak("Opening " + name + ", sir")
            subprocess.run(["termux-open-url", LINKS[name]])
            return True
    return False

def set_alarm(text):
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?", text)
    if not m:
        speak("Sorry sir, I did not catch the time")
        return
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").replace(".", "")
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        speak("Sorry sir, that time is not valid")
        return
    if confirm("Set alarm for %02d:%02d, sir. Say yes to confirm" % (hour, minute)):
        subprocess.run(["am", "start", "-a", "android.intent.action.SET_ALARM",
                        "--ei", "android.intent.extra.alarm.HOUR", str(hour),
                        "--ei", "android.intent.extra.alarm.MINUTES", str(minute),
                        "--ez", "android.intent.extra.alarm.SKIP_UI", "true"])
        speak("Alarm set, sir")
    else:
        speak("Cancelled, sir")

def find_contact(name):
    try:
        contacts = json.loads(subprocess.getoutput("termux-contact-list"))
    except Exception:
        speak("Sorry sir, I could not read your contacts")
        return None
    matches = [c for c in contacts if name in c.get("name", "").lower()]
    if len(matches) == 0:
        speak("Sorry sir, I could not find " + name + " in your contacts")
        return None
    if len(matches) > 1:
        speak("I found more than one contact named " + name + ", sir. Please say the full name")
        return None
    return matches[0]

def call_contact(text):
    name = text.split("call", 1)[1].strip()
    if name == "":
        speak("Whom should I call, sir")
        return
    person = find_contact(name)
    if person is None:
        return
    if confirm("Call " + person["name"] + ", sir. Say yes to confirm"):
        speak("Calling " + person["name"] + ", sir")
        subprocess.run(["termux-telephony-call", person["number"]])
    else:
        speak("Cancelled, sir")

def send_sms(text):
    if " to " not in text:
        speak("Whom should I message, sir")
        return
    name = text.split(" to ", 1)[1].strip()
    person = find_contact(name)
    if person is None:
        return
    speak("What should I say to " + person["name"] + ", sir")
    body = listen().strip()
    print("Message:", body)
    if body == "":
        speak("I did not hear a message, sir. Cancelled")
        return
    if confirm("I will send " + person["name"] + " this message: " + body + ". Say yes to confirm"):
        result = subprocess.run(["termux-sms-send", "-n", person["number"], body],
                                capture_output=True, text=True)
        if result.returncode == 0 and result.stderr.strip() == "":
            speak("I handed the message to your phone, sir. Please check your messages app to be sure")
        else:
            print("SMS error:", result.stderr)
            speak("Sorry sir, sending failed")
    else:
        speak("Cancelled, sir")

speak("Jarvis is ready, sir")

while True:
    text = listen()
    print("You said:", text)

    if text.strip() == "":
        continue

    if "stop" in text or "goodbye" in text:
        speak("Goodbye sir")
        break
    elif "sms" in text or ("message" in text and "send" in text):
        send_sms(text)
    elif text.startswith("call ") or " call " in text:
        call_contact(text)
    elif "alarm" in text:
        set_alarm(text)
    elif "news" in text or "headlines" in text or "going on in the world" in text:
        get_news()
    elif "open" in text and open_app(text):
        pass
    elif "youtube" in text:
        speak("Opening YouTube, sir")
        subprocess.run(["termux-open-url", "https://youtube.com"])
    elif "time" in text:
        now = subprocess.getoutput("date +%I:%M%p")
        speak("The time is " + now + ", sir")
    elif "battery" in text:
        info = json.loads(subprocess.getoutput("termux-battery-status"))
        speak("Battery is at " + str(info["percentage"]) + " percent, sir")
    elif "torch" in text or "flashlight" in text:
        subprocess.run(["termux-torch", "on"])
        speak("Flashlight on, sir")
    elif "music" in text:
        speak("Opening music, sir")
        subprocess.run(["termux-open-url", "https://music.youtube.com"])
    else:
        answer = ask_gemini(text)
        print("Jarvis:", answer)
        speak(answer)
