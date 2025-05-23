
import streamlit as st
import pandas as pd
import requests

TCG_OPTIONS = ["Magic: The Gathering", "Yu-Gi-Oh!", "Pokémon"]
DECK_TYPES = {
    "Magic: The Gathering": ["Aggro", "Control", "Combo", "Midrange"],
    "Yu-Gi-Oh!": ["Beatdown", "Control", "Combo"],
    "Pokémon": ["Standard", "Expanded", "Theme"]
}

def parse_card_list(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        return df['Card'].tolist()
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return []

def find_builds(tcg, card_list, deck_type):
    if tcg == "Magic: The Gathering":
        return find_mtg_builds(card_list, deck_type)
    elif tcg == "Yu-Gi-Oh!":
        return find_yugioh_builds(card_list, deck_type)
    elif tcg == "Pokémon":
        return find_pokemon_builds(card_list, deck_type)
    else:
        return []

def find_mtg_builds(card_list, deck_type):
    builds = []
    query = deck_type.lower()
    url = f"https://api.moxfield.com/v2/decks/search?q={query}&format=commander&pageNumber=1&pageSize=5"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        for deck in data.get('data', []):
            deck_name = deck.get('name', 'Unnamed Deck')
            builds.append({
                "title": f"{deck_name} (MTG - {deck_type})",
                "cards": [card for card in card_list[:10]],
                "notes": f"Deck from Moxfield: {deck_name}"
            })
    return builds

def find_yugioh_builds(card_list, deck_type):
    builds = []
    url = f"https://db.ygoprodeck.com/api/v7/decktypes.php"
    response = requests.get(url)
    if response.ok:
        types = response.json().get('data', [])
        builds.append({
            "title": f"Sample Yu-Gi-Oh! {deck_type} Deck",
            "cards": card_list[:10],
            "notes": f"Suggested from common Yu-Gi-Oh! deck types."
        })
    return builds

def find_pokemon_builds(card_list, deck_type):
    builds = []
    builds.append({
        "title": f"Sample Pokémon {deck_type} Deck",
        "cards": card_list[:10],
        "notes": "Static example build for Pokémon TCG."
    })
    return builds

# UI
st.title("TCG Deck Builder Assistant")

tcg_choice = st.selectbox("Select Your TCG", TCG_OPTIONS)
deck_type = st.selectbox("Select Deck Type", DECK_TYPES[tcg_choice])

uploaded_file = st.file_uploader("Upload Your Card List (CSV with column 'Card')", type="csv")

if uploaded_file:
    card_list = parse_card_list(uploaded_file)
    if card_list:
        st.success(f"{len(card_list)} cards loaded.")
        if st.button("Generate Deck Builds"):
            builds = find_builds(tcg_choice, card_list, deck_type)
            for build in builds:
                st.subheader(build["title"])
                st.write("**Cards:**")
                st.write(", ".join(build["cards"]))
                st.write("**Notes:**")
                st.write(build["notes"])
