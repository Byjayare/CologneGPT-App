
import streamlit as st
import json
from collections import defaultdict
import matplotlib.pyplot as plt

# Load scent database
def load_scent_db():
    try:
        with open("scent_database.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Load hybrid combo ratings
def load_combo_ratings():
    try:
        with open("combo_ratings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Analyze dominant notes
def analyze_profile(user_scents, scent_db):
    note_counter = defaultdict(int)
    for scent in user_scents:
        scent_data = scent_db.get(scent)
        if scent_data:
            for note in scent_data["profile"]:
                note_counter[note] += 1
    return dict(sorted(note_counter.items(), key=lambda x: x[1], reverse=True))

# Display profile chart
def plot_note_profile(profile):
    if profile:
        notes, counts = zip(*profile.items())
        fig, ax = plt.subplots()
        ax.bar(notes, counts, color="#ff6f00")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.info("No scent data available for your profile.")

# Suggest hybrid layering combos
def suggest_hybrids(user_scents, scent_db):
    suggestions = []
    for base in user_scents:
        for top in user_scents:
            if base != top:
                base_notes = set(scent_db.get(base, {}).get("profile", []))
                top_notes = set(scent_db.get(top, {}).get("profile", []))
                shared = base_notes.intersection(top_notes)
                if shared:
                    suggestions.append((base, top, list(shared)))
    return suggestions

# App starts here
st.set_page_config(page_title="CologneGPT", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-image: url('assets/beach_cologne_bg.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .main, .block-container {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 10px;
            padding: 1rem;
        }
        h1, h2 {
            color: #ff6f00;
        }
        .stButton>button {
            background-color: #ff6f00;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2 {
            color: #ff6f00;
        }
        .stButton>button {
            background-color: #ff6f00;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 CologneGPT - Personalized Scent Recommender")

# Load data
scent_db = load_scent_db()
combo_ratings = load_combo_ratings()
all_scents = list(scent_db.keys())

# Main UI with tabs
tabs = st.tabs(["👃 My Scents", "📊 Profile Analysis", "✨ Recommendations", "🧪 Hybrid Combos", "📬 Custom Request"])

with tabs[0]:
    st.header("Add Your Collection")
    selected_scents = st.multiselect("Select the fragrances you own:", options=all_scents)
    st.session_state["user_scents"] = selected_scents

with tabs[1]:
    st.header("Your Scent Note Profile")
    if st.session_state.get("user_scents"):
        profile = analyze_profile(st.session_state["user_scents"], scent_db)
        plot_note_profile(profile)
        st.write(profile)
    else:
        st.warning("Please add some scents first.")

with tabs[2]:
    st.header("Recommended Scents Based on Your Profile")
    if st.session_state.get("user_scents"):
        user_profile = analyze_profile(st.session_state["user_scents"], scent_db)
        top_notes = list(user_profile.keys())[:3]
        st.markdown(f"Top Notes: **{', '.join(top_notes)}**")
        matches = {
            name: data for name, data in scent_db.items()
            if name not in st.session_state["user_scents"]
            and any(note in data["profile"] for note in top_notes)
        }
        for name, data in matches.items():
            st.markdown(f"**{name}** - {data['type']} | Notes: {', '.join(data['profile'])}")
    else:
        st.info("Add your scents to see recommendations.")

with tabs[3]:
    st.header("Smart Layering Suggestions")
    if st.session_state.get("user_scents"):
        hybrids = suggest_hybrids(st.session_state["user_scents"], scent_db)
        if hybrids:
            for base, top, shared in hybrids:
                st.write(f"- {base} + {top} → Shared notes: {', '.join(shared)}")
        else:
            st.info("No hybrid suggestions found with overlapping notes.")
    else:
        st.info("Add your scents to explore layering options.")

with tabs[4]:
    st.header("Request a Custom Decant or Hybrid")
    if st.session_state.get("user_scents"):
        with st.form("request_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            notes = st.text_area("Message or Preferences")
            submit = st.form_submit_button("Send Request")
            if submit:
                with open("custom_requests_log.txt", "a") as f:
                    f.write(f"Name: {name}\nEmail: {email}\nScents: {st.session_state['user_scents']}\nNotes: {notes}\n\n")
                st.success("Request submitted successfully!")
    else:
        st.info("Add your scents first to build a request.")
