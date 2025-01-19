#!/usr/bin/env python3
import fontforge
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python3 adjust_whitespace.py <folder>")
    sys.exit(1)

input_folder = sys.argv[1]

for file_name in os.listdir(input_folder):
    if file_name.endswith(".ttf"):
        file_path = os.path.join(input_folder, file_name)
        print(f"Processing {file_name}...")

        font = fontforge.open(file_path)

        # Adjust whitespace width
        space_glyph = font[0x20]
        original_width = space_glyph.width
        space_glyph.width = original_width * 0.85  # -0.15ch

        # Create a kerning lookup
        font.addLookup("kern_punct", "gpos_pair", None, (("kern", (("DFLT", ("dflt")),)),))
        font.addLookupSubtable("kern_punct", "kern_punct_subtable")

        # Kerning adjustments
        punctuation = [0x2E, 0x2C, 0x3B, 0x3A, 0x21, 0x3F]
        for punct in punctuation:
            if punct in font:
                for g in font.glyphs():
                    if g.isWorthOutputting():
                        font[punct].addPosSub("kern_punct_subtable",
                                              g.glyphname,
                                              0, 0,
                                              int(original_width * -0.15), 0)

        # Overwrite the file in place with adjusted metrics
        font.generate(file_path)
        font.close()
        print(f"Overwrote font in place at {file_path}")

print("Processing complete.")
