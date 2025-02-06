#!/usr/bin/env python3
"""
Post-process a TTF to fix:
1) Subset (Basic Latin + U+00A0).
2) Reuse space glyph for U+00A0.
3) Match head.version and name version string.
4) Drop hinting to avoid OTS "Bad glyph flag" errors.
5) Set up NameID 13 and 14 for an OFL font.
"""

import sys
from fontTools import subset
from fontTools.ttLib import TTFont
from fontbakery.constants import NameID

# OFL license data
OFL_LICENSE_DESCRIPTION = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org"
)
OFL_LICENSE_INFO_URL = "https://openfontlicense.org"

# Example version you want for both head.fontRevision and nameID=5
FONT_VERSION_STRING = "Version 32.5.0"
FONT_REVISION_FLOAT = 32.5  # head.fontRevision is a 16.16 fixed-point float

def set_license_description(ttFont, license_text):
    """Ensure NameID 13 (LICENSE DESCRIPTION) matches the provided text."""
    name_table = ttFont["name"]
    found_license = False
    for record in name_table.names:
        if record.nameID == NameID.LICENSE_DESCRIPTION:  # 13
            found_license = True
            if record.toUnicode() != license_text:
                record.string = license_text.encode(record.getEncoding())
    if not found_license:
        # Windows
        name_table.setName(license_text, NameID.LICENSE_DESCRIPTION, 3, 1, 0x409)
        # Mac
        name_table.setName(license_text, NameID.LICENSE_DESCRIPTION, 1, 0, 0)

def set_license_info_url(ttFont, license_url):
    """Ensure NameID 14 (LICENSE INFO URL) is set to the provided URL."""
    name_table = ttFont["name"]
    found_license_url = False
    for record in name_table.names:
        if record.nameID == NameID.LICENSE_INFO_URL:  # 14
            found_license_url = True
            if record.toUnicode() != license_url:
                record.string = license_url.encode(record.getEncoding())
    if not found_license_url:
        # Windows
        name_table.setName(license_url, NameID.LICENSE_INFO_URL, 3, 1, 0x409)
        # Mac
        name_table.setName(license_url, NameID.LICENSE_INFO_URL, 1, 0, 0)

def fix_nbsp_glyph(ttFont):
    """
    Reuse the same glyph for U+00A0 (no-break space) as U+0020 (space),
    if missing.
    """
    cmap_table = None
    for table in ttFont["cmap"].tables:
        if table.isUnicode():
            cmap_table = table.cmap
            break
    if not cmap_table:
        return  # No unicode cmap found

    space_glyph = cmap_table.get(0x0020)
    if not space_glyph:
        return  # No space glyph to reuse

    if 0x00A0 not in cmap_table:
        # Map U+00A0 to the same glyph as U+0020
        cmap_table[0x00A0] = space_glyph

def fix_font_version(ttFont, version_string, revision_float):
    """
    1) Sets 'head.fontRevision' to 'revision_float'.
    2) Updates nameID=5 (VERSION_STRING) to 'version_string' on major platforms.
    """
    # 1) head.fontRevision
    ttFont["head"].fontRevision = revision_float

    # 2) nameID=5
    name_table = ttFont["name"]
    for record in name_table.names:
        if record.nameID == NameID.VERSION_STRING:  # 5
            # Example final name ID 5 text is "Version 32.5.0"
            if record.toUnicode() != version_string:
                record.string = version_string.encode(record.getEncoding())

    # If you want to ensure both Windows and Mac entries exist:
    name_table.setName(version_string, NameID.VERSION_STRING, 3, 1, 0x409)  # Win
    name_table.setName(version_string, NameID.VERSION_STRING, 1, 0, 0)      # Mac

def subset_basic_latin_plus_nbsp(input_path, output_path):
    """
    1) Subset the font to Basic Latin (U+0020–U+007E) plus U+00A0.
    2) Reuse space glyph for U+00A0.
    3) Drop hinting to avoid OTS "Bad glyph flag" errors.
    4) Fix NameID 13, 14, and version mismatch.
    """
    # Basic Latin range plus U+00A0:
    codepoints = list(range(0x0020, 0x007F))
    codepoints.append(0x00A0)

    # Set up subset options
    options = subset.Options()
    # If hinting data is causing OTS errors, remove it by setting hinting=False:
    options.hinting = False
    # Other subset options:
    options.desubroutinize = True
    options.notdef_outline = True
    options.recalc_bounds = True
    options.recalc_timestamp = True
    # This can help remove certain tables
    options.drop_tables = ["DSIG"]
    # We only keep the codepoints we care about
    options.unicodes = codepoints

    # Load font
    font = subset.load_font(input_path, options)

    # Subset
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)

    # 1) Fix version mismatch
    fix_font_version(font, FONT_VERSION_STRING, FONT_REVISION_FLOAT)

    # 2) Fix licensing name IDs
    set_license_description(font, OFL_LICENSE_DESCRIPTION)
    set_license_info_url(font, OFL_LICENSE_INFO_URL)

    # 3) Reuse space glyph for U+00A0
    fix_nbsp_glyph(font)

    # Save
    subset.save_font(font, output_path, options)
    print(f"Post-processed font saved to: {output_path}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.ttf> <output.ttf>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    subset_basic_latin_plus_nbsp(input_path, output_path)

if __name__ == "__main__":
    main()
