#!/usr/bin/env python3
"""
Bulk download 200 space images using NASA APIs
"""

import requests
import random
from datetime import datetime, timedelta
from pathlib import Path

def download_bulk_images(count=200):
    """Download specified number of space images using NASA APIs"""
    
    # Create images directory if it doesn't exist
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    
    # NASA API key (same as nasa.py)
    api_key = "qqHhUU52eMENdo5DgwhciF7c4R6QRXRujeVrIyRF"
    
    # Space objects for NASA Library search
    space_objects = [
        "mars", "jupiter", "saturn", "venus", "mercury", "uranus", "neptune", "earth",
        "comet", "galaxy", "andromeda", "milky way", "betelgeuse", "sirius", "vega", "polaris"
    ]
    
    print(f"🚀 Downloading {count} space images from NASA APIs...")
    
    success_count = 0
    
    for i in range(1, count + 1):
        try:
            # Alternate between APOD and NASA Library
            if i % 2 == 1:  # APOD for odd numbers
                if download_apod_image(api_key, images_dir, i):
                    success_count += 1
            else:  # NASA Library for even numbers
                if download_nasa_library_image(space_objects, images_dir, i):
                    success_count += 1
            
            print(f"Progress: {i}/{count} (Success: {success_count})")
            
        except Exception as e:
            print(f"Error downloading image {i}: {e}")
            continue
    
    print(f"Successfully downloaded {success_count}/{count} images to {images_dir}/")

def download_apod_image(api_key, images_dir, index):
    """Download APOD image from random date"""
    # Generate random date within last 2 years for more variety
    today = datetime.now()
    two_years_ago = today - timedelta(days=730)
    random_days = random.randint(0, 730)
    random_date = two_years_ago + timedelta(days=random_days)
    date_str = random_date.strftime('%Y-%m-%d')
    
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={date_str}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('media_type') == 'image':
            image_url = data['url']
            filename = f"apod_{index:03d}_{date_str}.jpg"
            filepath = images_dir / filename
            
            # Save description
            title = data['title'].replace('/', '_').replace(':', '_').replace('?', '').replace('<', '').replace('>', '').replace('|', '_').replace('"', '').replace('*', '')
            description_filename = f"apod_{index:03d}_{date_str}.md"
            description_filepath = images_dir / description_filename
            description_content = f"# {data['title']}\n\n**Date:** {data['date']}\n**URL:** {data.get('hdurl', data['url'])}\n**Index:** {index}\n\n## Description\n\n{data.get('explanation', 'No description')}"
            
            with open(description_filepath, 'w', encoding='utf-8') as f:
                f.write(description_content)
            
            if download_image(image_url, filepath):
                return True
            else:
                # Clean up description file if image download failed
                description_filepath.unlink(missing_ok=True)
                return False
        else:
            # If it's a video, try again with different date
            return download_apod_image(api_key, images_dir, index)
            
    except Exception:
        return False

def download_nasa_library_image(space_objects, images_dir, index):
    """Download image from NASA Image Library"""
    search_term = random.choice(space_objects)
    url = f"https://images-api.nasa.gov/search?q={search_term}&media_type=image"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = data.get('collection', {}).get('items', [])
        if not items:
            return False
        
        # Get a random image from the results
        item = random.choice(items[:20])
        image_data = item['data'][0]
        
        # Get the actual image URL
        asset_url = item['href']
        asset_response = requests.get(asset_url, timeout=10)
        asset_response.raise_for_status()
        assets = asset_response.json()
        
        # Find the largest image
        image_url = None
        for asset in assets:
            if asset.endswith(('.jpg', '.jpeg', '.png')):
                image_url = asset
                break
        
        if not image_url:
            return False
        
        filename = f"nasa_{index:03d}_{search_term}.jpg"
        filepath = images_dir / filename
        
        # Save description
        description_filename = f"nasa_{index:03d}_{search_term}.md"
        description_filepath = images_dir / description_filename
        description_content = f"# {image_data.get('title', 'Unknown')}\n\n**Search term:** {search_term}\n**NASA ID:** {image_data.get('nasa_id', 'Unknown')}\n**Date created:** {image_data.get('date_created', 'Unknown')}\n**Index:** {index}\n\n## Description\n\n{image_data.get('description', 'No description')}"
        
        with open(description_filepath, 'w', encoding='utf-8') as f:
            f.write(description_content)
        
        if download_image(image_url, filepath):
            return True
        else:
            # Clean up description file if image download failed
            description_filepath.unlink(missing_ok=True)
            return False
        
    except Exception:
        return False

def download_image(url, filepath):
    """Download image from URL to filepath"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception:
        return False

if __name__ == "__main__":
    download_bulk_images(200)