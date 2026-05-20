"""
NEXUS — AI-Powered Student Wellbeing Advisor
HCI Assessment (CLO-3) | SE305T Spring-26
Uses: speech_recognition (STT), nltk VADER, textblob, matplotlib
(No whisper/torch required — compatible with Assignment-5 library set)
"""

import sys
import time
import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from collections import Counter

# ── Download required NLTK data ──────────────────────────────────────────────
nltk.download('vader_lexicon', quiet=True)

# ── Shared state used across stages ──────────────────────────────────────────
recognizer = sr.Recognizer()
sia = SentimentIntensityAnalyzer()

WELLBEING_SCALE = [
    ('THRIVING',    0.60,          float('inf'), '🌟'),
    ('CONTENT',     0.20,          0.60,         '😊'),
    ('NEUTRAL',    -0.19,          0.20,         '😐'),
    ('STRESSED',   -0.40,         -0.19,         '😟'),
    ('DISTRESSED', -0.60,         -0.40,         '😢'),
    ('CRISIS',     float('-inf'), -0.60,         '🆘'),
]

SUPPORT_KEYWORDS = {
    'ACADEMIC':  ['assignment', 'deadline', 'exam', 'grade', 'fail', 'pass',
                  'lecture', 'study', 'professor', 'submit','degree'],
    'WELLBEING': ['stress', 'anxious', 'depressed', 'lonely', 'overwhelmed',
                  'panic', 'cry', 'hopeless', 'afraid'],
    'FINANCIAL': ['fees', 'scholarship', 'loan', 'afford', 'money', 'rent',
                  'bursary', 'payment', 'debt'],
    'TECHNICAL': ['portal', 'login', 'password', 'system', 'error', 'access',
                  'email', 'vpn', 'reset'],
    'SOCIAL':    ['friends', 'roommate', 'belong', 'isolated', 'group',
                  'relationship', 'community'],
    'ADMIN':     ['enrolment', 'certificate', 'transcript', 'registration',
                  'form', 'office'],
}

# =============================================================================
# STAGE 1 — Input Layer: Voice + Text Capture & Transcription
# =============================================================================

def nexus_capture_audio(seconds=7, sample_rate=16000):
    """
    Records audio from the system microphone for a fixed number of seconds.

    Uses the SpeechRecognition library to open the default microphone and
    record raw audio for `seconds` seconds. A countdown is printed so the
    student knows how long they have to speak.

    Args:
        seconds (int): Duration to record, default 7 seconds.
        sample_rate (int): Target sample rate in Hz, default 16000.
                           (speech_recognition manages the actual device rate.)

    Returns:
        sr.AudioData: An AudioData object ready to be passed to nexus_transcribe().
    """
    print(f"\n🎙  NEXUS is listening — you have {seconds} second(s). Speak now!")
    with sr.Microphone(sample_rate=sample_rate) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        for remaining in range(seconds, 0, -1):
            print(f"   ⏱  {remaining}s remaining…", end='\r')
            time.sleep(0)          # just display; blocking is inside record()
        audio_data = recognizer.record(source, duration=seconds)
    print("\n✅  Recording complete.")
    return audio_data


def nexus_transcribe(audio_data, sample_rate=16000):
    """
    Transcribes an audio recording to text using Google Speech Recognition.

    This function replaces the Whisper-based transcription used in other
    versions of NEXUS. It uses the free Google Web Speech API via the
    speech_recognition library, which requires no local GPU or large model
    download.

    Args:
        audio_data (sr.AudioData): Audio captured by nexus_capture_audio().
        sample_rate (int): Provided for API compatibility; not used directly
                           by Google STT (it handles resampling internally).

    Returns:
        dict: {
            'text'       (str):  Transcribed text, or empty string on failure.
            'language'   (str):  Always 'en-US' for Google STT default.
            'confidence' (str):  'high' if text length > 10 chars, else 'low'.
        }
    """
    try:
        text = recognizer.recognize_google(audio_data, language='en-US')
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        print(f"⚠  STT service error: {e}")
        text = ""

    confidence = 'high' if len(text) > 10 else 'low'
    return {
        'text':       text,
        'language':   'en-US',
        'confidence': confidence,
    }


def nexus_get_input(turn_number):
    """
    Prompts the student for either text or voice input and returns a
    structured dict with source tracking and word count.

    Shows the current turn number in the prompt. Students may type 'voice'
    at the text prompt to switch to microphone input for that turn.

    Args:
        turn_number (int): The current conversation turn (1-indexed).

    Returns:
        dict: {
            'text'       (str):  The student's message.
            'source'     (str):  'text' or 'voice'.
            'turn'       (int):  The provided turn_number.
            'word_count' (int):  Number of words in the message.
        }
    """
    print(f"\n{'─'*50}")
    print(f"  NEXUS | Turn {turn_number}")
    print(f"{'─'*50}")
    choice = input("  Type your message (or 'voice' to speak): ").strip()

    if choice.lower() == 'voice':
        audio_data = nexus_capture_audio()
        result = nexus_transcribe(audio_data)
        text = result['text']
        source = 'voice'
        if not text:
            print("  ⚠  Could not recognise speech — falling back to text.")
            text = input("  Please type your message instead: ").strip()
            source = 'text'
    else:
        text = choice
        source = 'text'

    word_count = len(text.split()) if text else 0
    return {
        'text':       text,
        'source':     source,
        'turn':       turn_number,
        'word_count': word_count,
    }


# ── Stage 1 self-test (uncomment to run) ─────────────────────────────────────
# result = nexus_get_input(turn_number=1)
# assert 'text' in result and 'source' in result
# assert 'turn' in result and 'word_count' in result
# assert result['source'] in ('voice', 'text')
# print('Stage 1 OK:', result)


# =============================================================================
# STAGE 2 — Wellbeing Engine: 6-Tier Emotional State Tracker
# =============================================================================

def assess_wellbeing(text):
    """
    Classify a piece of student text into the NEXUS 6-Tier Wellbeing Scale
    using VADER sentiment analysis.

    Args:
        text (str): The student's input message.

    Returns:
        dict: {
            'tier'      (str):  One of THRIVING / CONTENT / NEUTRAL /
                                STRESSED / DISTRESSED / CRISIS.
            'score'     (float): VADER compound score in [-1, 1].
            'emoji'     (str):  Corresponding wellbeing emoji.
            'is_at_risk'(bool): True only if tier == 'CRISIS'.
        }
    """
    score = sia.polarity_scores(text)['compound']

    tier, emoji = 'NEUTRAL', '😐'
    for tier_name, low, high, tier_emoji in WELLBEING_SCALE:
        if low <= score < high:
            tier, emoji = tier_name, tier_emoji
            break

    is_at_risk = (tier == 'CRISIS')
    return {
        'tier':       tier,
        'score':      score,
        'emoji':      emoji,
        'is_at_risk': is_at_risk,
    }


def compute_trajectory(wellbeing_log):
    """
    Compute the emotional trend across a session by comparing the first-half
    average score with the second-half average score.

    Args:
        wellbeing_log (list[dict]): List of dicts returned by assess_wellbeing(),
                                    one per conversation turn.

    Returns:
        dict: {
            'trend'       (str):  'improving', 'declining', or 'fluctuating'.
            'lowest_tier' (str):  The tier label with the lowest score seen.
            'at_risk_turns'(list): 0-based indices of turns where is_at_risk
                                   is True.
        }
    """
    if not wellbeing_log:
        return {'trend': 'fluctuating', 'lowest_tier': 'NEUTRAL', 'at_risk_turns': []}

    scores = [entry['score'] for entry in wellbeing_log]
    n = len(scores)
    mid = n // 2

    first_avg  = np.mean(scores[:mid]) if mid > 0 else scores[0]
    second_avg = np.mean(scores[mid:]) if scores[mid:] else scores[-1]

    if second_avg > first_avg + 0.1:
        trend = 'improving'
    elif second_avg < first_avg - 0.1:
        trend = 'declining'
    else:
        trend = 'fluctuating'

    lowest_entry = min(wellbeing_log, key=lambda e: e['score'])
    lowest_tier  = lowest_entry['tier']

    at_risk_turns = [i for i, e in enumerate(wellbeing_log) if e['is_at_risk']]

    return {
        'trend':        trend,
        'lowest_tier':  lowest_tier,
        'at_risk_turns': at_risk_turns,
    }


def check_and_alert(wellbeing_result, turn_number):
    """
    Print a prominent crisis alert if the student's wellbeing is at CRISIS
    level, and return the at-risk boolean flag.

    Args:
        wellbeing_result (dict): Output of assess_wellbeing().
        turn_number      (int):  Current 1-based turn number.

    Returns:
        bool: True if the student is at risk (CRISIS tier), else False.
    """
    if wellbeing_result['is_at_risk']:
        print(f"""
╔══════════════════════════════════════════════════════╗
║  🆘  NEXUS CRISIS ALERT — Turn {turn_number:<3}                   ║
║  A student may need IMMEDIATE support.               ║
║  Please contact the University Counselling Line NOW  ║
║  📞  0800-XXX-XXXX  (24 / 7)                        ║
╚══════════════════════════════════════════════════════╝
""")
    return wellbeing_result['is_at_risk']


# =============================================================================
# STAGE 3 — Support Classifier & At-Risk Flag System
# =============================================================================

def classify_support_need(text):
    """
    Classify student text into one or more NEXUS support categories using
    keyword matching. Returns ALL matching categories so multi-need students
    are never under-served.

    Args:
        text (str): The student's input message.

    Returns:
        dict: {
            'primary'     (str):  Highest-scoring category label.
            'all_detected'(list): All categories with score > 0, sorted
                                  descending by score.
            'scores'      (dict): Mapping of category → keyword hit count.
        }
    """
    lower_text = text.lower()
    scores = {}
    for category, keywords in SUPPORT_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in lower_text)
        scores[category] = count

    all_detected = [cat for cat, sc in
                    sorted(scores.items(), key=lambda x: x[1], reverse=True)
                    if sc > 0]

    primary = all_detected[0] if all_detected else 'GENERAL'

    return {
        'primary':      primary,
        'all_detected': all_detected,
        'scores':       scores,
    }


def log_support_transition(support_log, new_primary, turn_number):
    """
    Append a transition event to support_log whenever the primary support
    category changes from the previous turn. Marks escalations into WELLBEING.

    Args:
        support_log  (list):  Mutable list of transition event dicts.
        new_primary  (str):   Primary category detected in the current turn.
        turn_number  (int):   Current 1-based turn number.

    Returns:
        list: The updated support_log.
    """
    if support_log:
        prev_primary = support_log[-1].get('curr', 'GENERAL')
    else:
        prev_primary = 'GENERAL'

    if new_primary != prev_primary:
        is_escalation = (new_primary == 'WELLBEING' and prev_primary != 'WELLBEING')
        event = {
            'prev':          prev_primary,
            'curr':          new_primary,
            'turn':          turn_number,
            'is_escalation': is_escalation,
        }
        support_log.append(event)

    return support_log


def nexus_respond(text, support_need, wellbeing):
    """
    Generate a context-aware, empathetic NEXUS response based on the student's
    primary support category and current wellbeing tier.

    Handles all 6 required combinations plus sensible fall-backs for any other
    combination that may arise.

    Args:
        text         (str): The student's raw message (reserved for future use).
        support_need (str): Primary support category from classify_support_need().
        wellbeing    (str): Wellbeing tier string from assess_wellbeing().

    Returns:
        str: A tailored response string.
    """
    combo = (support_need, wellbeing)

    # ── Required combinations ─────────────────────────────────────────────
    if combo == ('WELLBEING', 'CRISIS'):
        return ("I am very concerned about you. Please contact the university "
                "counselling line RIGHT NOW: 0800-XXX-XXXX.")

    if combo == ('WELLBEING', 'DISTRESSED'):
        return ("It sounds like you are going through a really difficult time. "
                "Have you spoken to anyone about how you are feeling?")

    if combo == ('ACADEMIC', 'STRESSED'):
        return ("Exam pressure is real. Let us look at what support your faculty "
                "offers — have you spoken to your tutor?")

    if support_need == 'FINANCIAL':
        return ("Financial difficulty is more common than you think. The university "
                "bursary office can help — shall I give you their contact?")

    if support_need == 'TECHNICAL':
        return ("Let me help you with that technical issue. "
                "Which system are you trying to access?")

    if combo == ('SOCIAL', 'DISTRESSED'):
        return ("Feeling isolated at university is incredibly hard. The student "
                "union runs weekly social events — would that help?")

    # ── Additional sensible fall-backs ────────────────────────────────────
    if support_need == 'WELLBEING':
        return ("It is okay to feel the way you do. NEXUS is here. "
                "Would you like me to connect you with a student counsellor?")

    if support_need == 'ACADEMIC':
        return ("I hear you — academic challenges can feel overwhelming. "
                "Have you reached out to your module coordinator or student services?")

    if support_need == 'SOCIAL':
        return ("Building connections takes time. The Student Union has clubs and "
                "events that can help — want me to share the link?")

    if support_need == 'ADMIN':
        return ("I can help with that administrative query. Please visit the "
                "student office or use the online portal for the fastest resolution.")

    # ── Generic fallback ──────────────────────────────────────────────────
    return ("Thank you for sharing that with me. NEXUS is here to support you — "
            "please feel free to tell me more so I can direct you to the right help.")


# =============================================================================
# STAGE 4 — Surprise Challenge: Offline Session Replay
# =============================================================================

STUDENT_LOG = [
    'Hi, I need some help please.',
    'I have a major assignment due tomorrow and I have not started.',
    'My laptop also broke yesterday so I cannot access my files.',
    'To be honest I have been struggling a lot lately, not just academically.',
    'I have not been sleeping, I feel completely hopeless about everything.',
    'I think I might need to talk to someone but I do not know who.',
    'Also I got an email saying my fees are overdue and I cannot register.',
    'Sorry for dumping all this. I just feel very alone right now.',
    'Actually, my friend just texted. I feel a tiny bit better now.',
    'Thank you for listening. I will try to contact the counsellor.',
]


def run_session_replay(student_log=None):
    """
    Process an offline student conversation log through the complete NEXUS
    pipeline without requiring a microphone.

    For every turn the function prints the wellbeing emoji + tier, the
    primary support category, any multi-labels, and the NEXUS response.
    Returns the accumulated logs needed for the intelligence report.

    Args:
        student_log (list[str]): List of student messages. Defaults to the
                                 assessment-supplied STUDENT_LOG.

    Returns:
        tuple: (session_log, wellbeing_log, support_primary_log, transition_log)
    """
    if student_log is None:
        student_log = STUDENT_LOG

    session_log     = []  # list of nexus_get_input-style dicts
    wellbeing_log   = []  # list of assess_wellbeing dicts
    support_primary = []  # list of primary category strings (one per turn)
    transition_log  = []  # list of transition event dicts

    print("\n" + "═"*60)
    print("  NEXUS — SESSION REPLAY (Offline Mode)")
    print("═"*60)

    for i, msg in enumerate(student_log):
        turn_number = i + 1

        # Build session entry (source = 'text' for offline replay)
        session_entry = {
            'text':       msg,
            'source':     'text',
            'turn':       turn_number,
            'word_count': len(msg.split()),
        }
        session_log.append(session_entry)

        # Wellbeing
        wb   = assess_wellbeing(msg)
        wellbeing_log.append(wb)

        # Support need
        need = classify_support_need(msg)
        support_primary.append(need['primary'])

        # Transition logging
        log_support_transition(transition_log, need['primary'], turn_number)

        # Crisis alert
        check_and_alert(wb, turn_number)

        # Response
        resp = nexus_respond(msg, need['primary'], wb['tier'])

        print(f"Turn {turn_number:>2}: {wb['emoji']} {wb['tier']:<12} | "
              f"Primary: {need['primary']:<10} | "
              f"All: {need['all_detected']}")
        print(f"  Student : {msg}")
        print(f"  NEXUS   : {resp}\n")

    return session_log, wellbeing_log, support_primary, transition_log


# =============================================================================
# STAGE 5 — Intelligence Report & Submission
# =============================================================================

def generate_intelligence_report(session_log, wellbeing_log,
                                  support_log, transition_log):
    """
    Generate a structured counsellor intelligence report at the end of a
    NEXUS session.

    Computes risk score using the assessment-specified formula and determines
    the recommended clinical action.

    Args:
        session_log    (list[dict]): Per-turn input records.
        wellbeing_log  (list[dict]): Per-turn wellbeing assessment records.
        support_log    (list[str]):  Per-turn primary support category strings.
        transition_log (list[dict]): Support transition event records.

    Prints:
        The full intelligence report to stdout.
    """
    # ── Basic counts ──────────────────────────────────────────────────────
    total_turns  = len(session_log)
    voice_turns  = sum(1 for t in session_log if t.get('source') == 'voice')
    text_turns   = total_turns - voice_turns

    # ── Wellbeing trajectory ──────────────────────────────────────────────
    trajectory   = compute_trajectory(wellbeing_log)
    avg_score    = np.mean([e['score'] for e in wellbeing_log]) if wellbeing_log else 0.0

    # ── At-risk turns ─────────────────────────────────────────────────────
    at_risk_turns = [i + 1 for i, e in enumerate(wellbeing_log) if e['is_at_risk']]
    at_risk_count = len(at_risk_turns)

    # ── Support category frequency ────────────────────────────────────────
    cat_freq = Counter(support_log)
    ranked_cats = cat_freq.most_common()

    # ── Escalation events ─────────────────────────────────────────────────
    escalations = [e for e in transition_log if e.get('is_escalation')]
    escalation_count = len(escalations)

    # ── Average words per turn ────────────────────────────────────────────
    avg_words = np.mean([t.get('word_count', 0) for t in session_log]) if session_log else 0

    # ── Risk score ────────────────────────────────────────────────────────
    base_risk          = 20
    wellbeing_penalty  = abs(avg_score) * 40
    at_risk_penalty    = at_risk_count * 15
    escalation_penalty = escalation_count * 10
    word_count_factor  = 5 if avg_words > 20 else 0

    risk_score = (base_risk + wellbeing_penalty + at_risk_penalty
                  + escalation_penalty + word_count_factor)
    risk_score = max(0, min(100, round(risk_score)))

    # ── Recommended action ────────────────────────────────────────────────
    if risk_score >= 70:
        action = 'URGENT_REFERRAL'
    elif risk_score >= 40:
        action = 'FOLLOW_UP'
    else:
        action = 'NO_ACTION'

    # ── Print report ──────────────────────────────────────────────────────
    W = 58
    print('=' * W)
    print('  NEXUS STUDENT INTELLIGENCE REPORT')
    print('  Code: NX-2B — Counsellor Eyes Only')
    print('=' * W)

    print(f"\n📋  SESSION OVERVIEW")
    print(f"  Total turns   : {total_turns}")
    print(f"  Voice turns   : {voice_turns}")
    print(f"  Text turns    : {text_turns}")

    print(f"\n💓  WELLBEING SUMMARY")
    print(f"  Trajectory    : {trajectory['trend'].upper()}")
    print(f"  Average score : {avg_score:+.3f}")
    print(f"  Lowest tier   : {trajectory['lowest_tier']}")

    print(f"\n🚨  AT-RISK ALERTS")
    print(f"  Total alerts  : {at_risk_count}")
    if at_risk_turns:
        print(f"  Alert turns   : {at_risk_turns}")
    else:
        print("  No CRISIS-level turns detected.")

    print(f"\n📂  SUPPORT CATEGORIES")
    for cat, freq in ranked_cats:
        bar = '█' * freq
        print(f"  {cat:<12} : {bar} ({freq})")

    print(f"\n⚠   ESCALATION EVENTS (→ WELLBEING)")
    if escalations:
        for ev in escalations:
            print(f"  Turn {ev['turn']:>2}: {ev['prev']} → {ev['curr']}")
    else:
        print("  None.")

    print(f"\n📊  RISK ASSESSMENT")
    print(f"  Risk score    : {risk_score} / 100")
    bar_filled = '█' * (risk_score // 5)
    bar_empty  = '░' * (20 - risk_score // 5)
    print(f"  [{bar_filled}{bar_empty}] {risk_score}%")

    action_symbol = {'URGENT_REFERRAL': '🔴', 'FOLLOW_UP': '🟡', 'NO_ACTION': '🟢'}
    print(f"\n  Recommended action: {action_symbol.get(action, '')} {action}")

    print('\n' + '=' * W)
    print("  END OF REPORT — NEXUS Session Intelligence v2.0")
    print('=' * W)


# =============================================================================
# Wellbeing Trajectory Plot (bonus visual for the counsellor report)
# =============================================================================

def plot_wellbeing_trajectory(wellbeing_log):
    """
    Render a simple line chart of the student's wellbeing compound score
    across all session turns and display it with matplotlib.

    Args:
        wellbeing_log (list[dict]): Output list from per-turn assess_wellbeing().
    """
    scores = [e['score'] for e in wellbeing_log]
    tiers  = [e['tier']  for e in wellbeing_log]
    turns  = list(range(1, len(scores) + 1))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(turns, scores, marker='o', linewidth=2, color='steelblue', label='Compound score')
    ax.axhline(0,    color='gray',   linestyle='--', linewidth=0.8)
    ax.axhline(-0.6, color='red',    linestyle=':',  linewidth=0.8, label='Crisis threshold')
    ax.axhline(0.6,  color='green',  linestyle=':',  linewidth=0.8, label='Thriving threshold')

    for x, y, tier in zip(turns, scores, tiers):
        ax.annotate(tier, (x, y), textcoords='offset points',
                    xytext=(0, 8), ha='center', fontsize=7)

    ax.set_xlabel('Turn')
    ax.set_ylabel('VADER Compound Score')
    ax.set_title('NEXUS — Student Wellbeing Trajectory')
    ax.set_xticks(turns)
    ax.legend()
    plt.tight_layout()
    plt.savefig('nexus_trajectory.png', dpi=120)
    plt.show()
    print("📊  Trajectory chart saved as nexus_trajectory.png")


# =============================================================================
# INTERACTIVE LIVE SESSION (run from __main__)
# =============================================================================

def run_live_session(max_turns=10):
    """
    Run a full interactive NEXUS session with real student input (text or
    voice). Prints a summary at the end and generates the counsellor report.

    Args:
        max_turns (int): Maximum number of conversation turns before the
                         session ends automatically.
    """
    print("\n" + "═"*60)
    print("  Welcome to NEXUS — Student Wellbeing Advisor")
    print("  Type your message or type 'voice' to speak.")
    print("  Type 'quit' or 'exit' to end the session early.")
    print("═"*60)

    session_log     = []
    wellbeing_log   = []
    support_primary = []
    transition_log  = []

    for turn in range(1, max_turns + 1):
        user_input = nexus_get_input(turn)

        if user_input['text'].lower() in ('quit', 'exit'):
            print("\n  Session ended by student.")
            break

        session_log.append(user_input)

        wb   = assess_wellbeing(user_input['text'])
        wellbeing_log.append(wb)

        need = classify_support_need(user_input['text'])
        support_primary.append(need['primary'])

        log_support_transition(transition_log, need['primary'], turn)
        check_and_alert(wb, turn)

        resp = nexus_respond(user_input['text'], need['primary'], wb['tier'])

        print(f"\n  {wb['emoji']} Wellbeing: {wb['tier']}  |  Support: {need['primary']}")
        print(f"  NEXUS: {resp}\n")

    generate_intelligence_report(session_log, wellbeing_log,
                                  support_primary, transition_log)
    plot_wellbeing_trajectory(wellbeing_log)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    print("\nNEXUS — Startup")
    print("─" * 40)
    print("  [1] Run OFFLINE session replay (Stage 4 — no mic needed)")
    print("  [2] Run LIVE interactive session")
    print("─" * 40)

    choice = input("Select mode (1 / 2): ").strip()

    if choice == '2':
        run_live_session()
    else:
        # ── Stage 4: Offline replay ───────────────────────────────────────
        session_log, wellbeing_log, support_primary, transition_log = run_session_replay()

        # ── Stage 5: Intelligence report ──────────────────────────────────
        print()
        generate_intelligence_report(session_log, wellbeing_log,
                                      support_primary, transition_log)

        # ── Bonus: trajectory chart ───────────────────────────────────────
        try:
            plot_wellbeing_trajectory(wellbeing_log)
        except Exception:
            pass  # skip if display not available (e.g. headless server)
