import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# Page setup
st.set_page_config(page_title="Boros Dashboard", layout="wide")
st.title("🔴 Boros Energy Winrate Dashboard")

# Load data
df = pd.read_csv("boros_energy_winrate_predictions.csv")
matchup_cols = [col for col in df.columns if col.startswith("Winrate_vs_")]

# Inject default deck version
df["deck_version"] = "Default"
deck_versions = ["Default"]

# Archetype categories
interaction_heavy = ["Control", "Midrange", "Tempo"]
low_interaction = ["Aggro", "Combo", "Ramp"]

# Trait-based card suggestions
trait_suggestions = {
    "Resilience": ["Veil of Summer", "Loran of the Third Path", "Reckoner Bankbuster"],
    "Explosiveness": ["Reinforced Ronin", "Experimental Synthesizer", "Monastery Swiftspear"],
    "Versatility": ["Fable of the Mirror-Breaker", "Wedding Announcement", "Restless Bivouac"],
    "Adaptability": ["Chandra, Hope's Beacon", "The Wandering Emperor", "Sunfall"],
    "Late Game": ["Portal to Phyrexia", "Sanctuary Warden", "Farewell"]
}

# Helper: fetch card image from Scryfall
def get_card_image(card_name):
    try:
        response = requests.get(f"https://api.scryfall.com/cards/named?exact={card_name}")
        if response.status_code == 200:
            return response.json()["image_uris"]["normal"]
    except:
        return None

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
    st.subheader("🧠 Trait Diagnostics")

    trait_data = []
    suggestions = {}

    for version in deck_versions:
        subset = df[df['deck_version'] == version]

        resilience_cols = [col for col in matchup_cols if any(tag.lower() in col.lower() for tag in interaction_heavy)]
        resilience = subset[resilience_cols].mean().mean() if resilience_cols else 0

        explosive_cols = [col for col in matchup_cols if any(tag.lower() in col.lower() for tag in low_interaction)]
        explosiveness = subset[explosive_cols].mean().mean() if explosive_cols else 0

        versatility = subset[matchup_cols].mean().std()
        adaptability = subset["Predicted Winrate"].std() if "Predicted Winrate" in subset.columns else 0

        control_cols = [col for col in matchup_cols if "control" in col.lower()]
        late_game = subset[control_cols].mean().mean() if control_cols else 0

        trait_data.append({
            "Deck Version": version,
            "Resilience": resilience,
            "Explosiveness": explosiveness,
            "Versatility": versatility,
            "Adaptability": adaptability,
            "Late Game": late_game
        })

        # Detect weak traits
        weak = []
        if resilience < 0.15: weak.append("Resilience")
        if explosiveness < 0.15: weak.append("Explosiveness")
        if versatility < 0.15: weak.append("Versatility")
        if adaptability < 0.15: weak.append("Adaptability")
        if late_game < 0.15: weak.append("Late Game")
        suggestions[version] = weak

    trait_df = pd.DataFrame(trait_data)

    # Radar chart comparison
    st.subheader("📊 Radar Chart")
    selected_versions = st.multiselect("Select Deck Versions", deck_versions, default=deck_versions)

    if selected_versions:
        radar_df = trait_df[trait_df["Deck Version"].isin(selected_versions)]
        radar_df = radar_df.set_index("Deck Version").T

        fig = go.Figure()

        for version in selected_versions:
            fig.add_trace(go.Scatterpolar(
                r=radar_df[version],
                theta=radar_df.index,
                fill='toself',
                name=version
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # Sideboard suggestions
    st.subheader("🧙 Sideboard Suggestions")
    selected_version = st.selectbox("Select Deck Version", deck_versions)
    weak_traits = suggestions[selected_version]

    if weak_traits:
        for trait in weak_traits:
            st.markdown(f"**{trait}** is below threshold. Consider:")
            for card in trait_suggestions[trait]:
                url = f"https://scryfall.com/search?q={card.replace(' ', '+')}"
                image_url = get_card_image(card)
                if image_url:
                    st.image(image_url, caption=f"[{card}]({url})", use_column_width=True)
                else:
                    st.markdown(f"- [{card}]({url})")
    else:
        st.success("No major weaknesses detected for this version.")

with tab4:
    st.subheader("📄 Full Dataset")
    st.dataframe(df)