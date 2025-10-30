#!/usr/bin/env python3
"""
NASA Planet Image Downloader

Downloads 20 images for each planet from the NASA Image and Video Library
and saves them into a single folder (no subdirectories).
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

class PlanetImageDownloader:
    def __init__(self, download_dir="planets"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # NASA API key (replace with your own if you have one)
        self.api_key = "qqHhUU52eMENdo5DgwhciF7c4R6QRXRujeVrIyRF"
    
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
        """Download up to `max_images` NASA library images for a given planet"""
        print(f"\n🔭 Downloading images for: {planet_name.capitalize()}")
        
        url = f"https://images-api.nasa.gov/search?q={planet_name}&media_type=image"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get('collection', {}).get('items', [])
            
            if not items:
                print(f"   No images found for '{planet_name}'.")
                return False
            
            count = 0
            for item in items[:max_images]:
                try:
                    image_data = item['data'][0]
                    asset_url = item['href']
                    
                    # Get image asset links
                    asset_response = requests.get(asset_url, timeout=10)
                    asset_response.raise_for_status()
                    assets = asset_response.json()
                    
                    # Pick the first suitable image (JPG/PNG)
                    image_url = next((a for a in assets if a.endswith(('.jpg', '.jpeg', '.png'))), None)
                    if not image_url:
                        continue
                    
                    # Unique filenames
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
