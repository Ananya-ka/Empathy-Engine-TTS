import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pyttsx3
import uuid
from elevenlabs.client import ElevenLabs
import os


def get_sentiment_analyzer():
    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon")
        return SentimentIntensityAnalyzer()


_client = None

def get_client():
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
    return _client
  




analyzer = SentimentIntensityAnalyzer()

def detect_emotion(text: str):
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.4:
        emotion = "positive"
    elif compound <= -0.4:
        emotion = "negative"
    else:
        emotion = "neutral"

    intensity = min(abs(compound), 1.0)

    return emotion, intensity

if __name__ == "__main__":
    tests = [
        "This is fine.",
        "I am so sad and disappointed.",
        "I love this product!",
        "This is terrible.",
        "I mean, it's not bad, but it could be better.",
        "This is the worst experience ever.",
        "I am very happy with the result!"
    ]

    for t in tests:
        print(t, "→", detect_emotion(t))


BASE_RATE = 170
BASE_VOLUME = 1.0

def map_emotion_to_voice(emotion, intensity):
    rate = BASE_RATE
    volume = BASE_VOLUME

    if emotion == "positive":
        rate += int(40 * intensity)
        volume = 1.0

    elif emotion == "negative":
        rate -= int(30 * intensity)
        volume = 0.6

    else:  # neutral
        rate = BASE_RATE
        volume = 0.9

    volume = max(0.7, min(volume, 1.0))
    return rate, volume

engine = pyttsx3.init()

def speak_pyttsx3(text: str):
    emotion, intensity = detect_emotion(text)
    rate, volume = map_emotion_to_voice(emotion, intensity)

    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    filename = f"output_{uuid.uuid4().hex}.wav"
    engine.save_to_file(text, filename)
    engine.runAndWait()

    return {
        "emotion": emotion,
        "intensity": intensity,
        "rate": rate,
        "volume": volume,
        "file": filename
    }


if __name__ == "__main__":
    text = input("Enter text: ")
    result = speak_pyttsx3(text)
    print(result)
    print(f"Emotion: {result['emotion']}")
    print(f"Intensity: {result['intensity']}")
    print(f"Rate: {result['rate']}")
    print(f"Volume: {result['volume']}")


def emotion_to_eleven_params(emotion, intensity):
    if emotion == "positive":
        return {
            "stability": max(0.05, 0.25 - 0.2 * intensity),
            "similarity_boost": 0.9,
            "style": min(1.0, 0.85 + 0.15 * intensity),
            "use_speaker_boost": True
        }

    if emotion == "negative":
        return {
            "stability": min(0.9, 0.7 + 0.2 * intensity),
            "similarity_boost": 0.5,
            "style": max(0.05, 0.15 - 0.1 * intensity),
            "use_speaker_boost": False
        }

    return {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.4,
        "use_speaker_boost": False
    }

def enrich_text_for_emotion(text, emotion):
    if emotion == "positive":
        return (
            "Wow!!!  "
            + text.upper()
            + "!!!  "
            + "This is absolutely amazing!"
        )

    if emotion == "negative":
        return (
            "I’m really sorry…  "
            + text
            + "…  "
            + "I understand how frustrating this can be."
        )

    return text

def speak_elevenlabs(text: str):
    emotion, intensity = detect_emotion(text)
    voice_params = emotion_to_eleven_params(emotion, intensity)

    text = enrich_text_for_emotion(text, emotion)

    

    client = get_client()
    audio_stream = client.text_to_speech.convert(
        voice_id="EXAVITQu4vr4xnSDxMaL",
        text=text,
        voice_settings=voice_params
    )

    filename = f"static/audio/output_{uuid.uuid4().hex}.mp3"
    os.makedirs("static/audio", exist_ok=True)

    with open(filename, "wb") as f:
        for chunk in audio_stream:
            if chunk:
             f.write(chunk)

    print(f"[Emotion] {emotion}")
    print(f"[Intensity] {intensity}")
    print(f"[Voice Params] {voice_params}")

    return {
        "emotion": emotion,
        "intensity": intensity,
        "file": filename.replace("static/audio/", "")
    }

def speak(text: str, provider: str = "auto"):
    """
    provider:
      - 'auto'       → try ElevenLabs, fallback to local
      - 'elevenlabs' → force ElevenLabs
      - 'local'      → force pyttsx3
    """
    if provider == "local":
        return speak_pyttsx3(text)

    if provider == "elevenlabs":
        return speak_elevenlabs(text)

    # AUTO MODE (recommended)
    try:
        return speak_elevenlabs(text)
    except Exception as e:
        print("⚠️ ElevenLabs failed, falling back to local TTS:", e)
        return speak_pyttsx3(text)

   

    




