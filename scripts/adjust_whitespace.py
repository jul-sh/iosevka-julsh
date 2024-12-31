import fontforge
import os
import sys

# Get the folder from command-line arguments
if len(sys.argv) < 2:
    print("Usage: python3 adjust_whitespace.py <folder>")
    sys.exit(1)

input_folder = sys.argv[1]
output_folder = os.path.join(input_folder, "output")

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process all .ttf files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".ttf"):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)

        print(f"Processing {file_name}...")

        # Open the font file
        try:
            font = fontforge.open(input_path)
        except Exception as e:
            print(f"Error opening {input_path}: {e}")
            continue


        # Adjust the width of the whitespace character (Unicode 0x20)
        if 0x20 in font:
            glyph = font[0x20]
            original_width = glyph.width
            new_width = original_width * 0.85  # Equivalent to CSS word-spacing: -0.15ch
            glyph.width = new_width

            # Adjust kerning for punctuation that may affect word spacing
            punctuation = [0x2E, 0x2C, 0x3B, 0x3A, 0x21, 0x3F]  # Period, comma, semicolon, colon, exclamation, question mark
            for punct in punctuation:
                if punct in font and font[punct].isWorthOutputting():
                    for glyph in font:
                        if glyph.isWorthOutputting():
                            font.addLookup("kern_punct", "gpos_pair", (), (("kern", (("DFLT", ("dflt")),)),))
                            font.addLookupSubtable("kern_punct", "kern_punct_subtable")
                            font[punct].addPosSub("kern_punct_subtable", glyph.glyphname, 0, 0, int(original_width * -0.15), 0)

            # Save the modified font
            try:
                font.generate(output_path)
                print(f"Saved font to {output_path}")
            except Exception as e:
                print(f"Error saving {output_path}: {e}")
        else:
            print(f"Skipping {file_name}: Space character (0x20) not found.")

        if font:
            font.close()


print("Processing complete. All fonts have been processed.")
