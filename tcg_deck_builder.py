import streamlit as st
import pandas as pd
import requests
from typing import List

# Create a session to persist headers and cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.moxfield.com/",
    "Origin": "https://www.moxfield.com",
})

@st.cache_data(ttl=600)
def fetch_recent_moxfield_decks(format_name="standard", max_decks=20) -> List[dict]:
    url = f"https://api.moxfield.com/v2/decks?format={format_name}&sort=recent&size={max_decks}"
    try:
        # Pre-visit homepage to get cookies
        session.get("https://www.moxfield.com/", timeout=5)
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        decks_data = response.json()
        decks = []
        for deck in decks_data.get("data", []):
            decks.append({
                "id": deck["id"],
                "name": deck["name"],
                "author": deck.get("author", {}).get("username", "unknown"),
            })
        return decks
    except Exception as e:
        st.warning(f"Failed to fetch decks from Moxfield: {e}")
        return []

@st.cache_data(ttl=600)
def fetch_decklist(deck_id: str) -> List[str]:
    url = f"https://api.moxfield.com/v2/decks/{deck_id}/slots"
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        slots = response.json()
        cards = []
        for card_info in slots.values():
            card_name = card_info.get("card", {}).get("name")
            if card_name:
                cards.append(card_name)
        return cards
    except Exception as e:
        st.warning(f"Failed to fetch decklist for deck {deck_id}: {e}")
        return []

def load_card_list(file) -> set:
    try:
        df = pd.read_csv(file)
        cards = set(df['Card'].str.strip().str.lower())
        return cards
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return set()

def suggest_decks(user_cards: set, decks_info: List[dict]) -> List[dict]:
    suggestions = []
    for deck in decks_info:
        deck_cards = fetch_decklist(deck["id"])
        deck_cards_set = set(card.lower() for card in deck_cards)
        matched = user_cards.intersection(deck_cards_set)
        match_ratio = len(matched) / len(deck_cards_set) if deck_cards_set else 0
        if match_ratio > 0:
            suggestions.append({
                "deck_name": deck["name"],
                "author": deck["author"],
                "match_count": len(matched),
                "total_cards": len(deck_cards_set),
                "match_ratio": match_ratio,
                "missing_cards": deck_cards_set - matched,
                "deck_url": f"https://www.moxfield.com/decks/{deck['id']}"
            })

    suggestions.sort(key=lambda x: (x['match_ratio'], x['match_count']), reverse=True)
    return suggestions

def main():
    st.title("MTG Deck Builder Helper with Moxfield Scraper")

    game = st.selectbox("Select your Trading Card Game", ["Magic: The Gathering"])
    if game != "Magic: The Gathering":
        st.info("Currently only Magic: The Gathering with Moxfield scraping is supported.")
        return

    format_map = {
        "Standard": "standard",
        "Modern": "modern",
        "Pioneer": "pioneer",
        "Historic": "historic",
        "Legacy": "legacy",
        "Vintage": "vintage",
        "Commander": "commander",
    }
    selected_format = st.selectbox("Select Format", list(format_map.keys()))

    uploaded_file = st.file_uploader("Upload your card list CSV file (must have 'Card' column)", type=["csv"])

    if uploaded_file:
        user_cards = load_card_list(uploaded_file)
        if not user_cards:
            st.warning("No cards loaded from your file.")
            return
        st.write(f"Loaded {len(user_cards)} unique cards from your list.")

        with st.spinner(f"Fetching recent {selected_format} decks from Moxfield..."):
            decks_info = fetch_recent_moxfield_decks(format_map[selected_format], max_decks=20)

        if not decks_info:
            st.warning("No decks found or failed to fetch decks.")
            return

        st.write(f"Fetched {len(decks_info)} recent decks from Moxfield.")

        with st.spinner("Comparing your cards with fetched decks..."):
            suggestions = suggest_decks(user_cards, decks_info)

        if not suggestions:
            st.info("No matching decks found for your card list in recent decks.")
        else:
            st.subheader("Suggested Deck Builds from Moxfield:")
            for suggestion in suggestions[:10]:
                st.markdown(f"### [{suggestion['deck_name']}]({suggestion['deck_url']}) by {suggestion['author']}")
                st.write(f"Matched cards: {suggestion['match_count']} / {suggestion['total_cards']} "
                         f"({suggestion['match_ratio']*100:.1f}%)")
                missing = suggestion['missing_cards']
                if missing:
                    st.write("Missing cards:", ", ".join(sorted(missing)))
                else:
                    st.write("You have all the cards for this deck!")

if __name__ == "__main__":
    main()
