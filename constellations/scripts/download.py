import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the IAU constellations page
BASE_URL = "https://iauarchive.eso.org/public/themes/constellations/"

# Fetch the page content
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to GIF and TXT files
links = soup.find_all('a', href=True)
gif_links = [link['href'] for link in links if link['href'].endswith('.gif')]
txt_links = [link['href'] for link in links if link['href'].endswith('.txt')]

# Create directories for storing the files
os.makedirs('data/gifs', exist_ok=True)
os.makedirs('data/boundaries', exist_ok=True)

# Function to download files
def download_file(url, folder):
    local_filename = os.path.join(folder, os.path.basename(url))
    full_url = urljoin(BASE_URL, url)
    with requests.get(full_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {local_filename}")

# Download GIFs
for url in gif_links:
    download_file(url, 'data/gifs')

# Download TXT files
for url in txt_links:
    download_file(url, 'data/boundaries')

print("Download complete.")
