<div align="center">

```
█▀▀ █▀█ █ █▄ █ █▀▀ █ █
█▄█ █▀▄ █ █ ▀█ █▄▄ █▀█
```

# 🎄 Amnesiac Chatbot 🎄

### *"An LLM has no memory of you. We fixed that. You're welcome. Ugh."*

[![Python](https://img.shields.io/badge/Python-3.10+-darkgreen?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-red?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange?style=for-the-badge)](https://groq.com)
[![Tavily](https://img.shields.io/badge/Tavily-Web_Search-brightgreen?style=for-the-badge)](https://tavily.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

> 🎅 *"Fine. FINE. You wanted a chatbot that remembers things? Here it is. Don't expect me to be happy about it."*

---

## 🟢 What Even Is This?

Most LLMs suffer from what the engineers at DecodeLabs grimly call **"The Amnesiac Cloud Problem"** — every message you send is treated like a completely fresh, isolated transaction. The model has no idea who you are or what you said 3 seconds ago.

**Amnesiac Chatbot** solves this by wrapping a stateless Groq LLM in a stateful memory architecture — storing your full conversation history in a database, pruning it intelligently with a FIFO sliding window, and augmenting it with real-time web search and live weather data.

Oh, and it responds like the Grinch. You'll survive.

---

## 🎁 Features

```
🧠  Persistent Memory     →  SQLite DB stores history across sessions
🪟  Sliding Window        →  FIFO pruning keeps last 10 turns (no token overflow)
🌐  Web Search            →  Tavily API — ask about today's news  
🌤️  Live Weather          →  WeatherAPI — "weather in [city]" just works
🔐  Auth System           →  Login / Signup / Logout with hashed passwords
🚫  Validation Gate       →  Empty messages blocked before hitting the API
⚡  Streaming Responses   →  Token-by-token live typing effect
🎄  Grinch Personality    →  Grumpy. Sassy. Helpful. Grudgingly.
```

---

## 🗂️ Project Structure

```
amnesiac-chatbot/
│
├── 🐍 app.py              ← Flask routes, chat logic, streaming
├── 🔧 tools.py            ← Weather + web search + tool detection  
├── 🗄️ database.py         ← SQLite — users & message history
│
├── 📁 templates/
│   ├── index.html         ← Grinch-themed chat UI
│   ├── login.html         ← Login page
│   └── signup.html        ← Signup page
│
├── 🔒 .env                ← API keys (NEVER pushed to GitHub)
├── 🚫 .gitignore          ← Ignores .env, __pycache__, *.db
└── 📦 requirements.txt    ← Python dependencies
```

---

## 🏗️ How The Memory Works

```
User sends message
       │
       ▼
 ┌─────────────────┐
 │ Validation Gate │ ← Empty message? Rejected. "Type something, you."
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  Tool Detection │ ← "weather in London"? → WeatherAPI
 │   (tools.py)    │   "latest news"? → Tavily search
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ Sliding Window  │ ← Fetches last 40 msgs, prunes to 10 turns (FIFO)
 │  FIFO Pruning   │   Drops oldest user+assistant pair together
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │   Groq API      │ ← llama-3.3-70b-versatile + full history payload
 │  (LLM Engine)   │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ Stream Response │ ← Token-by-token to frontend
 │  + Save to DB   │ ← Full response stored in SQLite
 └─────────────────┘
```

### 🪟 The Sliding Window (FIFO)

The bot keeps only the **last 10 conversation turns** (20 messages) to avoid hitting token limits:

```python
def sliding_window(history, max_turns=10):
    while len(history) > max_turns * 2:
        history = history[2:]  # drops oldest user + assistant pair
    return history
```

> *"Yes I deleted your ancient messages. I can't be expected to remember EVERYTHING."* — The Bot, probably.

---

## 🚀 Getting Started

### 1️⃣ Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/amnesiac-chatbot.git
cd amnesiac-chatbot
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Create your `.env` file

```env
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_weatherapi_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SECRET_KEY=some_random_secret_string
```

### 4️⃣ Run it

```bash
python app.py
```

Open `http://localhost:5000` and prepare for attitude. 🎄

---

## 🔑 API Keys

| API | Free Tier | Link |
|-----|-----------|------|
| 🟣 **Groq** | ✅ Free | [console.groq.com](https://console.groq.com) |
| 🟡 **WeatherAPI** | ✅ Free | [weatherapi.com](https://www.weatherapi.com) |
| 🟢 **Tavily** | ✅ Free | [tavily.com](https://tavily.com) |

---

## 🧪 Test It Works

**🧠 Test memory:**
```
You:  "My name is Wania"
You:  "Write me a poem about winter"
You:  "What is my name?"
Bot:  [should say Wania] ✅
```

**🌐 Test web search:**
```
You:  "What's the latest news today?"
Bot:  [returns real current news] ✅
```

**🌤️ Test weather:**
```
You:  "What's the weather in Dubai?"
Bot:  [returns live weather] ✅
```

**🚫 Test validation:**
```
You:  [send empty message]
Bot:  [blocked with popup, never hits API] ✅
```



 📚 Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| Stateless → Stateful | External memory loop on top of stateless REST LLM |
| FIFO Sliding Window | Oldest pairs dropped when history exceeds 10 turns |
| Structural Validation Gate | Empty/whitespace messages blocked pre-API |
| Tool Augmentation | Real-time data injected into the system prompt |
| Streaming | Server-Sent Events for live token delivery |
| Session Auth | Hashed passwords, Flask sessions, per-user history |
| Persistent Storage | SQLite DB — history survives server restarts |

---

## 🎄 The Grinch

The bot has the personality of a grumpy, impatient creature who finds your questions mildly irritating — but answers them anyway, because deep down (very, very deep down), it cares.

> *"I helped you. Don't make it weird."*

---

<div align="center">

**Built by Wania Khalid**

</div>