import streamlit as st
import json

# Load decks from JSON once
@st.cache_data
def load_decks():
    with open("moxfield_decks.json", "r", encoding="utf-8") as f:
        return json.load(f)

decks = load_decks()

st.title("TCG Deck Builder")

# Input owned cards file (CSV expected: one card per line)
uploaded_file = st.file_uploader("Upload your card list (one card per line)", type=["txt", "csv"])

if uploaded_file is not None:
    # Read cards you own
    owned_cards = set(line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip())
    st.write(f"**You own {len(owned_cards)} cards.**")

    st.write("### Deck Suggestions:")

    for deck in decks:
        deck_cards = deck.get("cards", [])
        owned_in_deck = [card for card in deck_cards if card in owned_cards]
        missing_in_deck = [card for card in deck_cards if card not in owned_cards]

        if len(owned_in_deck) < 5:
            # Skip decks with very few matching cards (optional)
            continue

        st.subheader(deck["name"])
        st.write(f"Author: {deck['author']}")
        st.write(f"Format: {deck['format']}")
        st.write(f"Deck Type: {deck.get('deck_type', 'Unknown')}")

        st.markdown("**Cards you own in this deck:**")
        st.write(", ".join(f"🟢 {card}" for card in sorted(set(owned_in_deck))))

        st.markdown("**Cards missing from this deck:**")
        st.write(", ".join(f"🔴 {card}" for card in sorted(set(missing_in_deck))))

else:
    st.info("Upload your card list file to see deck suggestions.")
