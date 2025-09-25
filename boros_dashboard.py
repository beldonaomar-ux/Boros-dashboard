import streamlit as st
import pandas as pd

st.set_page_config(page_title="Boros Dashboard", layout="wide")
st.title("🔴 Boros Energy Winrate Dashboard")

# Load your CSV
df = pd.read_csv("boros_energy_winrate_predictions.csv")

# Show overall winrate chart
st.subheader("⚡ Predicted Winrate Over Time")
if "Predicted Winrate" in df.columns:
    st.line_chart(df["Predicted Winrate"])
else:
    st.warning("Predicted Winrate column not found.")

# Detect matchup columns
matchup_cols = [col for col in df.columns if col.startswith("Winrate_vs_")]

# Show matchup filter
if matchup_cols:
    selected = st.selectbox("🧩 Choose Opponent Archetype", matchup_cols)
    st.subheader(f"📊 Winrate vs {selected.replace('Winrate_vs_', '').replace('_', ' ')}")
    st.line_chart(df[selected])
else:
    st.warning("No matchup data found in the CSV.")

# Optional: show raw data
with st.expander("📄 Show Raw Data"):
    st.dataframe(df)
