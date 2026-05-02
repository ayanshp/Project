from __future__ import annotations

import base64
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*").split(",")}})

MOOD_MUSIC: Dict[str, List[Dict[str, str]]] = {
    "happy": [
        {"title": "Happy", "artist": "Pharrell Williams", "mood": "happy"},
        {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake", "mood": "happy"},
        {"title": "Uptown Funk", "artist": "Bruno Mars", "mood": "happy"},
        {"title": "Good as Hell", "artist": "Lizzo", "mood": "happy"},
        {"title": "Shake It Off", "artist": "Taylor Swift", "mood": "happy"},
    ],
    "sad": [
        {"title": "Someone Like You", "artist": "Adele", "mood": "sad"},
        {"title": "The Night We Met", "artist": "Lord Huron", "mood": "sad"},
        {"title": "Skinny Love", "artist": "Bon Iver", "mood": "sad"},
        {"title": "Fix You", "artist": "Coldplay", "mood": "sad"},
        {"title": "Hurt", "artist": "Johnny Cash", "mood": "sad"},
    ],
    "angry": [
        {"title": "Break Stuff", "artist": "Limp Bizkit", "mood": "angry"},
        {"title": "Killing in the Name", "artist": "Rage Against the Machine", "mood": "angry"},
        {"title": "Bodies", "artist": "Drowning Pool", "mood": "angry"},
        {"title": "Numb", "artist": "Linkin Park", "mood": "angry"},
        {"title": "Break the Rules", "artist": "Charli XCX", "mood": "angry"},
    ],
    "surprised": [
        {"title": "Bohemian Rhapsody", "artist": "Queen", "mood": "surprised"},
        {"title": "Superstition", "artist": "Stevie Wonder", "mood": "surprised"},
        {"title": "Mr. Brightside", "artist": "The Killers", "mood": "surprised"},
        {"title": "Jump", "artist": "Van Halen", "mood": "surprised"},
        {"title": "Africa", "artist": "Toto", "mood": "surprised"},
    ],
    "fearful": [
        {"title": "Weightless", "artist": "Marconi Union", "mood": "fearful"},
        {"title": "Clair de Lune", "artist": "Debussy", "mood": "fearful"},
        {"title": "Experience", "artist": "Ludovico Einaudi", "mood": "fearful"},
        {"title": "Teardrop", "artist": "Massive Attack", "mood": "fearful"},
        {"title": "Mad World", "artist": "Gary Jules", "mood": "fearful"},
    ],
    "disgusted": [
        {"title": "Bad Guy", "artist": "Billie Eilish", "mood": "disgusted"},
        {"title": "Seven Nation Army", "artist": "White Stripes", "mood": "disgusted"},
        {"title": "Radioactive", "artist": "Imagine Dragons", "mood": "disgusted"},
        {"title": "Pumped Up Kicks", "artist": "Foster the People", "mood": "disgusted"},
        {"title": "Hate That I Love You", "artist": "Rihanna", "mood": "disgusted"},
    ],
    "neutral": [
        {"title": "Blinding Lights", "artist": "The Weeknd", "mood": "neutral"},
        {"title": "Levitating", "artist": "Dua Lipa", "mood": "neutral"},
        {"title": "Watermelon Sugar", "artist": "Harry Styles", "mood": "neutral"},
        {"title": "Golden Hour", "artist": "JVKE", "mood": "neutral"},
        {"title": "As It Was", "artist": "Harry Styles", "mood": "neutral"},
    ],
}
EMOTION_KEYS = list(MOOD_MUSIC.keys())


def _rid() -> str:
    return str(uuid.uuid4())


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _songs(emotion: str, count: int) -> List[Dict[str, str]]:
    base = MOOD_MUSIC.get(emotion, MOOD_MUSIC["neutral"])
    count = max(1, min(int(count or 5), 20))
    return base[:count]


def _classify_text(text: str) -> tuple[str, int]:
    t = text.lower().strip()
    rules = [
        ("happy", r"\b(happy|joy|great|awesome|excited|good|amazing|love)\b"),
        ("sad", r"\b(sad|down|depressed|cry|lonely|heartbroken|upset)\b"),
        ("angry", r"\b(angry|mad|furious|annoyed|rage|irritated)\b"),
        ("fearful", r"\b(anxious|anxiety|scared|fear|nervous|stressed|overwhelmed)\b"),
        ("surprised", r"\b(surprised|shocked|wow|unexpected|astonished)\b"),
        ("disgusted", r"\b(disgust|gross|nasty|revolting)\b"),
    ]
    for emo, pat in rules:
        if re.search(pat, t):
            return emo, 84
    return "neutral", 72


def _classify_image_demo(image_b64: str) -> tuple[str, int]:
    ln = len(image_b64 or "")
    emo = EMOTION_KEYS[ln % len(EMOTION_KEYS)]
    conf = 70 + (ln % 21)  # 70..90
    return emo, conf


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "request_id": _rid(), "timestamp": _ts()}), 200


@app.post("/api/emotion-from-text")
def emotion_from_text():
    rid = _rid()
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    song_count = payload.get("song_count", 5)

    if not text:
        return jsonify({"error": "text is required", "request_id": rid}), 400

    emotion, confidence = _classify_text(text)
    return jsonify(
        {
            "emotion": emotion,
            "confidence": confidence,
            "songs": _songs(emotion, song_count),
            "request_id": rid,
            "timestamp": _ts(),
        }
    ), 200


@app.post("/api/detect-emotion")
def detect_emotion():
    rid = _rid()
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    image = payload.get("image", "")
    song_count = payload.get("song_count", 5)

    if not image:
        return jsonify({"error": "image is required (base64)", "request_id": rid}), 400

    try:
        raw = image.split(",", 1)[1] if isinstance(image, str) and image.startswith("data:") else image
        base64.b64decode(raw, validate=True)
    except Exception:
        return jsonify({"error": "invalid base64 image payload", "request_id": rid}), 400

    emotion, confidence = _classify_image_demo(raw)
    return jsonify(
        {
            "emotion": emotion,
            "confidence": confidence,
            "songs": _songs(emotion, song_count),
            "request_id": rid,
            "timestamp": _ts(),
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
