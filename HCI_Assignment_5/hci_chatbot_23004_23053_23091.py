#!/usr/bin/env python3
"""
hci_chatbot_IBH_HK_MAC.py
Multi-Modal University Chatbot System
HCI Assignment 5 — SE305T & MD445T (Spring-26)
Dr. Muhammad Asif | Information Technology University, Lahore

Group Members:
    Ibrahim Sattar      (BSSE23004) — Spam Detection + STT
    M.Hasham Khan       (BSSE23053) — Intent Identification + TTS
    M.Abdullah Cheema   (BSSE23091) — Response Generation + Voice Pipeline + Menu
"""

import sys
import threading

# ── Optional library imports with graceful fallback ──────────────────────────

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False
    print("[WARN] speech_recognition not installed. Voice input disabled.")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[WARN] pyttsx3 not installed. Voice output disabled.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("[WARN] scikit-learn not installed. Using rule-based intent matching.")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS  ─ no global mutable state; all constants are immutable
# ══════════════════════════════════════════════════════════════════════════════

SPAM_KEYWORDS = (
    "buy now", "click here", "free offer", "win prize", "earn money fast",
    "limited time offer", "discount", "advertisement", "promo code",
    "you are a winner", "lottery", "casino", "gambling", "crypto investment",
    "make money online", "work from home offer", "hot singles", "adult content",
    "subscribe now", "unsubscribe", "weight loss pill", "dating site",
    "miracle cure", "get rich quick", "100% free", "no credit card needed"
)

DOMAIN_SPAM_PATTERNS = (
    "buy university degree", "fake diploma", "cheat in exam", "sell exam paper",
    "proxy attendance app", "homework for sale", "essay writing service ad"
)

INTENTS = {
    "Admission": [
        "admission", "apply", "application", "enroll", "enrollment", "entry test",
        "merit", "registration", "joining", "intake", "how to join", "requirements",
        "eligibility", "apply online", "form", "undergraduate", "graduate", "apply now"
    ],
    "Fee": [
        "fee", "fees", "charges", "cost", "tuition", "semester fee", "payment",
        "scholarship", "financial aid", "how much", "price", "pay", "amount",
        "dues", "installment", "bank challan", "fee structure", "waiver"
    ],
    "Courses": [
        "course", "courses", "subject", "subjects", "program", "programs",
        "curriculum", "syllabus", "degree", "bsse", "bscs", "ms", "phd",
        "computer science", "software engineering", "electrical", "elective",
        "credit hours", "course list", "what courses"
    ],
    "Schedule": [
        "schedule", "timetable", "time table", "class timing", "timings",
        "lecture", "exam", "mid term", "midterm", "final", "date sheet",
        "semester start", "semester end", "holiday", "break", "calendar", "when is class"
    ],
    "Faculty": [
        "faculty", "teacher", "professor", "instructor", "sir", "madam",
        "dr", "staff", "hod", "department head", "contact teacher", "office hours",
        "faculty contact", "staff list"
    ],
    "Library": [
        "library", "book", "books", "reading room", "digital library",
        "research paper", "journal", "borrow", "return book", "library hours",
        "ieee", "acm", "springer", "library card"
    ],
}

STATIC_RESPONSES = {
    "Admission": (
        "Admissions at ITU open twice a year. Applications are submitted online "
        "at itu.edu.pk/admissions. Selection is based on the ITU entry test and "
        "intermediate/A-level marks. Contact admissions@itu.edu.pk or visit the "
        "admissions office on campus for program-specific cutoffs and deadlines."
    ),
    "Fee": (
        "Tuition at ITU ranges from roughly PKR 60,000 to PKR 85,000 per semester "
        "depending on your program. Merit-based scholarships can cover 25% to 100% "
        "of fees, and need-based financial aid is also available. The finance office "
        "handles installment plans. Full details are at itu.edu.pk/finance."
    ),
    "Courses": (
        "ITU runs undergraduate programs in BSSE, BSCS, and BSEE, plus graduate "
        "programs including MS CS, MS EE, and PhD. A typical semester carries "
        "15-18 credit hours across 5-6 courses. The complete curriculum for each "
        "program is listed on the student portal at portal.itu.edu.pk."
    ),
    "Schedule": (
        "Semester timetables are posted on the ITU student portal at the start of "
        "each semester. Mid-term exams usually fall around Week 8 and finals in "
        "Week 16. The academic calendar with all holidays and exam dates is available "
        "on the portal and department notice boards."
    ),
    "Faculty": (
        "ITU faculty hold PhDs from universities worldwide. You can find names, "
        "emails, and office hours at itu.edu.pk/faculty. Department heads can also "
        "be contacted through the department office. Office hours are typically "
        "posted on classroom doors or the department portal page."
    ),
    "Library": (
        "The ITU library is open Monday to Friday 8 AM–10 PM and weekends 9 AM–5 PM. "
        "Students can borrow up to 3 books for two weeks. Digital resources such as "
        "IEEE Xplore, ACM Digital Library, and Springer are accessible via the library "
        "portal using your student credentials."
    ),
    "Unknown": (
        "Sorry, I could not understand your request. "
        "You can ask me about admissions, fees, courses, class schedules, "
        "faculty contacts, or library services."
    ),
}

DYNAMIC_OVERRIDES = {
    "bsse":       "For BSSE (BS Software Engineering): 4-year program, 8 semesters. ",
    "bscs":       "For BSCS (BS Computer Science): strong theory and applied computing. ",
    "ms":         "The MS program is 1.5-2 years with coursework and thesis tracks. ",
    "phd":        "The PhD program requires a research proposal and typically takes 3-5 years. ",
    "scholarship":"ITU merit scholarships can cover up to 100% of tuition for top students. ",
    "hostel":     "ITU has on-campus hostel facilities for both male and female students. ",
    "online":     "Online resources and registration are available at portal.itu.edu.pk. ",
    "contact":    "Reach ITU at info@itu.edu.pk or +92-42-35880007. ",
    "deadline":   "Check the academic calendar on the portal for all current deadlines. ",
}

EXIT_WORDS = frozenset(["exit", "quit", "bye", "goodbye", "stop", "close"])
SWITCH_WORDS = frozenset(["switch", "switch mode", "change mode", "text mode", "voice mode"])


# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 1 — SPAM DETECTION   (Ibrahim Sattar — BSSE23004)
# ══════════════════════════════════════════════════════════════════════════════

def is_basic_spam(query: str) -> bool:
    """
    T1 — Classify input as Spam or Not Spam using rule-based heuristics.

    Checks for known spam phrases, excessive punctuation, and ALL-CAPS text
    patterns common in unsolicited or malicious messages.

    Args:
        query: Raw input string from the user.

    Returns:
        True if the input matches spam heuristics, False otherwise.
    """
    q_lower = query.lower().strip()

    for phrase in SPAM_KEYWORDS:
        if phrase in q_lower:
            return True

    # Excessive exclamation marks or dollar signs
    if query.count("!") > 3 or query.count("$") > 1:
        return True

    # Heavy ALL-CAPS usage (>60% uppercase, non-trivial length)
    if len(query) > 8:
        upper_ratio = sum(1 for c in query if c.isupper()) / len(query)
        if upper_ratio > 0.60:
            return True

    return False


def is_domain_spam(query: str) -> bool:
    """
    T2 — Identify university-context spam (irrelevant ads, fake services).

    Checks for patterns specific to spam targeting a university audience,
    such as fake degree offers or proxy attendance services. Must correctly
    catch at least 5 predefined domain-specific spam patterns.

    Predefined spam cases this catches:
        1. "buy university degree"
        2. "fake diploma"
        3. "cheat in exam"
        4. "sell exam paper"
        5. "homework for sale"
        6. "proxy attendance app"
        7. "essay writing service ad"

    Args:
        query: Raw input string from the user.

    Returns:
        True if domain-specific spam is detected, False otherwise.
    """
    q_lower = query.lower().strip()
    for pattern in DOMAIN_SPAM_PATTERNS:
        if pattern in q_lower:
            return True
    return False


def is_university_relevant(query: str) -> bool:
    """
    Check whether the query relates to a university context.

    Scans for any intent keyword or general university vocabulary.
    Used as the second gate: even non-spam messages must be on-topic.

    Args:
        query: Raw input string.

    Returns:
        True if the query appears university-related, False otherwise.
    """
    q_lower = query.lower()

    general_university_words = (
        "university", "itu", "college", "campus", "student", "class",
        "semester", "academic", "department", "grade", "gpa", "portal",
        "hostel", "canteen", "lab", "project", "assignment", "thesis",
        "research", "exam", "degree", "lecture", "quiz", "result"
    )

    for word in general_university_words:
        if word in q_lower:
            return True

    for keywords in INTENTS.values():
        for kw in keywords:
            if kw in q_lower:
                return True

    return False


def check_spam(query: str) -> tuple:
    """
    Full spam detection pipeline (T1 + T2 + T3).

    Runs the query through basic spam detection, then domain-specific
    spam detection, then a domain-relevance check. If any stage flags
    the input, processing stops and a spam message is returned.

    T3 — If spam is detected, the system blocks further processing
    and returns: "This query is classified as spam."

    Args:
        query: The user's raw input text.

    Returns:
        Tuple of (is_spam: bool, message: str).
    """
    if is_basic_spam(query):
        return True, "This query is classified as spam."

    if is_domain_spam(query):
        return True, "This query is classified as spam."

    if not is_university_relevant(query):
        return True, "This query is classified as spam."

    return False, ""


# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 2 — INTENT IDENTIFICATION   (M.Hasham Khan — BSSE23053)
# ══════════════════════════════════════════════════════════════════════════════

def build_intent_classifier() -> tuple:
    """
    Build and return a trained TF-IDF + Naive Bayes intent classifier.

    Uses a broad set of training phrases (14+ per intent) to handle
    natural query variations robustly (T2). Falls back gracefully to
    (None, None) when scikit-learn is unavailable.

    Returns:
        Tuple of (trained Pipeline, class list) or (None, None).
    """
    if not ML_AVAILABLE:
        return None, None

    training_phrases = {
        "Admission": [
            "how do I apply for admission", "what are the admission requirements",
            "when does enrollment start", "how to apply online for bscs",
            "tell me about merit list", "entry test details for itu",
            "what is the registration deadline", "how to join itu lahore",
            "undergraduate application process", "graduate admission steps",
            "eligibility criteria for bsse", "is admission open right now",
            "documents required for admission", "how to submit my application",
        ],
        "Fee": [
            "what is the fee structure", "how much is the semester fee",
            "is there a scholarship available", "financial aid options at itu",
            "how to pay the semester dues", "fee installment plan details",
            "how much does bscs cost per semester", "bank challan for fee payment",
            "what are the tuition charges", "fee payment deadline this semester",
            "need based scholarship criteria", "fee concession process",
            "total cost of bsse degree", "are there any fee waivers",
        ],
        "Courses": [
            "what courses are offered at itu", "tell me about the curriculum",
            "what subjects are in semester 1", "bsse program course list",
            "what is the degree program structure", "phd in computer science details",
            "ms program overview at itu", "how many credit hours per semester",
            "elective courses available", "what programs does itu offer",
            "computer science subjects list", "software engineering curriculum",
            "is data science offered", "what is the course outline for cs301",
        ],
        "Schedule": [
            "when are the classes", "show me the class timetable",
            "mid term exam schedule this semester", "when does the semester start",
            "final exam date sheet", "holiday calendar for itu",
            "when does semester end", "class timings for bsse",
            "when is the quiz this week", "semester schedule overview",
            "exam schedule for spring 2026", "is there a break next week",
            "what day is the lecture", "when are midterms",
        ],
        "Faculty": [
            "who is the head of cs department", "contact information for professor",
            "faculty list for software engineering", "how to reach my teacher",
            "instructor email address", "dr asif contact details",
            "office hours of faculty members", "staff directory for itu",
            "who teaches data structures", "professor contact number",
        ],
        "Library": [
            "library opening hours", "how to borrow a book from library",
            "access to digital library resources", "ieee access for students",
            "return a borrowed book", "reading room availability at itu",
            "how to get a library card", "research paper access",
            "acm digital library login", "how many books can I borrow",
            "library timing on weekends", "springer journals access",
        ],
    }

    data, labels = [], []
    for intent, phrases in training_phrases.items():
        for phrase in phrases:
            data.append(phrase)
            labels.append(intent)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, min_df=1)),
        ("clf",   MultinomialNB(alpha=0.5)),
    ])
    pipeline.fit(data, labels)
    return pipeline, list(training_phrases.keys())


def identify_intent_rule_based(query: str) -> tuple:
    """
    Identify intent through keyword frequency matching (fallback method).

    Counts how many keywords from each intent category appear in the query.
    The intent with the highest count wins. Confidence is the proportion
    of keyword hits belonging to the winning intent.

    Args:
        query: The user's input text.

    Returns:
        Tuple of (intent: str, confidence: float).
    """
    q_lower = query.lower()
    scores = {intent: 0 for intent in INTENTS}

    for intent, keywords in INTENTS.items():
        for kw in keywords:
            if kw in q_lower:
                scores[intent] += 1

    best_intent = max(scores, key=scores.get)
    best_score  = scores[best_intent]

    if best_score == 0:
        return "Unknown", 0.0

    total      = sum(scores.values())
    confidence = round(best_score / total, 2) if total else 0.0
    return best_intent, confidence


def identify_intent(query: str, classifier) -> tuple:
    """
    Classify user query into one of 6 predefined university intents.

    T1 — Identifies: Admission, Fee, Courses, Schedule, Faculty, Library.
    T2 — Handles query variations (e.g. "charges", "cost", "tuition" → Fee)
         by combining TF-IDF ML classification with keyword-based fallback.
    T3 — Returns a confidence score alongside the detected intent label.

    Args:
        query:      The user's input text.
        classifier: Trained sklearn Pipeline (may be None).

    Returns:
        Tuple of (intent: str, confidence: float).
    """
    if classifier is not None and ML_AVAILABLE:
        try:
            probs    = classifier.predict_proba([query])[0]
            classes  = classifier.classes_
            best_idx = int(np.argmax(probs))
            intent   = classes[best_idx]
            conf     = round(float(probs[best_idx]), 2)

            # If ML is uncertain, check rule-based for confirmation
            if conf < 0.30:
                rb_intent, rb_conf = identify_intent_rule_based(query)
                if rb_conf > 0:
                    return rb_intent, rb_conf

            if conf < 0.15:
                return "Unknown", conf

            return intent, conf

        except Exception:
            pass  # Fall through to rule-based

    return identify_intent_rule_based(query)


# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 3 — RESPONSE GENERATION   (M.Abdullah Cheema — BSSE23091)
# ══════════════════════════════════════════════════════════════════════════════

def get_dynamic_prefix(query: str) -> str:
    """
    T2 — Scan the query for specific keywords and build a context prefix.

    Checks DYNAMIC_OVERRIDES for program names, topics, or modifiers that
    warrant a more targeted response. Multiple matches are concatenated.

    Args:
        query: The user's input text.

    Returns:
        A context string prepended to the static response, or empty string.
    """
    q_lower  = query.lower()
    additions = [text for kw, text in DYNAMIC_OVERRIDES.items() if kw in q_lower]
    return " ".join(additions)


def generate_response(intent: str, query: str, confidence: float) -> str:
    """
    Generate a meaningful, context-aware response for the given intent.

    T1 — Returns the predefined static response for each recognized intent.
    T2 — Prepends a dynamic keyword-based context if specific terms are found.
    T3 — Handles unrecognized queries gracefully with a fallback message:
         "Sorry, I could not understand your request."

    Args:
        intent:     The classified intent string from Module 2.
        query:      Original user query (used for keyword scanning in T2).
        confidence: Confidence score returned by the intent classifier.

    Returns:
        The final chatbot response string.
    """
    # T3 — Unknown or very low-confidence queries
    if intent == "Unknown" or confidence < 0.10:
        return STATIC_RESPONSES["Unknown"]

    # T1 — Base static response
    base = STATIC_RESPONSES.get(intent, STATIC_RESPONSES["Unknown"])

    # T2 — Dynamic prefix based on specific query keywords
    prefix = get_dynamic_prefix(query)

    return (prefix + base) if prefix else base


# ══════════════════════════════════════════════════════════════════════════════
#  MODULE 4 — VOICE INTERACTION   (Shared across team)
# ══════════════════════════════════════════════════════════════════════════════

def speech_to_text() -> object:
    """
    T1 — Capture microphone audio and convert it to text using Google STT.

    Adjusts for ambient noise, listens with a 10-second timeout, then
    sends audio to Google Speech Recognition. Recognized text is displayed
    on screen before any further processing.

    Returns:
        Recognized text string, or None if recognition fails for any reason.
    """
    if not STT_AVAILABLE:
        print("[STT] SpeechRecognition library is not installed.")
        return None

    recognizer = sr.Recognizer()
    recognizer.pause_threshold   = 1.0
    recognizer.energy_threshold  = 300

    try:
        with sr.Microphone() as source:
            print("\n[STT] Calibrating microphone... please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[STT] Listening — speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)

        print("[STT] Processing your speech...")
        text = recognizer.recognize_google(audio)
        print(f'[STT] Recognized: "{text}"')
        return text

    except sr.WaitTimeoutError:
        print("[STT] No speech detected. Please try again.")
    except sr.UnknownValueError:
        print("[STT] Could not understand audio. Please speak clearly.")
    except sr.RequestError as exc:
        print(f"[STT] Recognition service error: {exc}")
    except OSError:
        print("[STT] Microphone is not accessible on this device.")

    return None


def text_to_speech(text: str) -> None:
    """
    T2 — Convert a response string to spoken audio via pyttsx3.

    Uses an offline TTS engine so no internet connection is required.
    Speech rate is set to 160 WPM and volume to 90% for clarity.
    A fresh engine instance is created each call to avoid state leakage.

    Args:
        text: The chatbot response to be spoken aloud.
    """
    if not TTS_AVAILABLE:
        print("[TTS] pyttsx3 is not installed. Skipping audio output.")
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate",   160)
        engine.setProperty("volume", 0.9)

        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)

        print("[TTS] Speaking...")
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as exc:
        print(f"[TTS] Could not produce speech output: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
#  CORE PROCESSING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def process_query(query: str, classifier, use_tts: bool) -> None:
    """
    Run a single user query through the full chatbot pipeline.

    Pipeline order:
        1. Spam Detection  (Module 1) — blocks spam immediately
        2. Intent ID       (Module 2) — classifies the query
        3. Response Gen    (Module 3) — produces the reply
        4. TTS Output      (Module 4) — speaks the reply if voice mode

    Args:
        query:      User's input text (typed or speech-recognized).
        classifier: Trained intent classifier (or None for rule-based).
        use_tts:    If True, response is also spoken via TTS.
    """
    divider = "─" * 56
    print(f"\n{divider}")
    print(f"  Input   : {query}")

    # ── Module 1: Spam Detection ──
    spam, spam_msg = check_spam(query)
    if spam:
        print(f"  Status  : SPAM DETECTED")
        print(f"\n  {spam_msg}")
        if use_tts:
            text_to_speech(spam_msg)
        print(divider)
        return

    # ── Module 2: Intent Identification ──
    intent, confidence = identify_intent(query, classifier)
    print(f"  Intent  : {intent}   |   Confidence: {confidence:.0%}")

    # ── Module 3: Response Generation ──
    response = generate_response(intent, query, confidence)
    print(f"\n  Chatbot : {response}")

    # ── Module 4: TTS (voice/hybrid modes only) ──
    if use_tts:
        text_to_speech(response)

    print(divider)


# ══════════════════════════════════════════════════════════════════════════════
#  EXIT KEY SETUP
# ══════════════════════════════════════════════════════════════════════════════

def setup_esc_exit(exit_event: threading.Event) -> None:
    """
    Register a background ESC key listener that signals the main loop to stop.

    Uses the keyboard library when available. If keyboard is not installed,
    the user can still exit by typing 'exit' or 'quit'.

    Args:
        exit_event: A threading.Event set when ESC is pressed.
    """
    if KEYBOARD_AVAILABLE:
        try:
            keyboard.add_hotkey("esc", exit_event.set)
            print("[INFO] Press ESC at any time to exit the chatbot.")
            return
        except Exception:
            pass
    print("[INFO] Type 'exit' or 'quit' to stop the chatbot.")


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT MODES
# ══════════════════════════════════════════════════════════════════════════════

def run_text_mode(classifier, exit_event: threading.Event) -> None:
    """
    Text Input Mode — continuous typed interaction via the console.

    Suitable for testing spam detection, intent classification, and
    response generation without a microphone. User types queries one
    at a time; the chatbot responds immediately. Loop exits on ESC,
    'exit', or 'quit'.

    Args:
        classifier: Trained intent classifier Pipeline (or None).
        exit_event: Threading event that signals when to exit.
    """
    print("\n[TEXT MODE] Type your university question and press Enter.")

    while not exit_event.is_set():
        try:
            query = input("\n  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            exit_event.set()
            break

        if not query:
            continue

        if query.lower() in EXIT_WORDS:
            exit_event.set()
            break

        process_query(query, classifier, use_tts=False)


def run_voice_mode(classifier, exit_event: threading.Event) -> None:
    """
    Voice Input Mode — microphone-based interaction with TTS responses.

    T3 (Integrated Voice Flow): Captures audio → converts to text →
    runs full processing pipeline → speaks the response aloud.
    Falls back to text mode if SpeechRecognition is unavailable.
    Say 'exit' or 'quit' to stop.

    Args:
        classifier: Trained intent classifier Pipeline (or None).
        exit_event: Threading event that signals when to exit.
    """
    if not STT_AVAILABLE:
        print("[VOICE] SpeechRecognition not found. Switching to text mode.")
        run_text_mode(classifier, exit_event)
        return

    print("\n[VOICE MODE] Speak your university question.")
    print("[INFO] Say 'exit' or 'quit' to stop, or press ESC.")

    while not exit_event.is_set():
        query = speech_to_text()

        if query is None:
            print("[VOICE] Could not capture input — please try again.")
            continue

        if query.lower() in EXIT_WORDS:
            exit_event.set()
            break

        process_query(query, classifier, use_tts=True)


def run_hybrid_mode(classifier, exit_event: threading.Event) -> None:
    """
    Hybrid Mode — seamless switching between text and voice input.

    Starts in text mode by default. Type 'switch' to jump to voice,
    and say 'switch' (or type it as a fallback) to return to text.
    Both modes feed the same processing pipeline, and voice mode
    includes TTS responses. Type or say 'exit' to stop.

    Args:
        classifier: Trained intent classifier Pipeline (or None).
        exit_event: Threading event that signals when to exit.
    """
    print("\n[HYBRID MODE] Starting in text mode.")
    print("[INFO] Type 'switch' to toggle voice input, 'exit' to quit.")

    current_mode = "text"

    while not exit_event.is_set():
        label = "[TEXT]" if current_mode == "text" else "[VOICE]"

        if current_mode == "text":
            try:
                raw = input(f"\n  {label} You: ").strip()
            except (EOFError, KeyboardInterrupt):
                exit_event.set()
                break

            if not raw:
                continue

            if raw.lower() in EXIT_WORDS:
                exit_event.set()
                break

            if raw.lower() in SWITCH_WORDS:
                if STT_AVAILABLE:
                    current_mode = "voice"
                    print("[HYBRID] Switched to voice mode.")
                else:
                    print("[HYBRID] Voice unavailable — staying in text mode.")
                continue

            process_query(raw, classifier, use_tts=False)

        else:  # voice mode
            print(f"\n  {label} Listening... (say 'switch' to return to text)")
            query = speech_to_text()

            if query is None:
                print("[HYBRID] No voice input captured.")
                try:
                    fb = input("  Type 'switch' to return to text mode: ").strip()
                    if fb.lower() in SWITCH_WORDS:
                        current_mode = "text"
                except (EOFError, KeyboardInterrupt):
                    exit_event.set()
                    break
                continue

            if query.lower() in EXIT_WORDS:
                exit_event.set()
                break

            if query.lower() in SWITCH_WORDS:
                current_mode = "text"
                print("[HYBRID] Switched to text mode.")
                continue

            process_query(query, classifier, use_tts=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MENU & MAIN ENTRY POINT   (M.Abdullah Cheema — BSSE23091)
# ══════════════════════════════════════════════════════════════════════════════

def display_banner() -> None:
    """Print the application startup banner with group information."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║       ITU MULTI-MODAL UNIVERSITY CHATBOT — HCI Assignment 5     ║
║    SE305T & MD445T  |  Spring 2026  |  Dr. Muhammad Asif        ║
╠══════════════════════════════════════════════════════════════════╣
║  Ibrahim Sattar      BSSE23004                                   ║
║  M.Hasham Khan       BSSE23053                                   ║
║  M.Abdullah Cheema   BSSE23091                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Features: Spam Detection | Intent ID | Voice I/O | Hybrid      ║
╚══════════════════════════════════════════════════════════════════╝""")


def display_menu() -> str:
    """
    Display the mode-selection menu and return the user's validated choice.

    Runs a validation loop until the user enters '1', '2', or '3'.

    Returns:
        The user's choice as a single character string: '1', '2', or '3'.
    """
    print("""
┌──────────────── SELECT INPUT MODE ────────────────┐
│  1. Text Mode   — Type your queries               │
│  2. Voice Mode  — Speak your queries              │
│  3. Hybrid Mode — Switch between text & voice     │
└───────────────────────────────────────────────────┘""")

    while True:
        choice = input("  Enter choice (1 / 2 / 3): ").strip()
        if choice in ("1", "2", "3"):
            return choice
        print("  [ERROR] Please enter 1, 2, or 3.")


def main() -> None:
    """
    Application entry point for the ITU University Chatbot System.

    Displays the startup banner, builds the intent classifier, registers
    the ESC key listener, then enters the main menu-driven loop. The loop
    continues until the user exits via ESC or by typing 'exit'/'quit'.

    No global mutable variables are used; all state is passed explicitly
    as function arguments.
    """
    display_banner()

    # ── Initialise the intent classifier ──
    print("\n[INIT] Building intent classifier...")
    classifier, _ = build_intent_classifier()
    if classifier is not None:
        print("[INIT] ML classifier (TF-IDF + Naive Bayes) is ready.")
    else:
        print("[INIT] Using keyword-based rule matching.")

    # ── Set up ESC exit handler ──
    exit_event = threading.Event()
    setup_esc_exit(exit_event)

    # ── Main menu loop ──
    while not exit_event.is_set():
        choice = display_menu()

        if choice == "1":
            run_text_mode(classifier, exit_event)
        elif choice == "2":
            run_voice_mode(classifier, exit_event)
        elif choice == "3":
            run_hybrid_mode(classifier, exit_event)

        if exit_event.is_set():
            break

        try:
            again = input("\n[MENU] Return to mode selection? (y / n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if again != "y":
            break

    print("\n[EXIT] Thank you for using the ITU University Chatbot. Goodbye!\n")
    sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
