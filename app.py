import difflib
import html
import json
import os

import streamlit as st
from gemini_service import GeminiService, ServiceError, TONES, LENGTHS, validate_text

st.set_page_config(page_title="MailMate AI", page_icon="✉️", layout="wide")
st.markdown("""<style>
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stAppDeployButton"], #MainMenu, footer {display:none!important;}
.block-container {max-width:1240px;padding:2.5rem 2rem 3rem;}
h1 {letter-spacing:-.055em;font-weight:750!important;font-size:2.65rem!important;padding-bottom:.25rem!important;}
h3 {font-size:1.08rem!important;letter-spacing:-.02em;}
.st-key-email-card, .st-key-insights-card, .st-key-proof-card {background:#fff;border:1px solid #e2e8ed!important;border-radius:18px!important;padding:24px!important;box-shadow:0 4px 20px #17203303;}
[data-testid="stMetric"] {background:#f4f8f7;border:1px solid #e5eeeb;border-radius:12px;padding:14px;}
[data-testid="stMetricValue"] {font-size:1.4rem!important;}
[data-testid="stTextArea"] textarea {line-height:1.65!important;font-size:14px!important;}
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"]>div {border-radius:10px!important;}
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {border-radius:10px;min-height:42px;font-weight:600;}
[data-testid="stButton"] button[kind="primary"] {box-shadow:0 4px 12px #0f766e18;}
[data-testid="stCaptionContainer"] {color:#77818f;font-size:12px;}
[role="tablist"] {gap:8px;border-bottom:none!important;background:#e9eeed;padding:5px;border-radius:12px;width:fit-content;margin:1rem 0 1.25rem;}
[role="tab"] {padding:10px 22px!important;border-radius:8px;height:42px;color:#66716d;}
[role="tab"][aria-selected="true"] {background:white;color:#0f766e;box-shadow:0 1px 4px #17203310;}
.react-aria-SelectionIndicator {display:none;}
.brand-row {display:flex;align-items:center;gap:10px;margin-bottom:20px;color:#334155;font-size:13px;font-weight:650;}
.brand-icon {display:flex;align-items:center;justify-content:center;width:34px;height:34px;background:#0f766e;color:white;border-radius:10px;font-size:20px;}
.brand-label {letter-spacing:.12em;font-size:11px;color:#64748b;}
.empty-insights {border:1px dashed #dbe5e1;border-radius:12px;padding:28px 20px;text-align:center;background:#fafcfb;margin:8px 0 20px;}
.empty-icon {width:40px;height:40px;margin:0 auto 12px;background:#e5f1eb;color:#0f766e;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;}
.empty-title {font-weight:650;font-size:14px;color:#334155;margin-bottom:7px;}
.empty-description {font-size:13px;color:#7c8792;line-height:1.6;max-width:300px;margin:auto;}
@media(max-width:768px){[data-testid="stHorizontalBlock"]{flex-wrap:wrap;}
[data-testid="stColumn"]{min-width:100%!important;}
.block-container {padding:1.5rem 1rem;}
.st-key-email-card, .st-key-insights-card, .st-key-proof-card {padding:18px!important;}
h1 {font-size:2.1rem!important;}}
</style>""", unsafe_allow_html=True)

DEFAULTS = dict(email="", instructions="", signature="", tone="Professional", length="Short",
                reply="", analysis=None, analysis_source=None, reply_source=None,
                proof_text="", proof_result=None, proof_original="", busy=False, error=None,
                job=None, completed=None, request_input=None)
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.completed:
    st.session_state.update(st.session_state.completed)
    st.session_state.completed = None


def setting(name, default=""):
    if os.getenv(name):
        return os.environ[name]
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


def clear():
    for key, value in DEFAULTS.items():
        if key not in ("tone", "length", "signature"):
            st.session_state[key] = value


def use_reply():
    st.session_state.proof_text = st.session_state.reply
    st.session_state.proof_result = None


def apply_correction():
    if st.session_state.reply != st.session_state.proof_original:
        st.session_state.reply_source = None
    st.session_state.reply = st.session_state.proof_result.corrected_text


def enqueue(operation):
    if not st.session_state.busy:
        st.session_state.busy = True
        st.session_state.job = operation
        st.session_state.error = None
        st.session_state.request_input = {key: st.session_state[key] for key in
            ("email", "instructions", "signature", "tone", "length", "reply", "proof_text")}


def run(operation):
    st.session_state.error = None
    source = st.session_state.request_input
    updates = dict(source)
    try:
        if operation == "proofread":
            validate_text(source["proof_text"], "Proofreading text")
        else:
            validate_text(source["email"])
            if len(source["instructions"]) > 2000:
                raise ServiceError("Reply instructions exceed 2,000 characters. Shorten them and retry.")
        service = GeminiService(setting("GEMINI_API_KEY"), setting("GEMINI_MODEL", "gemini-2.5-flash"))
        with st.spinner("Working on your text…"):
            if operation == "proofread":
                result = service.proofread(source["proof_text"])
                updates.update(proof_result=result, proof_original=source["proof_text"])
            else:
                kwargs = {key: source[key] for key in ("email", "instructions", "signature", "tone", "length")}
                if operation == "analyze":
                    result = service.analyze_and_draft(**kwargs)
                    updates.update(analysis=result, analysis_source=source["email"])
                else:
                    result = service.regenerate_reply(**kwargs)
                updates.update(reply=result.reply, reply_source=source["email"])
    except ServiceError as exc:
        st.session_state.error = str(exc)
    except Exception:
        st.session_state.error = "Something went wrong. Retry; your existing text is preserved."
    finally:
        st.session_state.completed = updates
        st.session_state.busy = False
        st.session_state.job = None
        st.session_state.request_input = None


def copy_button(text):
    # Prevent draft text from breaking out of the script element.
    encoded = json.dumps(text).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    st.iframe("""<style>body{margin:0;font-family:Arial,sans-serif}button:hover{background:#f0f7f4!important}
        button:focus-visible{outline:2px solid #0f766e;outline-offset:2px}</style>
        <button id="copy" style="background:#fff;border:1px solid #dce3e1;width:100%;
        border-radius:10px;padding:12px 16px;cursor:pointer;color:#172033;font:600 14px sans-serif">
        Copy reply</button><span id="status" role="status" style="font:12px sans-serif"></span>
        <script>document.getElementById('copy').onclick=async()=>{try{
        await navigator.clipboard.writeText(""" + encoded + """);
        document.getElementById('status').textContent=' Copied';}catch(e){
        document.getElementById('status').textContent=' Use Download or select and copy the draft.';}};</script>""",
        height=65, alt="Copy the current reply")


st.markdown('<div class="brand-row"><span class="brand-icon">✉</span><span class="brand-label">YOUR WRITING WORKSPACE</span></div>', unsafe_allow_html=True)
st.title("MailMate AI")
st.markdown("Thoughtful replies. Clearer writing. A little less time in your inbox.")

email_tab, proof_tab = st.tabs(["Email assistant", "Proofread"])
with email_tab:
    left, right = st.columns([1, 1.15], gap="large")
    with left, st.container(border=True, key="email-card"):
        st.subheader("Received email")
        st.caption("Start with the message you want to respond to.")
        st.text_area("Email", key="email", height=260, placeholder="Paste an email here…", disabled=st.session_state.busy)
        st.caption(f"{len(st.session_state.email):,} / 20,000 characters")
        st.text_area("Reply instructions (optional)", key="instructions", height=90,
                     placeholder="For example: politely decline and ask for another date.", disabled=st.session_state.busy)
        c1, c2 = st.columns(2)
        c1.selectbox("Tone", TONES, key="tone", disabled=st.session_state.busy)
        c2.selectbox("Length", LENGTHS, key="length", disabled=st.session_state.busy)
        st.text_input("Signature (optional)", key="signature", max_chars=500, disabled=st.session_state.busy)
        generate, reset = st.columns([3, 1])
        generate.button("Analyze & Draft", type="primary", on_click=enqueue, args=("analyze",), disabled=st.session_state.busy, use_container_width=True)
        reset.button("Clear", on_click=clear, disabled=st.session_state.busy, use_container_width=True)
    with right, st.container(border=True, key="insights-card"):
        st.subheader("Email insights")
        analysis = st.session_state.analysis
        if analysis:
            if st.session_state.analysis_source != st.session_state.email:
                st.warning("These insights belong to an earlier email. Click Analyze & Draft to update them.")
            c1, c2 = st.columns(2)
            c1.metric("Intent", analysis.intent)
            c2.metric("Urgency", analysis.urgency)
            st.text(analysis.urgency_explanation)
            st.markdown("**Summary**")
            st.text(analysis.summary)
            st.markdown("**Required actions**")
            if analysis.action_items:
                for item in analysis.action_items:
                    st.text("• " + item)
            else:
                st.caption("No explicit action requested.")
            st.markdown("**Deadline**")
            st.text(analysis.deadline_text or "Not specified")
            if analysis.deadline_evidence:
                st.text("Source: " + analysis.deadline_evidence)
        else:
            st.markdown('<div class="empty-insights"><div class="empty-icon">✦</div><div class="empty-title">A clearer view of every email</div><div class="empty-description">Add a message and select Analyze & Draft to see its summary, next steps, and a suggested reply.</div></div>', unsafe_allow_html=True)
        st.subheader("Your reply")
        if st.session_state.reply_source and st.session_state.reply_source != st.session_state.email:
            st.warning("This draft belongs to an earlier email. Regenerate it for the current email.")
        st.text_area("Editable reply", key="reply", height=240, disabled=st.session_state.busy,
                     placeholder="Your draft will appear here. Make it yours before sending.")
        st.caption("Review the facts and commitments before sending.")
        st.button("Regenerate Reply", on_click=enqueue, args=("reply",), disabled=st.session_state.busy or not bool(st.session_state.reply))
        if st.session_state.reply:
            copy_col, download_col = st.columns(2)
            with copy_col:
                copy_button(st.session_state.reply)
            download_col.download_button("Download reply", st.session_state.reply, "mailmate-reply.txt", "text/plain", use_container_width=True)

with proof_tab, st.container(border=True, key="proof-card"):
    st.subheader("Polish your writing")
    st.caption("Correct English spelling, grammar and punctuation while preserving your meaning.")
    st.button("Use current reply", on_click=use_reply, disabled=st.session_state.busy or not bool(st.session_state.reply))
    st.text_area("Text to proofread", key="proof_text", height=220, disabled=st.session_state.busy)
    st.caption(f"{len(st.session_state.proof_text):,} / 20,000 characters")
    st.button("Proofread text", on_click=enqueue, args=("proofread",), disabled=st.session_state.busy, type="primary")
    proof = st.session_state.proof_result
    if proof:
        stale = st.session_state.proof_original != st.session_state.proof_text
        if stale:
            st.warning("These corrections belong to earlier text. Proofread again to update them.")
        c1, c2 = st.columns(2)
        c1.subheader("Original")
        c1.text(st.session_state.proof_original)
        c2.subheader("Corrected")
        c2.text(proof.corrected_text)
        st.markdown("**Changes** — removed words are struck through; added words are highlighted.")
        before, after = st.session_state.proof_original.split(), proof.corrected_text.split()
        parts = []
        for tag, i, j, a, b in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
            old, new = html.escape(" ".join(before[i:j])), html.escape(" ".join(after[a:b]))
            if tag == "equal":
                parts.append(old)
            else:
                if old:
                    parts.append(f'<del style="background:#fee2e2">{old}</del>')
                if new:
                    parts.append(f'<mark style="background:#dcfce7">{new}</mark>')
        st.markdown('<div style="line-height:1.9">' + " ".join(parts) + '</div>', unsafe_allow_html=True)
        for explanation in proof.change_explanations:
            st.text("• " + explanation)
        if proof.corrected_text == st.session_state.proof_original:
            st.success("No corrections needed.")
        st.button("Use corrected version", on_click=apply_correction, disabled=stale or st.session_state.busy)
        st.caption("Replaces the reply editor with this corrected text. The proofreading source stays unchanged.")

if st.session_state.error:
    st.error(st.session_state.error)
    st.caption("Retry with the same action button when ready.")

if st.session_state.job:
    run(st.session_state.job)
    st.rerun()
