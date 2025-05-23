import streamlit as st
import json

# Load decks JSON (adjust path to your JSON file)
@st.cache_data
def load_decks():
    with open("cached_mtgo_decks.json", "r") as f:
        return json.load(f)

decks = load_decks()

st.title("MTG Deck Suggestion App")

# Select deck type filter
deck_types = sorted(set(deck["deck_type"] for deck in decks))
selected_deck_type = st.selectbox("Select deck type", ["Any"] + deck_types)

# Upload user card list file (expecting CSV with one card name per line)
uploaded_file = st.file_uploader("Upload your card list (CSV)")

if uploaded_file:
    user_cards = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]
    st.write(f"You uploaded {len(user_cards)} cards.")

    # Filter decks by deck type if selected
    filtered_decks = decks if selected_deck_type == "Any" else [d for d in decks if d["deck_type"] == selected_deck_type]

    # Find decks that match user cards (e.g. at least 30% of deck cards in user collection)
    matching_decks = []
    for deck in filtered_decks:
        match_count = len(set(deck["cards"]).intersection(user_cards))
        match_ratio = match_count / len(deck["cards"])
        if match_ratio >= 0.3:  # Threshold for "good enough" match
            matching_decks.append((deck, match_ratio))

    if matching_decks:
        st.subheader(f"Found {len(matching_decks)} matching decks:")
        # Sort by best match ratio descending
        matching_decks.sort(key=lambda x: x[1], reverse=True)
        for deck, ratio in matching_decks:
            st.markdown(f"### {deck['name']} ({deck['deck_type']})")
            st.markdown(f"**Author:** {deck['author']}")
            st.markdown(f"**Match:** {ratio:.0%} of deck cards in your collection")
            st.write("Cards in deck:")
            st.write(", ".join(deck["cards"]))
    else:
        st.write("No matching decks found for your card collection and selected deck type.")
else:
    st.write("Please upload your card list CSV file to see matching decks.")
