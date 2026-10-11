from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import requests

app = Flask(__name__)

# --------------------------------------------------
# 1. SENTIMENT ANALYSIS MODEL
# --------------------------------------------------

print("Loading NLP model...")

try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("NLP model loaded successfully.")

except Exception as e:
    print("NLP model could not be loaded:", e)
    sentiment_analyzer = None


# --------------------------------------------------
# 2. SENTIMENT ANALYSIS
# --------------------------------------------------

def analyze_sentiment(email):
    """
    Analyze the sentiment of the incoming email.
    Returns: Positive / Negative / Neutral
    """

    if sentiment_analyzer is None:
        return "Neutral"

    try:
        result = sentiment_analyzer(email[:512])[0]

        if result["label"] == "POSITIVE":
            return "Positive"

        elif result["label"] == "NEGATIVE":
            return "Negative"

    except Exception as e:
        print("Sentiment error:", e)

    return "Neutral"


# --------------------------------------------------
# 3. INTENT DETECTION
# --------------------------------------------------

def detect_intent(email):
    """
    Detect the main purpose of the email.
    """

    text = email.lower()

    # Meeting
    if any(word in text for word in [
        "meeting",
        "appointment",
        "schedule",
        "reschedule",
        "meet"
    ]):
        return "Meeting / Appointment"

    # Payment
    if any(word in text for word in [
        "payment",
        "invoice",
        "bill",
        "price",
        "cost",
        "amount"
    ]):
        return "Payment / Invoice"

    # Leave
    if any(word in text for word in [
        "leave",
        "holiday",
        "vacation",
        "absent",
        "permission"
    ]):
        return "Leave Request"

    # Complaint / Problem
    if any(word in text for word in [
        "problem",
        "issue",
        "error",
        "not working",
        "complaint",
        "failure"
    ]):
        return "Problem / Complaint"

    # Thank You
    if any(word in text for word in [
        "thank",
        "thanks",
        "appreciate"
    ]):
        return "Thank You"

    # Information
    if any(word in text for word in [
        "information",
        "details",
        "question",
        "query",
        "tell me",
        "please provide"
    ]):
        return "Information Request"

    # Job
    if any(word in text for word in [
        "job",
        "resume",
        "cv",
        "interview",
        "vacancy",
        "application"
    ]):
        return "Job / Career"

    return "General"


# --------------------------------------------------
# 4. AI REPLY GENERATION
# --------------------------------------------------

def generate_reply(email, tone):
    """
    Generate reply using Ollama local AI.
    """

    prompt = f"""
You are an intelligent professional email assistant.

Read the email below and generate an appropriate reply.

Tone: {tone}

Instructions:
1. Reply only with the email body.
2. Do not explain your reasoning.
3. Keep the response natural and professional.
4. Understand the context of the original email.
5. Do not invent facts.
6. Do not use fake names.
7. Keep the reply reasonably short.

Original Email:
{email}

Generate the reply now.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",

            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },

            timeout=60
        )

        if response.status_code == 200:

            data = response.json()

            reply = data.get("response", "").strip()

            if reply:
                return reply

    except requests.exceptions.ConnectionError:

        print("Ollama is not running.")

    except Exception as e:

        print("AI generation error:", e)

    # If Ollama is unavailable
    return fallback_reply(email, tone)


# --------------------------------------------------
# 5. FALLBACK REPLY GENERATOR
# --------------------------------------------------

def fallback_reply(email, tone):
    """
    Generates a basic reply if AI is unavailable.
    """

    intent = detect_intent(email)

    # Meeting
    if intent == "Meeting / Appointment":

        return """Hello,

Thank you for your email. I understand your request regarding the meeting. I would be happy to coordinate a suitable time. Please let me know your preferred schedule.

Best regards"""

    # Leave
    elif intent == "Leave Request":

        return """Hello,

Thank you for informing me. I have received your leave request and will review it accordingly. I will get back to you shortly.

Best regards"""

    # Payment
    elif intent == "Payment / Invoice":

        return """Hello,

Thank you for your email regarding the payment/invoice. I have received your request and will review the details. I will get back to you shortly.

Best regards"""

    # Complaint
    elif intent == "Problem / Complaint":

        return """Hello,

Thank you for bringing this issue to our attention. We understand your concern and will look into the matter as soon as possible.

We will get back to you with an update.

Best regards"""

    # Thank you
    elif intent == "Thank You":

        return """Hello,

You're very welcome. Thank you for your kind message. Please feel free to contact us if you need any further assistance.

Best regards"""

    # Information
    elif intent == "Information Request":

        return """Hello,

Thank you for your email. I have received your request for information. I will review the details and get back to you shortly.

Best regards"""

    # Job
    elif intent == "Job / Career":

        return """Hello,

Thank you for your interest and for sharing your application. We have received your message and will review the details accordingly.

We will get back to you with further information.

Best regards"""

    # General
    else:

        return """Hello,

Thank you for your email. I have received your message and will review it carefully. I will get back to you as soon as possible.

Best regards"""


# --------------------------------------------------
# 6. HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# 7. GENERATE REPLY API
# --------------------------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        email = data.get("email", "").strip()

        tone = data.get(
            "tone",
            "Professional"
        )

        # Validate email
        if not email:

            return jsonify({
                "success": False,
                "message": "Please enter an email."
            }), 400

        # NLP analysis
        sentiment = analyze_sentiment(email)

        # Intent detection
        intent = detect_intent(email)

        # Generate AI reply
        reply = generate_reply(
            email,
            tone
        )

        # Return response
        return jsonify({

            "success": True,

            "reply": reply,

            "sentiment": sentiment,

            "intent": intent,

            "tone": tone

        })

    except Exception as e:

        print("Server error:", e)

        return jsonify({

            "success": False,

            "message": "Something went wrong."

        }), 500


# --------------------------------------------------
# 8. HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "application": "AI Email Reply Generator",

        "nlp_model": (
            "loaded"
            if sentiment_analyzer
            else "not loaded"
        )

    })


# --------------------------------------------------
# 9. START FLASK SERVER
# --------------------------------------------------

if __name__ == "__main__":

    print("----------------------------------------")
    print("AI Email Reply Generator")
    print("----------------------------------------")
    print("Server starting...")
    print("Open: http://127.0.0.1:5000")

    