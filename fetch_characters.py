"""
fetch_characters.py
-------------------
Fetches characters from the Rick and Morty REST API and exports
the filtered results to a CSV file.

Filtering criteria:
    - Species : Human
    - Status  : Alive
    - Origin  : Contains "Earth" (e.g. "Earth (C-137)", "Earth (Replacement Dimension)")

Output columns:
    Name, Location, Image

Usage:
    python fetch_characters.py

Dependencies:
    requests
"""

import requests
import csv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_URL = "https://rickandmortyapi.com/api/character"
OUTPUT_FILE = "characters.csv"


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_all_characters() -> list[dict]:
    """Retrieve all Human + Alive characters from the Rick and Morty API.

    The API returns paginated results (20 items per page).  This function
    follows the ``info.next`` URL until all pages have been consumed.

    Query parameters ``species=Human`` and ``status=Alive`` are applied on
    the first request; subsequent requests use the pre-built ``next`` URL
    which already encodes those filters.

    Returns:
        list[dict]: A flat list of character objects as returned by the API.

    Raises:
        requests.HTTPError: If any API request returns a non-2xx status code.
    """
    characters: list[dict] = []
    url: str | None = API_URL
    params: dict = {"species": "Human", "status": "Alive"}

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        characters.extend(data["results"])

        # 'next' is None when the last page has been reached
        url = data["info"]["next"]

        # Query params are embedded in the 'next' URL; do not re-send them
        params = {}

    return characters


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_characters(characters: list[dict]) -> list[dict]:
    """Filter characters whose origin planet contains the word "Earth".

    The API may return origins such as "Earth (C-137)" or
    "Earth (Replacement Dimension)", so a substring match is used rather
    than an exact comparison.

    Args:
        characters (list[dict]): Raw character list from the API.

    Returns:
        list[dict]: Characters whose ``origin.name`` contains "Earth".
    """
    return [
        character for character in characters
        if "Earth" in character["origin"]["name"]
    ]


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def save_to_csv(characters: list[dict], filename: str = OUTPUT_FILE) -> None:
    """Persist the filtered character data to a CSV file.

    Writes a header row followed by one row per character containing the
    fields: Name, Location (current), and Image URL.

    Args:
        characters (list[dict]): Filtered character list to export.
        filename (str): Destination file path. Defaults to ``characters.csv``.
    """
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        # Header row
        writer.writerow(["Name", "Location", "Image"])

        # Data rows
        for character in characters:
            writer.writerow([
                character["name"],
                character["location"]["name"],
                character["image"],
            ])

    print(f"Saved {len(characters)} characters to '{filename}'")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Fetching characters from the Rick and Morty API...")
    all_characters = fetch_all_characters()
    print(f"Total characters retrieved (Human + Alive): {len(all_characters)}")

    filtered_characters = filter_characters(all_characters)
    print(f"Characters after Earth-origin filter: {len(filtered_characters)}")

    save_to_csv(filtered_characters)
