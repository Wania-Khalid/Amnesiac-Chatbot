import requests
import os
import re


def get_weather(city):
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        return "Weather API not set"

    url = "http://api.weatherapi.com/v1/current.json"
    res = requests.get(url, params={"key": key, "q": city}).json()

    if "error" in res:
        return "City not found"

    return f"{city}: {res['current']['temp_c']}°C, {res['current']['condition']['text']}"


def search_web(query):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return "Search API not set"

    res = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": key, "query": query, "max_results": 3}
    ).json()

    results = res.get("results", [])
    return "\n".join([r["content"][:200] for r in results])


def detect_tool_needed(msg):
    msg = msg.lower()

    if "weather" in msg:
        match = re.search(r"in ([a-zA-Z ]+)", msg)
       
        city = match.group(1) if match else None
        return ("weather", city) if city else ("ask_city", None)

    if "news" in msg or "latest" in msg:
        return ("search", msg)

    return (None, None)