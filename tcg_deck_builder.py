import streamlit as st
import json

@st.cache_data
def load_cached_decks():
    with open("cached_mtgo_decks.json", "r", encoding="utf-8") as f:
        decks = json.load(f)
    return decks

def suggest_decks(user_cards, deck_type, decks):
    user_cards_set = set(card.lower() for card in user_cards)
    filtered_decks = []

    for deck in decks:
        if deck_type != "All" and deck["deck_type"].lower() != deck_type.lower():
            continue
        deck_cards_set = set(card.lower() for card in deck["cards"])
        if user_cards_set & deck_cards_set:  # intersection not empty
            filtered_decks.append(deck)

    return filtered_decks

def main():
    st.title("MTG Deck Suggestion App with Cached Decks")

    deck_types = ["All", "Aggro", "Control", "Midrange", "Combo"]
    selected_deck_type = st.selectbox("Select deck type", deck_types)

    uploaded_file = st.file_uploader("Upload your card list (CSV or TXT, one card per line)")
    user_cards = []
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        user_cards = [line.strip() for line in content.splitlines() if line.strip()]

    decks = load_cached_decks()

    if user_cards:
        suggestions = suggest_decks(user_cards, selected_deck_type, decks)
        if suggestions:
            st.subheader(f"Decks matching your cards ({len(suggestions)} found):")
            for deck in suggestions:
                st.markdown(f"### {deck['name']} ({deck['deck_type']})")
                st.write(f"Author: {deck['author']}")
                st.write(f"Format: {deck['format']}")
                st.write("Cards:")
                st.write(", ".join(deck["cards"]))
                st.markdown("---")
        else:
            st.write("No matching decks found.")
    else:
        st.write("Upload your card list to see deck suggestions.")

if __name__ == "__main__":
    main()
