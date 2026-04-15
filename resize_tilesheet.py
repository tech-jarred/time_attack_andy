import os
from PIL import Image

def convert_18_to_16_tilemap(input_filename, output_filename):
    """
    Converts an 18x18 tilemap to a clean 16x16 tilemap by cropping the center.
    """
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' not found.")
        return

    # Open the input image
    try:
        source_image = Image.open(input_filename).convert('RGBA')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    source_width, source_height = source_image.size
    
    # Calculate the grid dimensions (assumes no extra padding/margins on sheet)
    tiles_x = source_width // 18
    tiles_y = source_height // 18

    # We are packing the new 16x16 tiles into a smaller sheet
    new_width = tiles_x * 16
    new_height = tiles_y * 16

    # Create a new blank image with transparency
    output_image = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

    print(f"Processing '{input_filename}'...")
    print(f" Detected Grid: {tiles_x}x{tiles_y} tiles (Original Size: {source_width}x{source_height})")
    print(f" Creating New Sheet: {new_width}x{new_height} pixels (Compact 16x16 format)")

    # The conversion loop
    for y in range(tiles_y):
        for x in range(tiles_x):
            # 1. Define the 18x18 "frame" coordinates on source sheet
            src_x = x * 18
            src_y = y * 18
            
            # 2. Define the 16x16 "content" (center 16x16 of the 18x18 block)
            # This logic effectively crops the 1px border.
            content_left = src_x + 1
            content_top = src_y + 1
            content_right = content_left + 16
            content_bottom = content_top + 16
            
            # 3. Crop the content from source
            tile_content = source_image.crop((content_left, content_top, content_right, content_bottom))
            
            # 4. Define destination coordinates on the new 16x16 sheet
            dest_x = x * 16
            dest_y = y * 16
            
            # 5. Paste the 16x16 content into the new sheet
            output_image.paste(tile_content, (dest_x, dest_y))

    # Save the result
    output_image.save(output_filename)
    print(f"Successfully converted and saved as '{output_filename}'.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Define your input and output names here.
    # We recommend changing the original file names for clarity.
    convert_18_to_16_tilemap('avoidland_tilemap.png', 'avoidland_tilemap_16x16.png')
    convert_18_to_16_tilemap('keyboard-&-mouse_sheet_default.png', 'keyboard_tilemap_16x16.png')
    convert_18_to_16_tilemap('tilemap-characters_packed.png', 'characters_tilemap_16x16.png')
    convert_18_to_16_tilemap('tilemap-farmer_packed.png', 'farmer_tilemap_16x16.png')
    convert_18_to_16_tilemap('tilemap-food_packed.png', 'food_tilemap_16x16.png')
    convert_18_to_16_tilemap('tilemap-grassland_packed.png', 'grassland_tilemap_16x16.png')
    
    # Repeat for other sheets if needed:
    # convert_18_to_16_tilemap('avoidland_18x18.png', 'avoidland_16x16.png')
    # convert_18_to_16_tilemap('characters_18x18.png', 'characters_16x16.png')
    
    print("\n--- All conversions complete! ---")
    print("These new 16x16 sheets are now ready for manual cleanup or a 'retro style' redesign in Aseprite/Piskel.")