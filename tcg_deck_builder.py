import streamlit as st
import json
import pandas as pd

# Load cached decks from JSON file (adjust path if needed)
@st.cache_data
def load_decks():
    with open("cached_mtgo_decks.json", "r", encoding="utf-8") as f:
        return json.load(f)

decks = load_decks()

# Extract TCG options from decks (assuming decks have a 'tcg' key, fallback if not)
# For this example, let's assume all decks are Magic: The Gathering
tcg_options = ["Magic: The Gathering", "Yu-Gi-Oh!"]
selected_tcg = st.selectbox("Select TCG", tcg_options)

st.title("TCG Deck Builder")

uploaded_file = st.file_uploader("Upload your card list CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Load card list CSV into a dataframe
        df = pd.read_csv(uploaded_file)
        # Expecting the CSV to have a column named 'card' or similar
        # We'll try to find the first column and treat it as card names:
        user_cards = df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().tolist()
        st.write(f"Loaded {len(user_cards)} cards from your list.")
        
        # Filter decks by TCG (if your decks have a 'tcg' field; if not, skip this)
        # For this example, assume all decks are Magic: The Gathering
        filtered_decks = [deck for deck in decks if selected_tcg == "Magic: The Gathering"]

        # Score decks by how many cards match user's cards (case insensitive)
        def deck_match_score(deck):
            deck_cards = [c.lower() for c in deck["cards"]]
            return len(set(deck_cards) & set(user_cards))

        scored_decks = [(deck, deck_match_score(deck)) for deck in filtered_decks]
        # Keep decks with at least one matching card, sorted by score descending
        matching_decks = [d for d in scored_decks if d[1] > 0]
        matching_decks.sort(key=lambda x: x[1], reverse=True)

        if not matching_decks:
            st.info("No matching decks found with your cards.")
        else:
            st.success(f"Found {len(matching_decks)} decks matching your cards:")
            for deck, score in matching_decks[:20]:  # limit to top 20 matches
                st.markdown(f"### {deck['name']} — *{deck.get('deck_type', 'Unknown Type')}*")
                st.markdown(f"**Author:** {deck.get('author', 'Unknown')}")
                st.markdown(f"**Format:** {deck.get('format', 'Unknown')}")
                st.markdown(f"**Matching cards:** {score}")
                # Color-code cards: green if owned, red if missing
                colored_cards = []
                for card in deck["cards"]:
                    if card.lower() in user_cards:
                        colored_cards.append(f'<span style="color: green">{card}</span>')
                    else:
                        colored_cards.append(f'<span style="color: red">{card}</span>')
                st.markdown(", ".join(colored_cards), unsafe_allow_html=True)
                st.markdown("---")
    except Exception as e:
        st.error(f"Failed to process your file: {e}")

else:
    st.info("Please upload a CSV file containing your card list.")
