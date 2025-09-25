import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Boros Dashboard", layout="wide")
st.title("🔴 Boros Energy Winrate Dashboard")

# Load data
df = pd.read_csv("boros_energy_winrate_predictions.csv")

# Show overall winrate chart
st.subheader("⚡ Predicted Winrate Over Time")
if "Predicted Winrate" in df.columns:
    st.line_chart(df["Predicted Winrate"])
else:
    st.warning("Predicted Winrate column not found.")

# Detect matchup columns
matchup_cols = [col for col in df.columns if col.startswith("Winrate_vs_")]

# Matchup dropdown
if matchup_cols:
    selected = st.selectbox("🧩 Choose Opponent Archetype", matchup_cols)
    st.subheader(f"📊 Winrate vs {selected.replace('Winrate_vs_', '').replace('_', ' ')}")
    st.line_chart(df[selected])
else:
    st.warning("No matchup data found in the CSV.")

# View all matchup winrates
if matchup_cols:
    st.subheader("📋 All Matchup Winrates")
    avg_winrates = df[matchup_cols].mean().sort_values(ascending=False)
    st.bar_chart(avg_winrates)

    # Top and bottom matchups
    st.subheader("🔥 Top 5 Matchups")
    st.bar_chart(avg_winrates.head(5))

    st.subheader("💀 Bottom 5 Matchups")
    st.bar_chart(avg_winrates.tail(5))

    # Optional: show as table
    with st.expander("📄 View All Matchups as Table"):
        st.dataframe(avg_winrates)

# Raw data viewer
with st.expander("📄 Full Dataset"):
    st.dataframe(df)
