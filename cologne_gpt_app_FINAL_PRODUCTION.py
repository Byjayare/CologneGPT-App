
# Streamlit-based CologneGPT Web App with Styling and Background

import streamlit as st
import json
from collections import defaultdict

# Inject custom CSS
st.markdown("""
    <style>
        body {
            background-image: url('https://raw.githubusercontent.com/Byjayare/Cologne-GPT/main/assets/beach_cologne_bg.jpg');
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07);
        }
        h1, h2, h3, h4, h5 {
            color: #ff6f00;
        }
        .stButton>button {
            border-radius: 8px;
            background-color: #ff6f00;
            color: white;
            padding: 0.5em 1em;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Branded header
st.markdown("""
    <div style='text-align:center; padding-bottom: 1rem;'>
        <h1 style='font-size: 3rem; font-weight: 600; color: #ff6f00;'>Byjayare</h1>
        <p style='font-size: 1.1rem; color: #333;'>Where Scent Meets Style</p>
    </div>
""", unsafe_allow_html=True)

class CologneGPT:
    def __init__(self, user_scents):
        self.user_scents = user_scents
        self.scent_db = self.build_scent_db()
        self.ratings_file = "combo_ratings.json"
        self.combo_ratings = self.load_combo_ratings()

    def build_scent_db(self):
        try:
            with open("scent_database.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_combo_ratings(self):
        try:
            with open(self.ratings_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def analyze_profile(self):
        note_counter = defaultdict(int)
        for scent in self.user_scents:
            scent_data = self.scent_db.get(scent)
            if scent_data:
                for note in scent_data["profile"]:
                    note_counter[note] += 1
        return dict(sorted(note_counter.items(), key=lambda x: x[1], reverse=True))

# Streamlit Logic
st.title("🧠 CologneGPT: Personalized Fragrance Recommender")

user_input = st.sidebar.text_area("Enter your fragrances (one per line):")
user_scents = [s.strip() for s in user_input.strip().splitlines() if s.strip()]

st.sidebar.subheader("Filter & Search")
selected_type = st.sidebar.selectbox("Filter by Scent Type", ["All"] + sorted(set(s["type"] for s in CologneGPT([]).build_scent_db().values())))
search_query = st.sidebar.text_input("Search Fragrance Name")

cgpt = CologneGPT(user_scents)

if selected_type != "All" or search_query:
    filtered = {
        name: data for name, data in cgpt.scent_db.items()
        if (selected_type == "All" or data["type"] == selected_type)
        and (search_query.lower() in name.lower())
    }
    st.subheader("🔎 Matching Scents")
    for name, data in filtered.items():
        st.markdown(f"**{name}**\n- Profile: {', '.join(data['profile'])}\n- Category: {data['category']}\n- Occasion: {', '.join(data['occasion'])}\n- Type: {data['type']}")

if user_scents:
    profile = cgpt.analyze_profile()
    st.subheader("📊 Your Scent Profile")
    st.write(profile)

    st.subheader("🧪 Smart Layering Suggestions")
    hybrid_suggestions = []
    for base in user_scents:
        for top in user_scents:
            if base != top:
                base_notes = set(cgpt.scent_db.get(base, {}).get("profile", []))
                top_notes = set(cgpt.scent_db.get(top, {}).get("profile", []))
                if base_notes and top_notes:
                    shared = base_notes.intersection(top_notes)
                    if shared:
                        hybrid_suggestions.append((base, top, list(shared)))
    for base, top, shared in hybrid_suggestions:
        combo_key = f"{base} + {top}"
        if "saved_hybrids" not in st.session_state:
            st.session_state.saved_hybrids = []
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"- {base} + {top} (Shared notes: {', '.join(shared)})")
        with col2:
            if st.button(f"💾 Save", key=f"save_{combo_key}"):
                if combo_key not in st.session_state.saved_hybrids:
                    st.session_state.saved_hybrids.append(combo_key)
                    st.success(f"Saved hybrid: {combo_key}")

    if st.session_state.get("saved_hybrids"):
        st.subheader("📦 Saved Hybrids for Custom Requests")
        for combo in st.session_state.saved_hybrids:
            st.markdown(f"- {combo}")
        with st.form("custom_request_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            notes = st.text_area("Additional Notes")
            submitted = st.form_submit_button("Submit Request")
            if submitted:
                with open("custom_requests_log.txt", "a") as log:
                    log.write(f"Name: {name}\nEmail: {email}\nHybrids: {st.session_state.saved_hybrids}\nNotes: {notes}\n\n")
                st.success("Your request has been logged. We'll reach out to you at byjayare@gmail.com.")
