import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Boros Dashboard", layout="wide")
st.title("🔴 Boros Energy Winrate Dashboard")

# Load data
df = pd.read_csv("boros_energy_winrate_predictions.csv")
matchup_cols = [col for col in df.columns if col.startswith("Winrate_vs_")]

# Define archetype categories
interaction_heavy = ["Control", "Midrange", "Tempo"]
low_interaction = ["Aggro", "Combo", "Ramp"]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Winrate Trends", "🧩 Matchup Analysis", "🧠 Trait Diagnostics", "📄 Raw Data"])

with tab1:
    st.subheader("⚡ Predicted Winrate Over Time")
    if "Predicted Winrate" in df.columns:
        st.line_chart(df["Predicted Winrate"])
    else:
        st.warning("Predicted Winrate column not found.")

with tab2:
    if matchup_cols:
        selected = st.selectbox("Choose Opponent Archetype", matchup_cols)
        st.subheader(f"Winrate vs {selected.replace('Winrate_vs_', '').replace('_', ' ')}")
        st.line_chart(df[selected])

        st.subheader("📋 All Matchup Winrates")
        avg_winrates = df[matchup_cols].mean().sort_values(ascending=False)
        st.bar_chart(avg_winrates)

        st.subheader("🔥 Top 5 Matchups")
        st.bar_chart(avg_winrates.head(5))

        st.subheader("💀 Bottom 5 Matchups")
        st.bar_chart(avg_winrates.tail(5))

        with st.expander("📄 View All Matchups as Table"):
            st.dataframe(avg_winrates)
    else:
        st.warning("No matchup data found in the CSV.")

with tab3:
    st.subheader("🧠 Deck Trait Diagnostics")

    resilience_cols = [col for col in matchup_cols if any(tag.lower() in col.lower() for tag in interaction_heavy)]
    resilience_score = df[resilience_cols].mean().mean() if resilience_cols else 0

    explosive_cols = [col for col in matchup_cols if any(tag.lower() in col.lower() for tag in low_interaction)]
    explosiveness_score = df[explosive_cols].mean().mean() if explosive_cols else 0

    versatility_score = df[matchup_cols].mean().std()
    adaptability_score = df["Predicted Winrate"].std() if "Predicted Winrate" in df.columns else 0

    control_cols = [col for col in matchup_cols if "control" in col.lower()]
    late_game_score = df[control_cols].mean().mean() if control_cols else 0

    trait_scores = {
        "Resilience": resilience_score,
        "Explosiveness": explosiveness_score,
        "Versatility": versatility_score,
        "Adaptability": adaptability_score,
        "Late Game": late_game_score
    }
    trait_df = pd.DataFrame(trait_scores, index=["Score"]).T
    st.bar_chart(trait_df)

with tab4:
    st.subheader("📄 Full Dataset")
    st.dataframe(df)