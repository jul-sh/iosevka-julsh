import fontforge
import os
import sys

# Get the folders from command-line arguments
if len(sys.argv) < 3:
    print("Usage: python3 webfont.py <input_folder> <webfont_output_folder>")
    sys.exit(1)

input_folder = sys.argv[1]
webfont_output_folder = sys.argv[2]

# Create the webfont output directory if it doesn't exist
os.makedirs(webfont_output_folder, exist_ok=True)

# Basic Latin charset (Unicode range 0x0000 to 0x007F)
basic_latin = range(0x0000, 0x0080)

# Process all .ttf files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".ttf"):
        input_path = os.path.join(input_folder, file_name)
        webfont_path = os.path.join(webfont_output_folder, file_name.replace('.ttf', '.woff2'))

        print(f"Processing {file_name}...")

        # Open the font file
        font = fontforge.open(input_path)

        # Create a subset with only Basic Latin characters for the webfont
        font.selection.none()
        for char in basic_latin:
            font.selection.select(char)
        font.selection.invert()
        font.clear()

        # Generate WOFF2 webfont
        font.generate(webfont_path, flags=("woff2",))
        font.close()
        print(f"Saved WOFF2 webfont to {webfont_path}")

print("Processing complete. All webfonts have been generated.")
