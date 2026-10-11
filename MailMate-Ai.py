import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MailMate AI",
    page_icon="✉️",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

    .main {
        background-color: #f5f7fb;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .info-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
        color: #172033;
    }

    .metric-title {
        font-size: 14px;
        color: #334155;
        margin-bottom: 5px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 18px;
        font-weight: 600;
        color: #172033;
    }

    .footer {
        text-align: center;
        color: #888;
        margin-top: 40px;
        font-size: 14px;
    }

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown(
    '<div class="title">✉️ MailMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your Smart AI-Powered Email Assistant</div>',
    unsafe_allow_html=True
)


# ---------------- EMAIL INPUT ----------------

st.markdown(
    '<div class="section-title">📩 Received Email</div>',
    unsafe_allow_html=True
)

email = st.text_area(
    "Paste the email you received",
    height=220,
    placeholder="""Example:

Hello Aryan,

Could you please send me the final project report by tomorrow?

Regards,
Project Manager""",
    label_visibility="collapsed"
)


# ---------------- OPTIONS ----------------

st.markdown(
    '<div class="section-title">⚙️ Reply Settings</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    tone = st.selectbox(
        "🎭 Reply Tone",
        [
            "Professional",
            "Friendly",
            "Formal",
            "Casual",
            "Polite"
        ]
    )

with col2:
    length = st.selectbox(
        "📏 Reply Length",
        [
            "Short",
            "Medium",
            "Detailed"
        ]
    )

with col3:
    language = st.selectbox(
        "🌐 Language",
        [
            "English",
            "Hindi",
            "Marathi"
        ]
    )


# ---------------- ANALYZE BUTTON ----------------

st.write("")

analyze = st.button(
    "🔍 Analyze Email",
    use_container_width=True
)


if analyze:

    if not email.strip():

        st.warning("⚠️ Please paste an email first.")

    else:

        # Temporary analysis
        # Real AI analysis will be connected later.

        email_lower = email.lower()

        # Detect basic intent
        if any(word in email_lower for word in [
            "meeting",
            "schedule",
            "appointment"
        ]):
            intent = "Meeting / Scheduling"

        elif any(word in email_lower for word in [
            "report",
            "document",
            "file",
            "send"
        ]):
            intent = "Document / Information Request"

        elif any(word in email_lower for word in [
            "thank",
            "thanks"
        ]):
            intent = "Thank You"

        elif any(word in email_lower for word in [
            "problem",
            "issue",
            "complaint"
        ]):
            intent = "Problem / Complaint"

        else:
            intent = "General Email"

        # Basic urgency detection
        if any(word in email_lower for word in [
            "urgent",
            "immediately",
            "asap",
            "today",
            "deadline"
        ]):
            urgency = "High 🔴"

        elif any(word in email_lower for word in [
            "tomorrow",
            "soon"
        ]):
            urgency = "Medium 🟠"

        else:
            urgency = "Low 🟢"


        # ---------------- AI ANALYSIS ----------------

        st.markdown("---")

        st.markdown(
            '<div class="section-title">🧠 Email Analysis</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="metric-title">🎯 Intent</div>
                    <div class="metric-value">{intent}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="metric-title">⚠️ Urgency</div>
                    <div class="metric-value">{urgency}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div class="info-card">
                    <div class="metric-title">📅 Deadline</div>
                    <div class="metric-value">AI detection coming soon</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # ---------------- SUMMARY ----------------

        st.markdown(
            '<div class="section-title">📝 Summary</div>',
            unsafe_allow_html=True
        )

        st.info(
            "AI-generated email summary will appear here. "
            "The AI will understand the main purpose of the email "
            "and present it in simple words."
        )


        # ---------------- ACTION REQUIRED ----------------

        st.markdown(
            '<div class="section-title">✅ Required Action</div>',
            unsafe_allow_html=True
        )

        st.warning(
            "AI will identify what action the sender expects from you."
        )


        # ---------------- REPLY ----------------

        st.markdown(
            '<div class="section-title">✍️ Suggested Reply</div>',
            unsafe_allow_html=True
        )

        default_reply = f"""Hello,

Thank you for your email.

I have received your message and will get back to you shortly.

Best regards,
Aryan"""

        reply = st.text_area(
            "Generated Reply",
            value=default_reply,
            height=200,
            label_visibility="collapsed"
        )


        # ---------------- BUTTONS ----------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button(
                "📋 Copy Reply",
                use_container_width=True
            )

        with col2:
            st.button(
                "🔄 Regenerate",
                use_container_width=True
            )

        with col3:
            st.button(
                "🗑️ Clear",
                use_container_width=True
            )


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="footer">
        MailMate AI • AI-Powered Smart Email Assistant
    </div>
    """,
    unsafe_allow_html=True
)