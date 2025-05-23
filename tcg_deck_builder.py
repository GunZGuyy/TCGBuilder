import streamlit as st
import pandas as pd
import requests
from collections import Counter

TCG_OPTIONS = ["Magic: The Gathering", "Yu-Gi-Oh!"]
DECK_TYPES = {
    "Magic: The Gathering": ["Aggro", "Control", "Combo", "Midrange"],
    "Yu-Gi-Oh!": ["Beatdown", "Control", "Combo"]
}

# Static example Yu-Gi-Oh! decks with card lists (for demo purposes)
YUGIOH_DECKS = [
    {
        "name": "Dragon Beatdown",
        "cards": [
            "Blue-Eyes White Dragon", "Red-Eyes Black Dragon", "Dragon Spirit of White",
            "Lord of D.", "Dragon Master Knight", "Dragon Ravine", "Return of the Dragon Lords",
            "Dragon Shrine", "Trade-In", "Monster Reborn"
        ]
    },
    {
        "name": "Dark Control",
        "cards": [
            "Dark Magician", "Dark Magician Girl", "Magician's Rod", "Magician's Navigation",
            "Dark Magical Circle", "Eternal Soul", "Magicalized Fusion",
            "Skill Drain", "Mystical Space Typhoon", "Trap Hole"
        ]
    },
    {
        "name": "Spellcaster Combo",
        "cards": [
            "Performapal Skullcrobat Joker", "Pendulum Sorcerer", "Time Pendulumgraph",
            "Wavering Eyes", "Pendulum Call", "Tuning", "Secret Village of the Spellcasters",
            "Mystical Space Typhoon", "Dark Hole", "Twin Twisters"
        ]
    }
]

def parse_card_list(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        if 'Card' not in df.columns:
            st.error("CSV must contain a column named 'Card'.")
            return []
        return df['Card'].dropna().tolist()
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return []

def fetch_mtg_decklist(deck_id):
    url = f"https://api.moxfield.com/v2/decks/{deck_id}"
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            mainboard = data.get('mainboard', {})
            return list(mainboard.keys())
    except:
        pass
    return []

def find_mtg_builds(card_list, deck_type):
    builds = []
    collection_counter = Counter(card_list)
    query = deck_type.lower()
    url = f"https://api.moxfield.com/v2/decks/search?q={query}&format=commander&pageNumber=1&pageSize=10"

    try:
        response = requests.get(url)
        if not response.ok:
            st.warning("Failed to contact Moxfield.")
            return []

        data = response.json()
        decks = data.get('data', [])

        for deck in decks:
            deck_id = deck.get('publicId')
            deck_name = deck.get('name', 'Unnamed Deck')
            deck_cards = fetch_mtg_decklist(deck_id)

            deck_counter = Counter(deck_cards)
            match_count = sum(min(collection_counter[card], count) for card, count in deck_counter.items())
            total_cards = sum(deck_counter.values())

            if total_cards == 0:
                continue

            match_percent = (match_count / total_cards) * 100
            if match_percent >= 50:
                builds.append({
                    "title": f"{deck_name} ({match_percent:.0f}% match)",
                    "cards": deck_cards[:10],
                    "notes": f"Deck from Moxfield. You own about {match_percent:.0f}% of the required cards."
                })

    except Exception as e:
        st.error(f"Error matching MTG builds: {e}")

    return builds

def find_yugioh_builds(card_list, deck_type):
    builds = []
    collection_counter = Counter(card_list)

    # Filter example decks by name matching deck_type (simple keyword filter)
    filtered_decks = [deck for deck in YUGIOH_DECKS if deck_type.lower() in deck["name"].lower() or deck_type.lower() in " ".join(deck["name"].lower().split())]

    if not filtered_decks:
        # fallback to all decks if none matches deck_type text
        filtered_decks = YUGIOH_DECKS

    for deck in filtered_decks:
        deck_counter = Counter(deck["cards"])
        match_count = sum(min(collection_counter[card], count) for card, count in deck_counter.items())
        total_cards = sum(deck_counter.values())
        match_percent = (match_count / total_cards) * 100 if total_cards > 0 else 0

        if match_percent >= 50:
            builds.append({
                "title": f"{deck['name']} ({match_percent:.0f}% match)",
                "cards": deck["cards"][:10],
                "notes": f"Static example deck. You own about {match_percent:.0f}% of the cards."
            })

    return builds

def find_builds(tcg, card_list, deck_type):
    if tcg == "Magic: The Gathering":
        return find_mtg_builds(card_list, deck_type)
    elif tcg == "Yu-Gi-Oh!":
        return find_yugioh_builds(card_list, deck_type)
    else:
        return []

# UI
st.title("TCG Deck Builder Assistant (Magic & Yu-Gi-Oh!)")

tcg_choice = st.selectbox("Select Your TCG", TCG_OPTIONS)
deck_type = st.selectbox("Select Deck Type", DECK_TYPES[tcg_choice])

uploaded_file = st.file_uploader("Upload Your Card List (CSV with column 'Card')", type="csv")

if uploaded_file:
    card_list = parse_card_list(uploaded_file)
    if card_list:
        st.success(f"{len(card_list)} cards loaded.")
        if st.button("Generate Deck Builds"):
            st.write(f"Matching builds for: {tcg_choice} - {deck_type}")
            st.write("Your cards preview:", card_list[:5])
            builds = find_builds(tcg_choice, card_list, deck_type)
            if builds:
                for build in builds:
                    st.subheader(build["title"])
                    st.write("**Cards (partial):**")
                    st.write(", ".join(build["cards"]))
                    st.write("**Notes:**")
                    st.write(build["notes"])
            else:
                st.warning("No well-matched builds found. Try a different deck type or upload more cards.")
