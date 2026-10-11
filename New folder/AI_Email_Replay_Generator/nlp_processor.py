from transformers import pipeline
import re


class NLPProcessor:

    def __init__(self):
        """
        Initialize NLP models.
        """

        print("Loading NLP models...")

        try:
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )

            print("Sentiment model loaded successfully.")

        except Exception as e:
            print("Error loading sentiment model:", e)
            self.sentiment_model = None


    # --------------------------------------------------
    # TEXT CLEANING
    # --------------------------------------------------

    def clean_text(self, text):
        """
        Clean email text.
        """

        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        # Remove unnecessary special characters
        text = re.sub(r"[^\w\s.,!?@'-]", "", text)

        return text.strip()


    # --------------------------------------------------
    # SENTIMENT ANALYSIS
    # --------------------------------------------------

    def analyze_sentiment(self, text):
        """
        Detect email sentiment.
        """

        if not text:
            return "Neutral"

        if self.sentiment_model is None:
            return "Neutral"

        try:

            result = self.sentiment_model(
                text[:512]
            )[0]

            label = result["label"]

            if label == "POSITIVE":
                return "Positive"

            elif label == "NEGATIVE":
                return "Negative"

            return "Neutral"

        except Exception as e:

            print("Sentiment analysis error:", e)

            return "Neutral"


    # --------------------------------------------------
    # INTENT DETECTION
    # --------------------------------------------------

    def detect_intent(self, text):
        """
        Detect the purpose of the email.
        """

        text = text.lower()

        intents = {

            "Meeting / Appointment": [
                "meeting",
                "appointment",
                "schedule",
                "scheduled",
                "reschedule",
                "rescheduling",
                "meet"
            ],

            "Payment / Invoice": [
                "payment",
                "invoice",
                "bill",
                "billing",
                "price",
                "cost",
                "amount",
                "transaction"
            ],

            "Leave Request": [
                "leave",
                "holiday",
                "vacation",
                "absent",
                "absence",
                "permission"
            ],

            "Problem / Complaint": [
                "problem",
                "issue",
                "error",
                "not working",
                "complaint",
                "failure",
                "unable"
            ],

            "Thank You": [
                "thank",
                "thanks",
                "thank you",
                "appreciate",
                "grateful"
            ],

            "Information Request": [
                "information",
                "details",
                "question",
                "query",
                "please provide",
                "can you tell",
                "let me know"
            ],

            "Job / Career": [
                "job",
                "resume",
                "cv",
                "interview",
                "vacancy",
                "career",
                "application",
                "hiring"
            ],

            "Order / Delivery": [
                "order",
                "delivery",
                "deliver",
                "shipment",
                "tracking",
                "package"
            ]
        }

        # Check each intent
        for intent, keywords in intents.items():

            for keyword in keywords:

                if keyword in text:
                    return intent

        return "General"


    # --------------------------------------------------
    # KEYWORD EXTRACTION
    # --------------------------------------------------

    def extract_keywords(self, text):
        """
        Extract important words from the email.
        """

        stop_words = {

            "the",
            "is",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "in",
            "on",
            "for",
            "with",
            "this",
            "that",
            "i",
            "you",
            "we",
            "are",
            "was",
            "were",
            "be",
            "can",
            "could",
            "would",
            "please",
            "your",
            "my",
            "me"
        }

        words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text.lower()
        )

        keywords = []

        for word in words:

            if word not in stop_words:

                if word not in keywords:
                    keywords.append(word)

        # Return maximum 10 keywords
        return keywords[:10]


    # --------------------------------------------------
    # EMAIL ANALYSIS
    # --------------------------------------------------

    def process_email(self, email):
        """
        Complete NLP processing pipeline.
        """

        cleaned_email = self.clean_text(email)

        sentiment = self.analyze_sentiment(
            cleaned_email
        )

        intent = self.detect_intent(
            cleaned_email
        )

        keywords = self.extract_keywords(
            cleaned_email
        )

        return {

            "original_text": email,

            "cleaned_text": cleaned_email,

            "sentiment": sentiment,

            "intent": intent,

            "keywords": keywords
        }


# --------------------------------------------------
# TEST THE NLP PROCESSOR
# --------------------------------------------------

if __name__ == "__main__":

    processor = NLPProcessor()

    sample_email = """
    Hello,

    I am unable to attend tomorrow's meeting.
    Can we reschedule the appointment to Friday?

    Thank you.
    """

    result = processor.process_email(
        sample_email
    )

    print("\n-----------------------------")
    print("NLP PROCESSING RESULT")
    print("-----------------------------")

    print("Sentiment:",
          result["sentiment"])

    print("Intent:",
          result["intent"])

    print("Keywords:",
          result["keywords"])

    print("Cleaned Text:",
          result["cleaned_text"])