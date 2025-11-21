import requests
import pandas as pd
import os

os.makedirs("data/raw", exist_ok=True)

DATASETS = {
    "current_2024_plus": "business-licences",
    "1997_2012": "business-licences-1997-to-2012",
    "2013_2024": "business-licences-2013-to-2024"
}

BASE_URL = (
    "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/{}/records?limit=-1"
)

def fetch_and_save(name, dataset_id):
    url = BASE_URL.format(dataset_id)
    print(f"Fetching: {url}")

    # GET JSON from the API
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # Extract rows → DataFrame
    rows = data["results"]
    df = pd.DataFrame(rows)

    # Save to CSV
    output_path = f"data/raw/{name}.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved → {output_path}\n")

for name, dataset_id in DATASETS.items():
    fetch_and_save(name, dataset_id)
