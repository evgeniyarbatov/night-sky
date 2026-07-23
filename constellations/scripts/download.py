import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Base URL for the IAU constellations page
BASE_URL = "https://iauarchive.eso.org/public/themes/constellations/"


def extract_download_links(html: str) -> tuple[list[str], list[str]]:
    """Return (gif_links, txt_links) found in the page's anchor hrefs."""
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    hrefs = [href for link in links if isinstance(href := link["href"], str)]
    gif_links = [href for href in hrefs if href.endswith(".gif")]
    txt_links = [href for href in hrefs if href.endswith(".txt")]
    return gif_links, txt_links


def download_file(url: str, folder: str) -> None:
    local_filename = os.path.join(folder, os.path.basename(url))
    full_url = urljoin(BASE_URL, url)
    with requests.get(full_url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {local_filename}")


def main() -> None:
    response = requests.get(BASE_URL, timeout=30)
    gif_links, txt_links = extract_download_links(response.text)

    os.makedirs("data/gifs", exist_ok=True)
    os.makedirs("data/boundaries", exist_ok=True)

    for url in gif_links:
        download_file(url, "data/gifs")

    for url in txt_links:
        download_file(url, "data/boundaries")

    print("Download complete.")


if __name__ == "__main__":
    main()
