#!/usr/bin/env python
"""Generate Android app icons from source image."""

from PIL import Image
import os

# Android icon sizes (in pixels)
ICON_SIZES = {
    'mipmap-xxxhdpi': 192,
    'mipmap-xxhdpi': 144,
    'mipmap-xhdpi': 96,
    'mipmap-hdpi': 72,
    'mipmap-mdpi': 48,
    'mipmap-ldpi': 36,
}

SOURCE_IMAGE = r"C:\Users\Administrator\Downloads\Image_1779022239292_699.png"
OUTPUT_DIR = r"C:\Users\Administrator\WorkBuddy\2026-05-22-21-43-05\FurryChatApp\android_icons"

def generate_icons():
    # Load source image
    img = Image.open(SOURCE_IMAGE)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate foreground and background icons (adaptive icons for Android 8+)
    for folder, size in ICON_SIZES.items():
        folder_path = os.path.join(OUTPUT_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Resize for ic_launcher.png (legacy icon)
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(folder_path, 'ic_launcher.png'))
        
        # Also save as ic_launcher_foreground.png for adaptive icons
        resized.save(os.path.join(folder_path, 'ic_launcher_foreground.png'))
        
        # Create a simple background (white/transparent)
        bg = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        bg.save(os.path.join(folder_path, 'ic_launcher_background.png'))
        
        print(f"✅ Generated {folder}/{size}px icons")
    
    print(f"\n✅ All icons generated in: {OUTPUT_DIR}")

if __name__ == '__main__':
    generate_icons()
