import os
import fontforge
import sys

if len(sys.argv) < 2:
    print("Usage: python3 adjust_whitespace.py <folder>")
    sys.exit(1)

input_folder = sys.argv[1]
output_folder = os.path.join(input_folder, "output")
os.makedirs(output_folder, exist_ok=True)

# Walk the directory structure recursively
for root, _, files in os.walk(input_folder):
    for file_name in files:
        if file_name.endswith(".ttf"):
            input_path = os.path.join(root, file_name)
            # Place adjusted fonts at the top-level output folder
            output_path = os.path.join(output_folder, file_name)
            print(f"Processing {input_path}...")

            font = fontforge.open(input_path)

            # Adjust whitespace width
            space_glyph = font[0x20]
            original_width = space_glyph.width
            space_glyph.width = original_width * 0.85  # -0.15ch

            # Create a kerning lookup once
            font.addLookup("kern_punct", "gpos_pair", None, (("kern", (("DFLT", ("dflt")),)),))
            font.addLookupSubtable("kern_punct", "kern_punct_subtable")

            # Kerning adjustments
            punctuation = [0x2E, 0x2C, 0x3B, 0x3A, 0x21, 0x3F]
            for punct in punctuation:
                if punct in font:
                    for g in font.glyphs():
                        if g.isWorthOutputting():
                            font[punct].addPosSub("kern_punct_subtable", g.glyphname, 0, 0, int(original_width * -0.15), 0)

            # Generate and close
            font.generate(output_path)
            font.close()
            print(f"Saved font to {output_path}")

print("Processing complete.")
