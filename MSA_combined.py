import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import re
import os

# Target directory to save the final CSV
output_path = r"C:\Users\BW\OneDrive\Documents\web scrape\mixed_sex_accommodation_combined.csv"

# URL of the NHS England MSA data page
url = "https://www.england.nhs.uk/statistics/statistical-work-areas/mixed-sex-accommodation/msa-data/"
base_url = "https://www.england.nhs.uk"

# Fetch and parse the HTML page
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

# Pattern to match "Mixed-Sex Accommodation – Month Year"
pattern = re.compile(r"Mixed[- ]Sex[- ]Accommodation\s*–\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}", re.IGNORECASE)

data_frames = []

# Loop through all <a> tags with href
for link in soup.find_all('a', href=True):
    link_text = link.get_text(strip=True)
    href = link['href']

    if pattern.search(link_text) and (href.endswith('.xlsx') or href.endswith('.xls')):
        file_url = href if href.startswith('http') else base_url + href
        print(f"Downloading: {link_text} from {file_url}")
        file_response = requests.get(file_url)
        file_response.raise_for_status()

        try:
            if file_url.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(file_response.content), engine='xlrd')
            else:
                df = pd.read_excel(io.BytesIO(file_response.content), engine='openpyxl')

            df['Source File'] = link_text
            data_frames.append(df)
        except Exception as e:
            print(f"Failed to read {link_text}: {e}")

# Combine and export
if data_frames:
    combined_df = pd.concat(data_frames, ignore_index=True)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    combined_df.to_csv(output_path, index=False)
    print(f"Saved combined CSV as '{output_path}'")
else:
    print("No files were processed.")
