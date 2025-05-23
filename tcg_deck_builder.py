import streamlit as st
import json

@st.cache_data
def load_decks():
    with open("cached_mtgo_decks.json", "r", encoding="utf-8") as f:
        return json.load(f)

decks = load_decks()

st.title("TCG Deck Builder")

uploaded_file = st.file_uploader("Upload your card list (one card per line)", type=["txt", "csv"])

if uploaded_file is not None:
    owned_cards_raw = uploaded_file.getvalue().decode("utf-8").splitlines()
    owned_cards = [line.strip() for line in owned_cards_raw if line.strip()]

    # Count owned cards occurrences
    owned_counts = {}
    for card in owned_cards:
        owned_counts[card] = owned_counts.get(card, 0) + 1

    st.write(f"**You own {len(owned_cards)} cards total ({len(owned_counts)} unique).**")
    st.write("### Deck Suggestions:")

    for deck in decks:
        deck_cards = deck.get("cards", {})

        if isinstance(deck_cards, list):
            deck_cards = {card: 1 for card in deck_cards}
        elif not isinstance(deck_cards, dict):
            continue  # skip invalid decks

        matching_cards_count = sum(
            1 for card, req_count in deck_cards.items()
            if owned_counts.get(card, 0) > 0
        )
        if matching_cards_count < 5:
            continue

        st.subheader(deck["name"])
        st.write(f"Author: {deck.get('author','Unknown')}")
        st.write(f"Format: {deck.get('format','Unknown')}")
        st.write(f"Deck Type: {deck.get('deck_type','Unknown')}")

        owned_list = []
        missing_list = []

        for card, req_count in deck_cards.items():
            owned_qty = owned_counts.get(card, 0)
            if owned_qty >= req_count:
                owned_list.append(f"🟢 {card} x{req_count}")
            elif owned_qty > 0:
                missing_qty = req_count - owned_qty
                owned_list.append(f"🟢 {card} x{owned_qty} (partial)")
                missing_list.append(f"🔴 {card} x{missing_qty}")
            else:
                missing_list.append(f"🔴 {card} x{req_count}")

        if owned_list:
            st.markdown("**Cards you have:**")
            st.write(", ".join(owned_list))
        if missing_list:
            st.markdown("**Cards missing:**")
            st.write(", ".join(missing_list))


else:
    st.info("Upload your card list file to see deck suggestions.")
