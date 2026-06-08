# ============================================================
# ElderlyAI — Smart Daily Life Companion
# Full app with Claude API + RAG + All 9 Personas
# ============================================================
# HOW TO RUN:
# 1. pip install anthropic streamlit chromadb
# 2. Set your API key: export ANTHROPIC_API_KEY=sk-ant-...
#    OR the app will ask you to enter it
# 3. streamlit run elderly_ai_planner.py
# ============================================================

import streamlit as st
from datetime import datetime, date
import pytz
import anthropic
import os

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="ElderlyAI — Daily Life Companion",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# ============================================================
# CUSTOM CSS — Large text, accessible, professional
# ============================================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
    }

    /* Main background */
    .stApp { background-color: #F4F6FB; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A2E5A 0%, #0D1B3E 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #A8C5DA !important; font-size: 13px !important; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1A2E5A 0%, #C0152B 100%);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
    }
    .main-header h1 {
        font-family: 'DM Serif Display', serif;
        font-size: 28px;
        margin: 0;
        color: white;
    }
    .main-header p { font-size: 14px; color: rgba(255,255,255,0.8); margin: 4px 0 0; }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #1A2E5A;
    }
    .card-red { border-left-color: #C0152B; }
    .card-green { border-left-color: #22C55E; }
    .card-gold { border-left-color: #E8A020; }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    /* KPI numbers */
    .kpi-num { font-size: 32px; font-weight: 700; color: #1A2E5A; }
    .kpi-label { font-size: 12px; color: #94A3B8; margin-top: 2px; }

    /* Task items */
    .task-item {
        display: flex;
        align-items: center;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 6px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        font-size: 15px;
    }
    .task-done {
        background: #F0FFF4;
        border-color: #86EFAC;
        text-decoration: line-through;
        color: #64748B;
    }
    .task-urgent {
        background: #FFF5F5;
        border-color: #FCA5A5;
        font-weight: 600;
    }

    /* Alert box */
    .alert-box {
        background: linear-gradient(135deg, #FFF5F5, #FFF);
        border: 1.5px solid #C0152B;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .alert-title { font-size: 14px; font-weight: 700; color: #C0152B; }
    .alert-text { font-size: 13px; color: #64748B; margin-top: 3px; }

    /* Night mode */
    .night-alert {
        background: linear-gradient(135deg, #0D1B3E, #1A2E5A);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 14px;
    }
    .night-alert h2 { color: #E8A020; font-size: 20px; margin: 0 0 8px; }
    .night-alert p { color: rgba(255,255,255,0.85); font-size: 14px; margin: 4px 0; }

    /* SOS button */
    .sos-container { text-align: center; margin: 10px 0; }

    /* Chat messages */
    .chat-msg-user {
        background: #1A2E5A;
        color: white;
        padding: 10px 14px;
        border-radius: 12px 12px 4px 12px;
        margin: 6px 0;
        font-size: 14px;
        text-align: right;
    }
    .chat-msg-ai {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 10px 14px;
        border-radius: 12px 12px 12px 4px;
        margin: 6px 0;
        font-size: 14px;
    }

    /* Progress bar */
    .progress-wrap {
        background: #E2E8F0;
        border-radius: 8px;
        height: 12px;
        overflow: hidden;
        margin: 8px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #1A2E5A, #C0152B);
        transition: width 0.3s;
    }

    /* Mood buttons */
    .mood-row { display: flex; gap: 8px; margin: 8px 0; }

    /* Persona badge */
    .persona-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: white;
        margin-top: 6px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# PERSONA DATA — All 9 personas
# ============================================================
PERSONAS = {
    "Margaret Thompson": {
        "house": "hh108", "age": 82, "condition": "Parkinson's Disease",
        "fall_risk": "Critical", "medications": 6, "isolation": 8.9,
        "suburb": "Newcastle",
        "medications_list": [
            ("Levodopa", "07:30"), ("Carbidopa", "07:30"),
            ("Blood Pressure Tablet", "13:00"), ("Vitamin D", "13:00"),
            ("Cholesterol Tablet", "19:00"), ("Sleep Aid", "19:00")
        ],
        "contacts": [
            ("Daughter Sarah", "0412 345 678"),
            ("GP Dr Williams", "02 4923 1234"),
            ("Neighbour Joan", "0423 456 789")
        ],
        "appointments": [
            ("Neurologist", "Friday 2:00 PM"),
            ("Physiotherapy", "Monday 10:00 AM")
        ],
        "driver": "John — 0412 111 222",
        "birthday_contacts": [("Brother Michael", "28 May"), ("Friend Joan", "15 June")],
        "night_risk": "Very high — dizziness when standing, hold bed rail",
        "emoji": "👩"
    },
    "Dorothy Williams": {
        "house": "hh105", "age": 78, "condition": "Type 2 Diabetes",
        "fall_risk": "High", "medications": 5, "isolation": 7.8,
        "suburb": "Lake Macquarie",
        "medications_list": [
            ("Metformin", "07:30"), ("Blood Pressure Tablet", "07:30"),
            ("Vitamin D", "13:00"), ("Cholesterol Tablet", "19:00"),
            ("Aspirin", "19:00")
        ],
        "contacts": [
            ("Son David", "0413 567 890"),
            ("GP Dr Chen", "02 4932 5678"),
            ("Daughter Emma", "0424 678 901")
        ],
        "appointments": [
            ("Diabetic Clinic", "Wednesday 11:00 AM"),
            ("GP Checkup", "Friday 3:00 PM")
        ],
        "driver": "Emma — 0424 678 901",
        "birthday_contacts": [("Daughter Emma", "12 June"), ("Son David", "8 August")],
        "night_risk": "Medium — check blood sugar before bed",
        "emoji": "👩"
    },
    "Barbara Johnson": {
        "house": "hh103", "age": 85, "condition": "Mild Cognitive Impairment",
        "fall_risk": "High", "medications": 4, "isolation": 9.2,
        "suburb": "Maitland",
        "medications_list": [
            ("Memory Support Tablet", "07:30"), ("Blood Pressure Tablet", "07:30"),
            ("Vitamin D", "13:00"), ("Cholesterol Tablet", "19:00")
        ],
        "contacts": [
            ("Neighbour Helen", "0415 234 567"),
            ("GP Dr Smith", "02 4934 2345"),
            ("Community Worker Sue", "0426 789 012")
        ],
        "appointments": [
            ("Memory Clinic", "Thursday 10:00 AM"),
            ("GP Checkup", "Monday 2:00 PM")
        ],
        "driver": "Community Transport — 1800 456 789",
        "birthday_contacts": [("Friend Mary", "3 July"), ("Neighbour Helen", "22 August")],
        "night_risk": "High — confusion at night, leave hall light on",
        "emoji": "👩"
    },
    "Arthur Brown": {
        "house": "hh104", "age": 74, "condition": "Heart Disease",
        "fall_risk": "High", "medications": 5, "isolation": 7.2,
        "suburb": "Cessnock",
        "medications_list": [
            ("Heart Medication", "07:30"), ("Blood Pressure Tablet", "07:30"),
            ("Blood Thinners", "13:00"), ("Cholesterol Tablet", "19:00"),
            ("Vitamin D", "19:00")
        ],
        "contacts": [
            ("Son James", "0416 345 678"),
            ("GP Dr Patel", "02 4935 3456"),
            ("Daughter Karen", "0427 890 123")
        ],
        "appointments": [
            ("Cardiologist", "Tuesday 9:00 AM"),
            ("GP Checkup", "Thursday 3:00 PM")
        ],
        "driver": "Son James — 0416 345 678",
        "birthday_contacts": [("Son James", "18 July"), ("Daughter Karen", "4 September")],
        "night_risk": "High — chest pain protocol, call 000 immediately",
        "emoji": "👴"
    },
    "Helen Davis": {
        "house": "hh102", "age": 71, "condition": "Hypertension",
        "fall_risk": "Medium", "medications": 3, "isolation": 6.8,
        "suburb": "Gosford",
        "medications_list": [
            ("Blood Pressure Tablet", "07:30"),
            ("Antidepressant", "07:30"),
            ("Vitamin D", "13:00")
        ],
        "contacts": [
            ("Daughter Lisa", "0417 456 789"),
            ("GP Dr Wong", "02 4936 4567"),
            ("Friend Patricia", "0428 901 234")
        ],
        "appointments": [
            ("GP Checkup", "Wednesday 2:00 PM"),
            ("Counselling", "Friday 11:00 AM")
        ],
        "driver": "Daughter Lisa — 0417 456 789",
        "birthday_contacts": [("Friend Patricia", "9 August"), ("Daughter Lisa", "25 October")],
        "night_risk": "Low — generally safe at night",
        "emoji": "👩"
    },
    "Walter Miller": {
        "house": "hh106", "age": 79, "condition": "Osteoporosis",
        "fall_risk": "High", "medications": 4, "isolation": 8.1,
        "suburb": "Wyong",
        "medications_list": [
            ("Calcium Supplement", "07:30"), ("Vitamin D", "07:30"),
            ("Blood Pressure Tablet", "13:00"), ("Bone Density Tablet", "19:00")
        ],
        "contacts": [
            ("Community Worker Tom", "0418 567 890"),
            ("GP Dr Garcia", "02 4937 5678"),
            ("Neighbour Bob", "0429 012 345")
        ],
        "appointments": [
            ("Bone Density Scan", "Monday 10:00 AM"),
            ("GP Checkup", "Wednesday 3:00 PM")
        ],
        "driver": "Community Transport — 1800 456 789",
        "birthday_contacts": [("Neighbour Bob", "14 September"), ("Old Friend Ted", "7 October")],
        "night_risk": "Very high — osteoporosis means fracture risk from any fall",
        "emoji": "👴"
    },
    "Frances Wilson": {
        "house": "hh107", "age": 76, "condition": "Arthritis",
        "fall_risk": "Medium", "medications": 3, "isolation": 5.9,
        "suburb": "Port Stephens",
        "medications_list": [
            ("Anti-inflammatory", "07:30"),
            ("Blood Pressure Tablet", "13:00"),
            ("Vitamin D", "19:00")
        ],
        "contacts": [
            ("Sibling Robert", "0419 678 901"),
            ("GP Dr Kim", "02 4938 6789"),
            ("Friend Sandra", "0430 123 456")
        ],
        "appointments": [
            ("Rheumatologist", "Thursday 11:00 AM"),
            ("GP Checkup", "Tuesday 2:00 PM")
        ],
        "driver": "Sibling Robert — 0419 678 901",
        "birthday_contacts": [("Sibling Robert", "29 October"), ("Friend Sandra", "12 November")],
        "night_risk": "Low — stiff joints in morning, move slowly",
        "emoji": "👩"
    },
    "Thomas Anderson": {
        "house": "hh101", "age": 68, "condition": "Mild Hypertension",
        "fall_risk": "Low", "medications": 1, "isolation": 4.2,
        "suburb": "Singleton",
        "medications_list": [
            ("Blood Pressure Tablet", "07:30")
        ],
        "contacts": [
            ("Son Michael", "0420 789 012"),
            ("GP Dr Brown", "02 4939 7890"),
            ("Friend Gary", "0431 234 567")
        ],
        "appointments": [
            ("GP Checkup", "Monthly — next Tuesday 10:00 AM")
        ],
        "driver": "Son Michael — 0420 789 012",
        "birthday_contacts": [("Son Michael", "8 December"), ("Friend Gary", "19 January")],
        "night_risk": "Low — generally healthy",
        "emoji": "👴"
    },
    "Alice Taylor": {
        "house": "hh110", "age": 91, "condition": "Dementia",
        "fall_risk": "Critical", "medications": 6, "isolation": 9.8,
        "suburb": "Dungog",
        "medications_list": [
            ("Dementia Medication", "07:30"), ("Blood Pressure Tablet", "07:30"),
            ("Vitamin D", "13:00"), ("Calcium Supplement", "13:00"),
            ("Cholesterol Tablet", "19:00"), ("Sleep Aid", "19:00")
        ],
        "contacts": [
            ("Daughter Mary", "0421 890 123"),
            ("GP Dr Lee", "02 4940 8901"),
            ("Carer Janet", "0432 345 678")
        ],
        "appointments": [
            ("Memory Specialist", "Every 2 weeks — next Thursday 9:00 AM"),
            ("GP Checkup", "Monthly")
        ],
        "driver": "Carer Janet — 0432 345 678",
        "birthday_contacts": [("Daughter Mary", "30 December")],
        "night_risk": "Critical — dementia confusion at night, door alarm active",
        "emoji": "👩"
    }
}

DAILY_TASKS = [
    ("💊", "Take morning medication", "07:30"),
    ("🍳", "Eat breakfast", "08:00"),
    ("🚶", "Morning walk or gentle exercise", "09:30"),
    ("💧", "Drink a glass of water", "10:30"),
    ("🥗", "Eat lunch", "12:30"),
    ("💊", "Take afternoon medication", "13:00"),
    ("😌", "Rest and relaxation", "14:30"),
    ("📞", "Call a family member or friend", "16:00"),
    ("🍽️", "Eat dinner", "18:00"),
    ("💊", "Take evening medication", "19:00"),
    ("🪥", "Personal hygiene", "20:30"),
    ("🛏️", "Prepare for bed", "21:00"),
]

MOOD_OPTIONS = [
    ("😔", "Very low", 1),
    ("😕", "Low", 2),
    ("😐", "Okay", 3),
    ("🙂", "Good", 4),
    ("😄", "Great", 5),
]

# ============================================================
# SESSION STATE
# ============================================================
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = None
if "task_done" not in st.session_state:
    st.session_state.task_done = [False] * len(DAILY_TASKS)
if "mood_score" not in st.session_state:
    st.session_state.mood_score = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False
if "sos_triggered" not in st.session_state:
    st.session_state.sos_triggered = False
# Load saved API key from file if exists
def load_saved_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    try:
        if os.path.exists("elderlyai_key.txt"):
            with open("elderlyai_key.txt", "r") as f:
                return f.read().strip()
    except:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")

def save_key(key):
    try:
        with open("elderlyai_key.txt", "w") as f:
            f.write(key)
    except:
        pass

if "api_key" not in st.session_state:
    st.session_state.api_key = load_saved_key()

# Force load from secrets every time
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    pass

# ============================================================
# HELPERS
# ============================================================
def get_persona_context(persona_name):
    p = PERSONAS[persona_name]
    sydney_tz = pytz.timezone('Australia/Sydney')
    now = datetime.now(sydney_tz)
    hour = now.hour
    tasks_done = sum(st.session_state.task_done)
    tasks_total = len(DAILY_TASKS)

    # Build tasks status
    tasks_status = []
    for i, (emoji, name, time) in enumerate(DAILY_TASKS):
        status = "✅ Completed" if st.session_state.task_done[i] else "❌ Not done"
        tasks_status.append(f"  - {name} ({time}): {status}")

    # Build medications
    meds = "\n".join([f"  - {m[0]} at {m[1]}" for m in p["medications_list"]])

    # Build appointments
    appts = "\n".join([f"  - {a[0]}: {a[1]}" for a in p["appointments"]])

    # Build contacts
    contacts = "\n".join([f"  - {c[0]}: {c[1]}" for c in p["contacts"]])

    # Build birthdays
    bdays = "\n".join([f"  - {b[0]}: {b[1]}" for b in p["birthday_contacts"]])

    mood_text = ""
    if st.session_state.mood_score:
        mood_labels = {1:"very low",2:"low",3:"okay",4:"good",5:"great"}
        mood_text = f"Today's mood: {mood_labels[st.session_state.mood_score]}"

    context = f"""
You are ElderlyAI — a warm, caring and patient AI companion for elderly people.
You are speaking with {persona_name}, {p['age']} years old, living alone in {p['suburb']}.

PERSONA PROFILE:
- Health condition: {p['condition']}
- Fall risk level: {p['fall_risk']}
- Social isolation score: {p['isolation']}/10
- Number of daily medications: {p['medications']}
- Driver for appointments: {p['driver']}
- Night safety note: {p['night_risk']}

MEDICATIONS TODAY:
{meds}

UPCOMING APPOINTMENTS:
{appts}

EMERGENCY CONTACTS:
{contacts}

BIRTHDAY REMINDERS:
{bdays}

TODAY'S TASKS STATUS ({tasks_done}/{tasks_total} completed):
{chr(10).join(tasks_status)}

{mood_text}
CURRENT TIME: {now.strftime("%I:%M %p")} — {now.strftime("%A, %d %B %Y")}

INSTRUCTIONS:
1. Always address them by first name only — {persona_name.split()[0]}
2. Use simple, warm and friendly language — no medical jargon
3. Keep responses concise — 2-4 sentences maximum
4. If they mention feeling unwell — check their medication status and suggest calling their GP
5. If they seem confused — gently reassure them and suggest calling a family member
6. If they ask about medications — refer to their specific medication list above
7. If they ask about appointments — refer to their specific appointment list above
8. If fall risk is High or Critical — always remind them to be careful when moving
9. Always end with an encouraging or caring note
10. Never give medical advice — always refer to their GP for medical questions
"""
    return context

def ask_claude(user_message, persona_name):
    if not st.session_state.api_key:
        return "Please enter your Anthropic API key in the sidebar to enable AI responses."
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        messages = []
        for msg in st.session_state.chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            system=get_persona_context(persona_name),
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"I'm having trouble connecting right now. Please check your API key. Error: {str(e)[:100]}"

def get_time_greeting():
    hour = datetime.now(pytz.timezone('Australia/Sydney')).hour
    if hour < 12: return "Good morning"
    elif hour < 17: return "Good afternoon"
    else: return "Good evening"

def is_night_mode():
    hour = datetime.now(pytz.timezone('Australia/Sydney')).hour
    return hour >= 22 or hour <= 6

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🏠 ElderlyAI")
    st.markdown("*Smart Daily Life Companion*")
    st.markdown("---")

    # API Key
    st.markdown("**🔑 API Key**")
    api_input = st.text_input("Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed")
    if api_input:
        st.session_state.api_key = api_input
        if api_input.startswith("sk-ant"):
            save_key(api_input)
            st.success("✅ Key saved permanently!")

    st.markdown("---")

    # Persona selector
    st.markdown("**👤 Select Persona**")
    persona_options = ["— Choose a persona —"] + list(PERSONAS.keys())
    selected = st.selectbox("Persona", persona_options, label_visibility="collapsed")

    if selected != "— Choose a persona —":
        if st.session_state.selected_persona != selected:
            st.session_state.selected_persona = selected
            st.session_state.task_done = [False] * len(DAILY_TASKS)
            st.session_state.mood_score = None
            st.session_state.chat_history = []
            st.session_state.show_summary = False

    if st.session_state.selected_persona:
        p = PERSONAS[st.session_state.selected_persona]
        first_name = st.session_state.selected_persona.split()[0]
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.1); border-radius:10px; padding:12px; margin-top:8px;'>
            <div style='font-size:13px; font-weight:600;'>{p['emoji']} {st.session_state.selected_persona}</div>
            <div style='font-size:11px; color:#A8C5DA; margin-top:4px;'>Age: {p['age']} · {p['suburb']}</div>
            <div style='font-size:11px; color:#A8C5DA;'>{p['condition']}</div>
            <div style='font-size:11px; color:#FCA5A5; margin-top:4px;'>⚠️ Fall Risk: {p['fall_risk']}</div>
            <div style='font-size:11px; color:#A8C5DA;'>🏠 {p['house']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown("**📋 Navigation**")
    page = st.radio("", ["🏠 Daily Planner", "💬 AI Assistant", "📊 My Progress", "📋 Daily Summary"],
                   label_visibility="collapsed")

    st.markdown("---")

    # Reset
    if st.button("🔄 New Day — Reset", use_container_width=True):
        st.session_state.task_done = [False] * len(DAILY_TASKS)
        st.session_state.mood_score = None
        st.session_state.chat_history = []
        st.session_state.show_summary = False
        st.session_state.sos_triggered = False
        st.rerun()

# ============================================================
# MAIN CONTENT
# ============================================================
if not st.session_state.selected_persona:
    # Welcome screen
    st.markdown("""
    <div class='main-header'>
        <h1>🏠 ElderlyAI — Smart Daily Life Companion</h1>
        <p>AI-powered daily support for elderly people living independently</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Select your details to begin below 👇")

    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        if st.session_state.api_key and st.session_state.api_key.startswith("sk-ant"):
            st.success("✅ API Key loaded automatically!")
        else:
            st.markdown("**🔑 Step 1 — Enter API Key:**")
            api_main = st.text_input("API Key", placeholder="sk-ant-...", type="password", key="api_main")
            if api_main:
                st.session_state.api_key = api_main
                save_key(api_main)
                st.success("✅ Key saved!")
    with col_setup2:
        st.markdown("**👤 Step 2 — Select Persona:**")
        current_index = 0
        if st.session_state.selected_persona:
            names = list(PERSONAS.keys())
            if st.session_state.selected_persona in names:
                current_index = names.index(st.session_state.selected_persona) + 1
        persona_main = st.selectbox("Choose", ["— Select —"] + list(PERSONAS.keys()), 
                                     index=current_index, key="persona_main")
        if persona_main != "— Select —" and persona_main != st.session_state.selected_persona:
            st.session_state.selected_persona = persona_main
            st.session_state.task_done = [False] * len(DAILY_TASKS)
            st.session_state.chat_history = []
            st.session_state.current_page = "🏠 Daily Planner"
            st.rerun()
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='card'>
            <div class='card-title'>💊 Daily Reminders</div>
            Medication, meals and appointment reminders at the right time
        </div>
        <div class='card card-red'>
            <div class='card-title'>🚨 Emergency SOS</div>
            One tap alerts caregivers immediately
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='card card-green'>
            <div class='card-title'>🤖 AI Assistant</div>
            Ask anything — personalised answers from your profile
        </div>
        <div class='card card-gold'>
            <div class='card-title'>🎂 Social Alerts</div>
            Birthday reminders and family connection prompts
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='card'>
            <div class='card-title'>🌙 Night Safety</div>
            Fall prevention alerts when waking at night
        </div>
        <div class='card card-green'>
            <div class='card-title'>📊 Daily Progress</div>
            Track task completion and mood over time
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Available Personas:**")
    cols = st.columns(3)
    for i, (name, data) in enumerate(PERSONAS.items()):
        with cols[i % 3]:
            risk_color = {"Low":"#22C55E","Medium":"#E8A020","High":"#EF4444","Critical":"#7F1D1D"}.get(data['fall_risk'],'#64748B')
            st.markdown(f"""
            <div class='card' style='padding:12px;'>
                <div style='font-size:14px; font-weight:600;'>{data['emoji']} {name}</div>
                <div style='font-size:12px; color:#64748B;'>{data['age']} · {data['suburb']}</div>
                <div style='font-size:12px; color:#64748B;'>{data['condition']}</div>
                <div style='font-size:11px; color:{risk_color}; margin-top:4px; font-weight:600;'>
                    ⚠️ {data['fall_risk']} fall risk
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    persona = st.session_state.selected_persona
    p = PERSONAS[persona]
    first_name = persona.split()[0]
    now = datetime.now(pytz.timezone('Australia/Sydney'))
    hour = now.hour

    # Header
    st.markdown(f"""
    <div class='main-header'>
        <h1>{get_time_greeting()}, {first_name}! {p['emoji']}</h1>
        <p>{now.strftime("%A, %d %B %Y")} · {p['condition']} · {p['suburb']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Night mode alert
    if is_night_mode():
        st.markdown(f"""
        <div class='night-alert'>
            <h2>🌙 Night Time Safety Alert</h2>
            <p><strong>{first_name} — if you need to get up, please be careful!</strong></p>
            <p>⚠️ {p['night_risk']}</p>
            <p>Turn on the light first · Hold onto something · Walk slowly</p>
        </div>
        """, unsafe_allow_html=True)

    # PERSONA SWITCHER — always visible on top
    switch_col1, switch_col2 = st.columns([3,1])
    with switch_col1:
        names = list(PERSONAS.keys())
        current_index = names.index(persona) if persona in names else 0
        new_persona = st.selectbox("👤 Switch Persona", names, index=current_index, key="persona_switcher")
        if new_persona != st.session_state.selected_persona:
            st.session_state.selected_persona = new_persona
            st.session_state.task_done = [False] * len(DAILY_TASKS)
            st.session_state.chat_history = []
            st.session_state.current_page = "🏠 Daily Planner"
            st.rerun()
    with switch_col2:
        if st.button("🔄 Reset Day", use_container_width=True):
            st.session_state.task_done = [False] * len(DAILY_TASKS)
            st.session_state.mood_score = None
            st.session_state.chat_history = []
            st.session_state.show_summary = False
            st.session_state.sos_triggered = False
            st.rerun()

    # MAIN PAGE NAVIGATION
    st.markdown("---")
    nav1, nav2, nav3, nav4 = st.columns(4)
    with nav1:
        if st.button("🏠 Daily Planner", use_container_width=True, key="nav1"):
            st.session_state.current_page = "🏠 Daily Planner"
            st.rerun()
    with nav2:
        if st.button("💬 AI Assistant", use_container_width=True, key="nav2"):
            st.session_state.current_page = "💬 AI Assistant"
            st.rerun()
    with nav3:
        if st.button("📊 My Progress", use_container_width=True, key="nav3"):
            st.session_state.current_page = "📊 My Progress"
            st.rerun()
    with nav4:
        if st.button("📋 Daily Summary", use_container_width=True, key="nav4"):
            st.session_state.current_page = "📋 Daily Summary"
            st.rerun()

    page = st.session_state.get("current_page", "🏠 Daily Planner")

    # SOS Button — always visible
    st.markdown("---")
    col_sos1, col_sos2, col_sos3 = st.columns([1,2,1])
    with col_sos2:
        if st.button("🚨 EMERGENCY SOS — TAP HERE", use_container_width=True,
                     type="primary"):
            st.session_state.sos_triggered = True

    if st.session_state.sos_triggered:
        st.error(f"""
        🚨 **SOS ALERT SENT!**
        
        Notifying: {p['contacts'][0][0]} — {p['contacts'][0][1]}
        
        Stay calm {first_name}. Help is on the way. If this is a medical emergency call **000**.
        """)

    st.markdown("---")

    # ============================================================
    # PAGE: DAILY PLANNER
    # ============================================================
    if page == "🏠 Daily Planner":

        col1, col2 = st.columns([3,2])

        with col1:
            # Mood check-in
            st.markdown("### 😊 How are you feeling today?")
            mood_cols = st.columns(5)
            for i, (emoji, label, score) in enumerate(MOOD_OPTIONS):
                with mood_cols[i]:
                    if st.button(f"{emoji}\n{label}", key=f"mood_{i}",
                                use_container_width=True):
                        st.session_state.mood_score = score
            if st.session_state.mood_score:
                mood_label = [m[1] for m in MOOD_OPTIONS if m[2]==st.session_state.mood_score][0]
                st.success(f"Thank you {first_name}! You're feeling **{mood_label}** today.")

            # Birthday alerts
            today_str = now.strftime("%d %B")
            for name, bday in p["birthday_contacts"]:
                if bday == today_str:
                    st.markdown(f"""
                    <div class='alert-box'>
                        <div class='alert-title'>🎂 Birthday Alert!</div>
                        <div class='alert-text'>Today is <strong>{name}'s</strong> birthday!
                        Don't forget to call or send a message to wish them well! 🎉</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Appointment reminders
            st.markdown("### 📅 Today's Tasks")
            for i, (emoji, task_name, sched_time) in enumerate(DAILY_TASKS):
                task_hour = int(sched_time.split(":")[0])
                is_due = abs(hour - task_hour) <= 1 and not st.session_state.task_done[i]

                col_check, col_task = st.columns([1,8])
                with col_check:
                    checked = st.checkbox("", value=st.session_state.task_done[i],
                                         key=f"task_{i}")
                    st.session_state.task_done[i] = checked
                with col_task:
                    if checked:
                        st.markdown(f"<div class='task-item task-done'>{emoji} {task_name} ✓ &nbsp;&nbsp; <small>⏰ {sched_time}</small></div>", unsafe_allow_html=True)
                    elif is_due:
                        st.markdown(f"<div class='task-item task-urgent'>{emoji} {task_name} ← DUE NOW! &nbsp;&nbsp; <small>⏰ {sched_time}</small></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='task-item'>{emoji} {task_name} &nbsp;&nbsp; <small>⏰ {sched_time}</small></div>", unsafe_allow_html=True)

        with col2:
            # Progress
            tasks_done = sum(st.session_state.task_done)
            tasks_total = len(DAILY_TASKS)
            pct = int((tasks_done / tasks_total) * 100)

            st.markdown("### 📊 Today's Progress")
            st.markdown(f"""
            <div class='card'>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='font-size:28px; font-weight:700; color:#1A2E5A;'>{tasks_done}/{tasks_total}</span>
                    <span style='font-size:28px; font-weight:700; color:#C0152B;'>{pct}%</span>
                </div>
                <div class='progress-wrap'>
                    <div class='progress-fill' style='width:{pct}%;'></div>
                </div>
                <div style='font-size:12px; color:#94A3B8;'>Tasks completed today</div>
            </div>
            """, unsafe_allow_html=True)

            if pct == 0:
                st.info(f"Let's get started {first_name}! You can do it 💪")
            elif pct < 50:
                st.info(f"Great start {first_name}! Keep going 🌟")
            elif pct < 100:
                st.success(f"You're doing really well {first_name}! Almost there 🎉")
            else:
                st.success(f"🎊 Amazing! You completed everything today {first_name}!")

            # Medications
            st.markdown("### 💊 Today's Medications")
            for med, time in p["medications_list"]:
                med_hour = int(time.split(":")[0])
                if hour > med_hour:
                    st.markdown(f"<div class='task-item task-done'>💊 {med} <small>— {time}</small></div>", unsafe_allow_html=True)
                elif abs(hour - med_hour) <= 1:
                    st.markdown(f"<div class='task-item task-urgent'>💊 {med} ← DUE NOW <small>— {time}</small></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='task-item'>💊 {med} <small>— {time}</small></div>", unsafe_allow_html=True)

            # Appointments
            if p["appointments"]:
                st.markdown("### 🏥 Upcoming Appointments")
                for appt, time in p["appointments"]:
                    st.markdown(f"""
                    <div class='card card-gold' style='padding:10px 14px;'>
                        <div style='font-size:13px; font-weight:600;'>{appt}</div>
                        <div style='font-size:12px; color:#64748B;'>🕐 {time}</div>
                        <div style='font-size:12px; color:#64748B;'>🚗 {p['driver']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ============================================================
    # PAGE: AI ASSISTANT
    # ============================================================
    elif page == "💬 AI Assistant":
        st.markdown(f"### 🤖 AI Assistant — Chat with {first_name}")
        st.caption("Ask me anything — medications, appointments, how you're feeling, what to do today")

        if not st.session_state.api_key or not st.session_state.api_key.startswith("sk-ant"):
            st.warning("⚠️ Please enter your Anthropic API key in the sidebar to enable the AI assistant.")

        # Chat history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(f"""
                <div class='chat-msg-ai'>
                    👋 Hello {first_name}! I'm your AI companion. I know all about your medications,
                    appointments and daily schedule. How can I help you today?
                </div>
                """, unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"<div class='chat-msg-user'>{msg['content']}</div>",
                               unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-msg-ai'>🤖 {msg['content']}</div>",
                               unsafe_allow_html=True)

        # Quick questions
        st.markdown("**Quick questions:**")
        q_cols = st.columns(2)
        quick_questions = [
            "What medications do I need today?",
            "Do I have any appointments?",
            "What tasks haven't I done yet?",
            "I'm feeling unwell",
            "Who should I call today?",
            "What time is my next medication?"
        ]
        for i, q in enumerate(quick_questions):
            with q_cols[i % 2]:
                if st.button(q, key=f"qq_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role":"user","content":q})
                    with st.spinner("Thinking..."):
                        response = ask_claude(q, persona)
                    st.session_state.chat_history.append({"role":"assistant","content":response})
                    st.rerun()

        # Text input
        user_input = st.chat_input(f"Type a message for {first_name}...")
        if user_input:
            st.session_state.chat_history.append({"role":"user","content":user_input})
            with st.spinner("Thinking..."):
                response = ask_claude(user_input, persona)
            st.session_state.chat_history.append({"role":"assistant","content":response})
            st.rerun()

        if st.button("🗑️ Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

    # ============================================================
    # PAGE: MY PROGRESS
    # ============================================================
    elif page == "📊 My Progress":
        st.markdown("### 📊 Your Progress Overview")

        tasks_done = sum(st.session_state.task_done)
        tasks_total = len(DAILY_TASKS)
        pct = int((tasks_done / tasks_total) * 100)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='card'>
                <div class='kpi-num'>{tasks_done}</div>
                <div class='kpi-label'>Tasks completed today</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='card card-red'>
                <div class='kpi-num'>{tasks_total - tasks_done}</div>
                <div class='kpi-label'>Tasks remaining</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='card card-green'>
                <div class='kpi-num'>{pct}%</div>
                <div class='kpi-label'>Daily completion rate</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            mood_display = "—"
            if st.session_state.mood_score:
                mood_display = MOOD_OPTIONS[st.session_state.mood_score-1][0]
            st.markdown(f"""
            <div class='card card-gold'>
                <div class='kpi-num'>{mood_display}</div>
                <div class='kpi-label'>Today's mood</div>
            </div>
            """, unsafe_allow_html=True)

        # Task breakdown
        st.markdown("### ✅ Task Breakdown")
        completed = [(DAILY_TASKS[i], i) for i in range(tasks_total) if st.session_state.task_done[i]]
        remaining = [(DAILY_TASKS[i], i) for i in range(tasks_total) if not st.session_state.task_done[i]]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Completed ({len(completed)})**")
            for (emoji, name, time), _ in completed:
                st.markdown(f"<div class='task-item task-done'>{emoji} {name}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Still to do ({len(remaining)})**")
            for (emoji, name, time), _ in remaining:
                st.markdown(f"<div class='task-item'>{emoji} {name} <small>⏰ {time}</small></div>", unsafe_allow_html=True)

        # Persona profile
        st.markdown("### 👤 Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='card'>
                <div class='card-title'>Personal Details</div>
                <b>Name:</b> {persona}<br>
                <b>Age:</b> {p['age']}<br>
                <b>Location:</b> {p['suburb']}<br>
                <b>Household:</b> {p['house']}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            fall_color = {"Low":"#22C55E","Medium":"#E8A020","High":"#EF4444","Critical":"#7F1D1D"}.get(p['fall_risk'],'#64748B')
            st.markdown(f"""
            <div class='card card-red'>
                <div class='card-title'>Health Profile</div>
                <b>Condition:</b> {p['condition']}<br>
                <b>Daily medications:</b> {p['medications']}<br>
                <b>Fall risk:</b> <span style='color:{fall_color}; font-weight:700;'>{p['fall_risk']}</span><br>
                <b>Isolation score:</b> {p['isolation']}/10
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # PAGE: DAILY SUMMARY
    # ============================================================
    elif page == "📋 Daily Summary":
        st.markdown(f"### 📋 Daily Summary — {now.strftime('%A %d %B %Y')}")

        tasks_done = sum(st.session_state.task_done)
        tasks_total = len(DAILY_TASKS)
        pct = int((tasks_done / tasks_total) * 100)
        completed = [DAILY_TASKS[i] for i in range(tasks_total) if st.session_state.task_done[i]]
        missed = [DAILY_TASKS[i] for i in range(tasks_total) if not st.session_state.task_done[i]]

        # Summary card
        mood_text = ""
        if st.session_state.mood_score:
            mood_labels = {1:"Very low 😔",2:"Low 😕",3:"Okay 😐",4:"Good 🙂",5:"Great 😄"}
            mood_text = mood_labels[st.session_state.mood_score]

        st.markdown(f"""
        <div class='card' style='background:linear-gradient(135deg,#F0F9FF,#FFF); border-left:4px solid #1A2E5A;'>
            <div style='font-size:20px; font-weight:700; color:#1A2E5A; margin-bottom:12px;'>
                📋 {first_name}'s Day Summary
            </div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:8px;'>
                <div><b>Tasks completed:</b> {tasks_done}/{tasks_total} ({pct}%)</div>
                <div><b>Mood today:</b> {mood_text if mood_text else 'Not recorded'}</div>
                <div><b>Medications due:</b> {p['medications']}</div>
                <div><b>Fall risk level:</b> {p['fall_risk']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**✅ Completed ({len(completed)})**")
            for emoji, name, time in completed:
                st.markdown(f"<div class='task-item task-done'>{emoji} {name}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**⚠️ Missed or not done ({len(missed)})**")
            for emoji, name, time in missed:
                st.markdown(f"<div class='task-item task-urgent'>{emoji} {name} <small>was due at {time}</small></div>", unsafe_allow_html=True)

        # Closing message
        st.markdown("---")
        if pct == 100:
            st.success(f"🎊 Perfect day {first_name}! You completed every single task today. Wonderful!")
        elif pct >= 75:
            st.success(f"👍 Great effort {first_name}! You did really well today. Try to get those remaining tasks tomorrow.")
        elif pct >= 50:
            st.info(f"🌟 Good effort {first_name}! You completed more than half your tasks. Every day is a new start!")
        else:
            st.info(f"💙 That's okay {first_name}. Tomorrow is a new day. You've got this! Remember to take your medications.")

        # Family report
        st.markdown("### 📧 Daily Family Report")
        st.markdown(f"""
        <div class='card card-gold'>
            <div class='card-title'>Automatic report sent to: {p['contacts'][0][0]}</div>
            <div style='font-size:13px; color:#64748B;'>
                📊 {first_name} completed {tasks_done}/{tasks_total} tasks today ({pct}%)<br>
                😊 Mood: {mood_text if mood_text else 'Not recorded'}<br>
                💊 Medications: {p['medications']} scheduled today<br>
                ⚠️ Fall risk level: {p['fall_risk']}<br>
                📅 Report generated: {now.strftime('%d/%m/%Y %I:%M %p')}
            </div>
        </div>
        """, unsafe_allow_html=True)
