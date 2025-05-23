import streamlit as st
import json

st.title("TCG Deck Builder Helper")

# Load cached decks JSON
@st.cache_data
def load_decks():
    with open("cached_mtgo_decks.json", "r") as f:
        return json.load(f)

decks = load_decks()

# Select TCG
tcg_options = sorted(set(deck["tcg"] for deck in decks))
selected_tcg = st.selectbox("Select your TCG", ["Any"] + tcg_options)

# Select deck type
deck_types = sorted(set(deck["deck_type"] for deck in decks if (selected_tcg == "Any" or deck["tcg"] == selected_tcg)))
selected_deck_type = st.selectbox("Select deck type", ["Any"] + deck_types)

# Upload user cards CSV (one card name per line)
uploaded_file = st.file_uploader("Upload your card list (CSV)")

if uploaded_file:
    user_cards = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]
    st.write(f"You uploaded {len(user_cards)} cards.")

    # Filter decks by TCG and deck type
    filtered_decks = decks
    if selected_tcg != "Any":
        filtered_decks = [d for d in filtered_decks if d["tcg"] == selected_tcg]
    if selected_deck_type != "Any":
        filtered_decks = [d for d in filtered_decks if d["deck_type"] == selected_deck_type]

    # Find decks matching user cards (e.g. at least 30% cards owned)
    matching_decks = []
    for deck in filtered_decks:
        owned = set(deck["cards"]).intersection(user_cards)
        ratio = len(owned) / len(deck["cards"]) if deck["cards"] else 0
        if ratio >= 0.3:
            matching_decks.append((deck, ratio))

    if matching_decks:
        st.subheader(f"Found {len(matching_decks)} matching decks:")
        matching_decks.sort(key=lambda x: x[1], reverse=True)
        for deck, ratio in matching_decks:
            st.markdown(f"### {deck['name']} ({deck['deck_type']}, {deck['tcg']})")
            st.markdown(f"**Author:** {deck['author']}")
            st.markdown(f"**Match:** {ratio:.0%} of deck cards in your collection")
            st.write("Cards in deck:")
            st.write(", ".join(deck["cards"]))
    else:
        st.write("No matching decks found for your collection with the filters selected.")
else:
    st.write("Please upload your card list CSV file.")
