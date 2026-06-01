import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Sports Analytics Dashboard", page_icon="⚽", layout="wide")

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
    }
    .card {
        background-color: #1E2127;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Sports Team Selection & Analytics")
st.markdown("---")

tab1, tab2 = st.tabs(["👥 Player Roster", "➕ Add New Player"])

with tab1:
    st.header("Current Players")
    try:
        response = requests.get(f"{API_URL}/players/")
        if response.status_code == 200:
            players = response.json()
            if players:
                df = pd.DataFrame(players)
                st.dataframe(
                    df[["id", "name", "age", "sport", "position", "team"]], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No players found. Add some players!")
        else:
            st.error(f"Failed to load players: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend API. Please make sure the FastAPI server is running on http://localhost:8000")

with tab2:
    st.header("Register New Player")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=15, max_value=50, value=25)
            sport = st.selectbox("Sport", ["Football/Soccer", "Basketball", "Cricket", "Tennis", "Rugby"])
        with col2:
            position = st.text_input("Position (e.g., Forward, Point Guard)")
            team = st.text_input("Current Team")
            
        if st.button("Register Player", use_container_width=True):
            if name and position and team:
                payload = {
                    "name": name,
                    "age": age,
                    "sport": sport,
                    "position": position,
                    "team": team
                }
                try:
                    res = requests.post(f"{API_URL}/players/", json=payload)
                    if res.status_code == 200:
                        st.success(f"Player {name} added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend API.")
            else:
                st.warning("Please fill out all fields.")
        st.markdown('</div>', unsafe_allow_html=True)
