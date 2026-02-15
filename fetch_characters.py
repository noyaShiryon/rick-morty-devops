import requests
import csv

API_URL = "https://rickandmortyapi.com/api/character"
OUTPUT_FILE = "characters.csv"


def fetch_all_characters():
    """Fetch all characters from the Rick and Morty API (handles pagination)."""
    characters = []
    url = API_URL
    params = {"species": "Human", "status": "Alive"}

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        characters.extend(data["results"])

        # Move to next page (None if last page)
        url = data["info"]["next"]
        params = {}  # params only needed for first request

    return characters


def filter_characters(characters):
    """Keep only characters whose origin contains 'Earth'."""
    return [
        c for c in characters
        if "Earth" in c["origin"]["name"]
    ]


def save_to_csv(characters, filename=OUTPUT_FILE):
    """Save the filtered characters to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Location", "Image"])
        for c in characters:
            writer.writerow([
                c["name"],
                c["location"]["name"],
                c["image"]
            ])
    print(f"Saved {len(characters)} characters to {filename}")


if __name__ == "__main__":
    print("Fetching characters...")
    all_characters = fetch_all_characters()
    print(f"Total fetched: {len(all_characters)}")

    filtered = filter_characters(all_characters)
    print(f"After Earth filter: {len(filtered)}")

    save_to_csv(filtered)
