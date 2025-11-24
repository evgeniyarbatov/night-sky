#!/usr/bin/env python3
"""
NASA Planet Image Downloader (Improved)

Downloads up to 20 planet images for each planet from the NASA Image and Video Library.
Includes retry logic, better filtering, and multi-page search.
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
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'NASA-Planet-Downloader/1.0'})
    
    def download_image(self, url, filepath, retries=3):
        """Download image from URL to filepath with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, stream=True, timeout=20)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   ✓ {filepath.name}")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    print(f"   ⚠ Retry {attempt + 1}/{retries - 1} for {filepath.name}")
                    time.sleep(2)
                else:
                    print(f"   ✗ Failed to download {filepath.name}: {e}")
                    return False
        return False

    def is_valid_planet_image(self, item, planet_name):
        """Check if image is a valid planet photo (relaxed filtering)"""
        try:
            data_block = item.get("data", [{}])[0]
            title = data_block.get("title", "").lower()
            desc = data_block.get("description", "").lower()
            keywords = data_block.get("keywords", [])
            keywords_text = " ".join(keywords).lower() if keywords else ""
            
            combined = f"{title} {desc} {keywords_text}"
            
            # Must contain planet name
            if planet_name not in combined:
                return False
            
            # Exclude obvious non-planet images (relaxed - only hard exclusions)
            exclude_terms = [
                "rover on", "landing site", "lander", "from rover",
                "spacecraft diagram", "mission patch", "crew", "astronaut",
                "launch", "rocket", "artist concept", "artist's concept",
                "illustration", "diagram", "schematic"
            ]
            
            if any(term in combined for term in exclude_terms):
                return False
            
            # Prefer images that explicitly mention the planet or show it
            positive_indicators = [
                planet_name, "surface", "atmosphere", "view", "photo",
                "image", "picture", "observation", "captured"
            ]
            
            # Give bonus points for having positive indicators
            has_positive = any(term in combined for term in positive_indicators)
            
            return has_positive
            
        except Exception:
            return False

    def fetch_images_from_page(self, planet_name, page=1):
        """Fetch images from a specific API page"""
        url = f"https://images-api.nasa.gov/search?q={planet_name}&media_type=image&page={page}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('collection', {}).get('items', [])
            metadata = data.get('collection', {}).get('metadata', {})
            total_hits = metadata.get('total_hits', 0)
            
            return items, total_hits
        except Exception as e:
            print(f"   ⚠ Failed to fetch page {page}: {e}")
            return [], 0

    def download_planet_images(self, planet_name, max_images=20):
        """Download up to max_images for a given planet"""
        print(f"\n🔭 Downloading images for: {planet_name.capitalize()}")
        
        # Collect items from multiple pages
        all_valid_items = []
        pages_to_check = min(5, max_images // 2)  # Check up to 5 pages
        
        for page in range(1, pages_to_check + 1):
            items, total_hits = self.fetch_images_from_page(planet_name, page)
            
            if page == 1:
                print(f"   📊 Total hits in NASA library: {total_hits}")
            
            if not items:
                break
            
            # Filter valid planet images
            for item in items:
                if self.is_valid_planet_image(item, planet_name):
                    all_valid_items.append(item)
            
            time.sleep(0.5)  # Be nice to NASA's API
        
        if not all_valid_items:
            print(f"   ✗ No valid images found for '{planet_name}'")
            return False
        
        print(f"   📸 Found {len(all_valid_items)} valid images")
        
        # Shuffle and limit to max_images
        random.shuffle(all_valid_items)
        items_to_download = all_valid_items[:max_images]
        
        count = 0
        for item in items_to_download:
            try:
                image_data = item['data'][0]
                asset_url = item['href']
                
                # Get image asset links
                asset_response = self.session.get(asset_url, timeout=10)
                asset_response.raise_for_status()
                assets = asset_response.json()
                
                # Find best quality image (prefer original, then large)
                image_url = None
                for asset in assets:
                    if 'orig' in asset or 'large' in asset:
                        if asset.endswith(('.jpg', '.jpeg', '.png')):
                            image_url = asset
                            break
                
                # Fallback to any image
                if not image_url:
                    image_url = next((a for a in assets if a.endswith(('.jpg', '.jpeg', '.png'))), None)
                
                if not image_url:
                    continue
                
                # Create unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                nasa_id = image_data.get('nasa_id', 'unknown')[:30]
                filename = f"{planet_name}_{nasa_id}_{timestamp}.jpg"
                filepath = self.download_dir / filename
                
                # Download image
                if self.download_image(image_url, filepath):
                    count += 1
                    
                    # Save metadata
                    desc_filename = f"{filename}.md"
                    desc_filepath = self.download_dir / desc_filename
                    desc_content = (
                        f"# {image_data.get('title', 'Unknown')}\n\n"
                        f"**Planet:** {planet_name.capitalize()}\n"
                        f"**NASA ID:** {image_data.get('nasa_id', 'Unknown')}\n"
                        f"**Date Created:** {image_data.get('date_created', 'Unknown')}\n"
                        f"**Center:** {image_data.get('center', 'Unknown')}\n\n"
                        f"## Description\n\n"
                        f"{image_data.get('description', 'No description available.')}\n\n"
                        f"## Keywords\n\n"
                        f"{', '.join(image_data.get('keywords', ['None']))}\n"
                    )
                    with open(desc_filepath, "w", encoding="utf-8") as f:
                        f.write(desc_content)
                    
                    if count >= max_images:
                        break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ✗ Error processing image: {e}")
                continue
        
        print(f"   ✅ Successfully downloaded {count}/{max_images} images for {planet_name}")
        return count > 0

    def download_all(self):
        """Download images for all planets"""
        print("🚀 NASA Planet Image Downloader (Improved)")
        print("=" * 60)
        
        planets = [
            "mercury", "venus", "earth", "mars",
            "jupiter", "saturn", "uranus", "neptune"
        ]
        
        results = []
        start_time = time.time()
        
        for planet in planets:
            success = self.download_planet_images(planet, max_images=20)
            results.append((planet, success))
            time.sleep(1)  # Pause between planets
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📋 Summary:")
        for planet, success in results:
            status = "✓" if success else "✗"
            print(f"   {status} {planet.capitalize()}")
        
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
        print(f"📁 All images saved to: {self.download_dir.absolute()}")

if __name__ == "__main__":
    downloader = PlanetImageDownloader(download_dir="planets")
    downloader.download_all()