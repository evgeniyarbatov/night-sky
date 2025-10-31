#!/usr/bin/env python3
"""
NASA Planet Image Downloader (Filtered & Randomized)

Downloads 20 *planet-only* images for each planet from the NASA Image and Video Library.
Each run fetches a new random set of images and excludes spacecraft, rover, or mission photos.
"""

import requests
import json
import time
import random
from datetime import datetime
from pathlib import Path

class PlanetImageDownloader:
    def __init__(self, download_dir="planets"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.api_key = "qqHhUU52eMENdo5DgwhciF7c4R6QRXRujeVrIyRF"  # NASA demo key
    
    def download_image(self, url, filepath):
        """Download image from URL to filepath"""
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"   ✓ {filepath.name}")
            return True
        except Exception as e:
            print(f"   ✗ Failed to download {url}: {e}")
            return False

    def download_planet_images(self, planet_name, max_images=20):
        """Download up to `max_images` filtered NASA images for a given planet"""
        print(f"\n🔭 Downloading images for: {planet_name.capitalize()}")

        # Randomize API page for new results each run
        page = random.randint(1, 20)
        url = f"https://images-api.nasa.gov/search?q={planet_name}+planet&media_type=image&page={page}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get('collection', {}).get('items', [])

            if not items:
                print(f"   No images found for '{planet_name}'.")
                return False

            # Filter to exclude spacecraft, missions, etc.
            filtered_items = []
            for item in items:
                data_block = item.get("data", [{}])[0]
                title = data_block.get("title", "").lower()
                desc = data_block.get("description", "").lower()
                keywords = " ".join(data_block.get("keywords", [])).lower() if "keywords" in data_block else ""

                combined_text = title + " " + desc + " " + keywords
                if (
                    planet_name in combined_text
                    and "planet" in combined_text
                    and not any(bad in combined_text for bad in [
                        "spacecraft", "rover", "mission", "probe", "satellite", "telescope", "station", "lander"
                    ])
                ):
                    filtered_items.append(item)

            if not filtered_items:
                print(f"   ✗ No valid planet-only images found for '{planet_name}'.")
                return False

            # Shuffle to randomize selection
            random.shuffle(filtered_items)

            count = 0
            for item in filtered_items[:max_images]:
                try:
                    image_data = item['data'][0]
                    asset_url = item['href']

                    # Get image asset links
                    asset_response = requests.get(asset_url, timeout=10)
                    asset_response.raise_for_status()
                    assets = asset_response.json()

                    # Pick first suitable image (JPG/PNG)
                    image_url = next((a for a in assets if a.endswith(('.jpg', '.jpeg', '.png'))), None)
                    if not image_url:
                        continue

                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    filename = f"{planet_name}_{timestamp}.jpg"
                    filepath = self.download_dir / filename

                    # Download image
                    if self.download_image(image_url, filepath):
                        count += 1

                        # Save description
                        desc_filename = f"{filename}.md"
                        desc_filepath = self.download_dir / desc_filename
                        desc_content = (
                            f"# {image_data.get('title', 'Unknown')}\n\n"
                            f"**Planet:** {planet_name}\n"
                            f"**NASA ID:** {image_data.get('nasa_id', 'Unknown')}\n"
                            f"**Date Created:** {image_data.get('date_created', 'Unknown')}\n\n"
                            f"## Description\n\n"
                            f"{image_data.get('description', 'No description available.')}"
                        )
                        with open(desc_filepath, "w", encoding="utf-8") as f:
                            f.write(desc_content)

                    if count >= max_images:
                        break

                    # Be gentle to NASA API
                    time.sleep(1)

                except Exception as e:
                    print(f"   ✗ Error processing image: {e}")
                    continue

            print(f"   ✅ Downloaded {count} images for {planet_name}")
            return True

        except Exception as e:
            print(f"   ✗ Failed to fetch NASA data for {planet_name}: {e}")
            return False

    def download_all(self):
        print("🚀 NASA Planet Image Downloader")
        print("=" * 50)

        planets = [
            "mercury", "venus", "earth", "mars",
            "jupiter", "saturn", "uranus", "neptune"
        ]

        results = []
        for planet in planets:
            success = self.download_planet_images(planet, max_images=20)
            results.append((planet, success))

        print("\n" + "=" * 50)
        print("Summary:")
        for planet, success in results:
            status = "✓" if success else "✗"
            print(f" {status} {planet.capitalize()}")

        print(f"\nAll images saved to: {self.download_dir.absolute()}")

if __name__ == "__main__":
    downloader = PlanetImageDownloader(download_dir="planets")
    downloader.download_all()
