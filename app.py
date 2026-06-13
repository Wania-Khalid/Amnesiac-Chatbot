from groq import Groq
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, session, redirect, url_for, jsonify
from database import (
    init_db, create_user, verify_user,
    save_message, get_messages, clear_messages
)
from tools import get_weather, search_web, detect_tool_needed
import os
from datetime import datetime

# ───────── Setup ─────────
load_dotenv()
init_db()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "grinch-secret")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ───────── Sliding Window (FIFO) ─────────
MAX_HISTORY_TURNS = 10  # 10 pairs = 20 messages max sent to the API

def sliding_window(history, max_turns=MAX_HISTORY_TURNS):
    """
    PDF requirement: FIFO pruning.
    Drops oldest user+assistant pairs from the front
    when history exceeds the turn limit.
    Always drops in pairs to keep role alignment intact.
    """
    while len(history) > max_turns * 2:
        history = history[2:]  # drop oldest user + assistant pair together
    return history


# ───────── Helpers ─────────
def logged_in():
    return "user_id" in session


# ───────── Pages ─────────
@app.route("/")
def home():
    if not logged_in():
        return redirect(url_for("login"))

    messages = get_messages(session["user_id"], limit=50)

    return render_template(
        "index.html",
        username=session.get("username"),
        messages=messages or []
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = verify_user(username, password)

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))
        else:
            error = "Invalid login"

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            error = "Passwords do not match"
        elif len(password) < 6:
            error = "Password too short"
        else:
            if create_user(username, password):
                return redirect(url_for("login"))
            else:
                error = "User already exists"

    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ───────── Chat ─────────
@app.route("/chat", methods=["POST"])
def chat():
    if not logged_in():
        return jsonify({"error": "not logged in"}), 401

    user_input = request.json.get("message", "")

    # ── Structural Validation Gate (PDF requirement) ──
    if not user_input or not user_input.strip():
        return jsonify({"error": "empty message"}), 400

    user_id = session["user_id"]

    save_message(user_id, "user", user_input)

    # ── Fetch more than needed, then apply FIFO sliding window ──
    raw_history = get_messages(user_id, limit=40)
    history = sliding_window(raw_history)

    tool_name, tool_arg = detect_tool_needed(user_input)
    tool_result = ""

    if tool_name == "weather":
     if tool_arg:
        tool_result = get_weather(tool_arg)
     else:
        # No city detected, ask the user
        return Response("Which city's weather do you want, you nosy little elf? 🎄", mimetype="text/plain")
    elif tool_name == "search":
     tool_result = search_web(tool_arg)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    system_prompt = f"""You are a grumpy but helpful AI assistant.

Time: {now}
User: {session.get("username")}

Use tool data if provided:
{tool_result}"""

    messages = [{"role": "system", "content": system_prompt}] + history

    def generate():
        full = ""

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta.content or ""
                full += delta
                yield delta

        save_message(user_id, "assistant", full)

    return Response(generate(), mimetype="text/plain")


@app.route("/clear", methods=["POST"])
def clear():
    if logged_in():
        clear_messages(session["user_id"])
    return jsonify({"ok": True})


# ───────── Run ─────────
if __name__ == "__main__":
    app.run(debug=True)