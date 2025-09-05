#!/usr/bin/env python3
"""
NASA Space Image Downloader

Downloads images from:
1. Astronomy Picture of the Day (APOD) API
2. NASA Image and Video Library (random space object search)
"""

import requests
import os
import json
from datetime import datetime, timedelta
import random
from pathlib import Path

class SpaceImageDownloader:
    def __init__(self, download_dir="images"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # NASA API key - you can get one at https://api.nasa.gov/
        # Using DEMO_KEY for now (limited requests)
        self.api_key = "qqHhUU52eMENdo5DgwhciF7c4R6QRXRujeVrIyRF"
        
        # No subdirectories needed
    
    def download_image(self, url, filepath):
        """Download image from URL to filepath"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Downloaded: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Failed to download {url}: {e}")
            return False
    
    def download_apod(self):
        """Download Astronomy Picture of the Day from random day within last year"""
        # Generate random date within last year
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        random_days = random.randint(0, 365)
        random_date = one_year_ago + timedelta(days=random_days)
        date_str = random_date.strftime('%Y-%m-%d')
        
        url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&date={date_str}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('media_type') == 'image':
                image_url = data['url']
                filename = "apod_today.jpg"
                filepath = self.download_dir / filename
                
                print(f"APOD: {data['title']} ({data['date']})")
                print(f"Description: {data.get('explanation', 'No description')[:100]}...")
                
                return self.download_image(image_url, filepath)
            else:
                print("APOD today is a video, not an image")
                return False
                
        except Exception as e:
            print(f"Failed to fetch APOD: {e}")
            return False
    
    
    def download_nasa_library_random(self):
        """Search and download random space object from NASA Image Library"""
        space_objects = [
            "mars", "jupiter", "saturn", "nebula", "galaxy", "asteroid",
            "comet", "space station", "shuttle", "telescope", "rover",
            "solar", "lunar", "earth", "venus", "mercury", "uranus", "neptune"
        ]
        
        search_term = random.choice(space_objects)
        url = f"https://images-api.nasa.gov/search?q={search_term}&media_type=image"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('collection', {}).get('items', [])
            if not items:
                print(f"No images found for '{search_term}'")
                return False
            
            # Get a random image from the results
            item = random.choice(items[:20])  # From first 20 results
            image_data = item['data'][0]
            
            # Get the actual image URL
            asset_url = item['href']
            asset_response = requests.get(asset_url)
            asset_response.raise_for_status()
            assets = asset_response.json()
            
            # Find the largest image
            image_url = None
            for asset in assets:
                if asset.endswith(('.jpg', '.jpeg', '.png')):
                    image_url = asset
                    break
            
            if not image_url:
                print(f"No suitable image found for '{search_term}'")
                return False
            
            filename = f"nasa_library_{search_term}.jpg"
            filepath = self.download_dir / filename
            
            print(f"NASA Library: {image_data.get('title', 'Unknown')}")
            print(f"Search term: {search_term}")
            print(f"Description: {image_data.get('description', 'No description')[:100]}...")
            
            return self.download_image(image_url, filepath)
            
        except Exception as e:
            print(f"Failed to fetch from NASA Library: {e}")
            return False
    
    def download_all(self):
        """Download from all three sources"""
        print("🚀 NASA Space Image Downloader")
        print("=" * 40)
        
        results = []
        
        print("\n1. Downloading Astronomy Picture of the Day...")
        results.append(("APOD", self.download_apod()))
        
        print("\n2. Downloading random space object from NASA Library...")
        results.append(("NASA Library", self.download_nasa_library_random()))
        
        print("\n" + "=" * 40)
        print("Summary:")
        for source, success in results:
            status = "✓" if success else "✗"
            print(f"{status} {source}")
        
        print(f"\nImages saved to: {self.download_dir.absolute()}")

if __name__ == "__main__":
    downloader = SpaceImageDownloader()
    downloader.download_all()