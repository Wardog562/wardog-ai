import streamlit as st
from openai import OpenAI
import json
import os
import speech_recognition as sr
import requests

# --- SET THIS: Your OpenRouter API Key securely via Streamlit secrets ---
API_KEY = st.secrets["OPENAI_API_KEY"]
# ------------------------------------------------------------------------

client = OpenAI(api_key=API_KEY)

# Voice input only (optional)
def listen():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as mic:
            audio = r.listen(mic)
        return r.recognize_google(audio)
    except Exception:
        return ""

# Memory file
MEMORY_PATH = "wardog_memory.json"
if os.path.exists(MEMORY_PATH):
    with open(MEMORY_PATH, "r") as f:
        memory = json.load(f)
else:
    memory = []

# Streamlit layout
st.set_page_config(page_title="Wardog AI", layout="centered")
st.title("🐺 Wardog AI Assistant")
if "chat" not in st.session_state:
    st.session_state.chat = []

def add_to_memory(role, content):
    memory.append({"role": role, "content": content})
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def call_gpt(prompt, memory, user_input):
    messages = memory + [{"role": "user", "content": prompt + user_input}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return resp.choices[0].message["content"]

# UI components
st.sidebar.title("🎧 Wardog Settings")
if st.sidebar.button("Clear Memory"):
    memory.clear()
    open(MEMORY_PATH, "w").write("[]")
    st.sidebar.success("Memory cleared!")

if st.sidebar.button("Listen (Voice Input)"):
    st.session_state.user_input = listen()
    st.experimental_rerun()

user_input = st.chat_input("Talk to Wardog...")

if user_input:
    # Commands
    cmd = user_input.strip().lower()
    if cmd.startswith("!verse"):
        verse = requests.get("https://bible-api.com/john 3:16").json().get("text", "")
        reply = f"📖 Here's your verse:\n> {verse}"
    elif cmd.startswith("!pray"):
        reply = "🙏 Lord, guide and strengthen you today..."
    elif cmd.startswith("!gymtip"):
        reply = "💪 Make sure to squat deep and rest!"
    elif cmd.startswith("!meme"):
        reply = "😂 Imagine a bear doing bicep curls with a salmon."
    else:
        reply = call_gpt("You are Wardog, a gym–God–loving, Gen Z AI: ", memory, user_input)

    st.session_state.chat.append(("You", user_input))
    st.session_state.chat.append(("Wardog", reply))
    add_to_memory("user", user_input)
    add_to_memory("assistant", reply)

# Display chat
for sender, message in st.session_state.chat:
    with st.chat_message(sender):
        st.markdown(message)
