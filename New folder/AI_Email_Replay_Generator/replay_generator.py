import requests


class ReplyGenerator:
    """
    AI-based email reply generator.

    Uses Ollama locally to generate email replies.
    """

    def __init__(
        self,
        model="llama3.2",
        ollama_url="http://localhost:11434/api/generate"
    ):
        self.model = model
        self.ollama_url = ollama_url


    # --------------------------------------------------
    # CREATE PROMPT
    # --------------------------------------------------

    def create_prompt(
        self,
        email,
        tone="Professional",
        intent="General",
        sentiment="Neutral",
        keywords=None
    ):
        """
        Create an AI prompt using NLP analysis.
        """

        if keywords is None:
            keywords = []

        keyword_text = ", ".join(keywords)

        prompt = f"""
You are an AI email reply assistant.

Your task is to write a suitable reply to the email provided below.

EMAIL INFORMATION
-----------------
Intent: {intent}
Sentiment: {sentiment}
Important Keywords: {keyword_text}
Required Tone: {tone}

ORIGINAL EMAIL
--------------
{email}

INSTRUCTIONS
------------
1. Understand the meaning and context of the email.
2. Write an appropriate reply.
3. Use the requested tone.
4. Keep the response clear and natural.
5. Do not invent information.
6. Do not make promises that are not present in the email.
7. Do not mention that you are an AI.
8. Do not explain your reasoning.
9. Return only the email reply.
10. Do not add a subject line unless specifically requested.

REPLY:
"""

        return prompt


    # --------------------------------------------------
    # GENERATE USING OLLAMA
    # --------------------------------------------------

    def generate_with_ollama(self, prompt):
        """
        Send the prompt to Ollama and return the generated reply.
        """

        try:

            response = requests.post(
                self.ollama_url,

                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },

                timeout=60
            )

            if response.status_code != 200:

                print(
                    "Ollama HTTP Error:",
                    response.status_code
                )

                return None

            data = response.json()

            reply = data.get(
                "response",
                ""
            ).strip()

            if reply:
                return reply

            return None

        except requests.exceptions.ConnectionError:

            print(
                "Error: Ollama is not running."
            )

            return None

        except requests.exceptions.Timeout:

            print(
                "Error: Ollama request timed out."
            )

            return None

        except Exception as e:

            print(
                "AI generation error:",
                e
            )

            return None


    # --------------------------------------------------
    # CLEAN GENERATED REPLY
    # --------------------------------------------------

    def clean_reply(self, reply):
        """
        Clean unnecessary AI output.
        """

        if not reply:
            return ""

        reply = reply.strip()

        # Remove common prefixes
        prefixes = [
            "Reply:",
            "REPLY:",
            "Email Reply:",
            "Generated Reply:"
        ]

        for prefix in prefixes:

            if reply.startswith(prefix):

                reply = reply[
                    len(prefix):
                ].strip()

        return reply


    # --------------------------------------------------
    # FALLBACK REPLY
    # --------------------------------------------------

    def fallback_reply(
        self,
        email,
        intent="General",
        tone="Professional"
    ):
        """
        Basic reply when Ollama is unavailable.
        """

        if intent == "Meeting / Appointment":

            return """Hello,

Thank you for your email. I understand your request regarding the meeting. Please let me know a suitable time so that we can coordinate accordingly.

Best regards"""

        elif intent == "Payment / Invoice":

            return """Hello,

Thank you for your email regarding the payment or invoice. I have received your request and will review the details. I will get back to you shortly.

Best regards"""

        elif intent == "Leave Request":

            return """Hello,

Thank you for informing me about your leave request. I have received your message and will review it accordingly.

Best regards"""

        elif intent == "Problem / Complaint":

            return """Hello,

Thank you for bringing this issue to our attention. We understand your concern and will review the matter as soon as possible.

Best regards"""

        elif intent == "Thank You":

            return """Hello,

You're very welcome. Thank you for your kind message. Please feel free to reach out if you need any further assistance.

Best regards"""

        elif intent == "Information Request":

            return """Hello,

Thank you for your email. I have received your request for information and will review the details. I will get back to you shortly.

Best regards"""

        elif intent == "Job / Career":

            return """Hello,

Thank you for your interest and for sharing your application. We have received your message and will review the details accordingly.

Best regards"""

        elif intent == "Order / Delivery":

            return """Hello,

Thank you for contacting us regarding your order. We have received your message and will check the relevant details.

Best regards"""

        else:

            return """Hello,

Thank you for your email. I have received your message and will review it carefully. I will get back to you as soon as possible.

Best regards"""


    # --------------------------------------------------
    # MAIN GENERATION FUNCTION
    # --------------------------------------------------

    def generate_reply(
        self,
        email,
        tone="Professional",
        intent="General",
        sentiment="Neutral",
        keywords=None
    ):
        """
        Main function for generating an email reply.
        """

        if not email or not email.strip():

            return {
                "success": False,
                "reply": "",
                "message": "Email text is required."
           