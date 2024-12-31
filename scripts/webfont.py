import os
import argparse
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.ttLib.sfnt import WOFF2FlavorData

def convert_ttf_to_woff2(input_folder, output_folder):
    """
    Converts all TTF files in a folder to WOFF2 format with the Basic Latin charset.

    :param input_folder: Path to the folder containing TTF files.
    :param output_folder: Path to the folder where WOFF2 files will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Define Basic Latin Unicode range (U+0000 to U+007F)
    basic_latin_range = [(0x0000, 0x007F)]

    # Process each TTF file in the folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".ttf"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + ".woff2")

            try:
                # Load the font
                font = TTFont(input_path)

                # Subset the font to Basic Latin charset
                subsetter = Subsetter()
                options = Options()
                options.unicodes = basic_latin_range
                subsetter.populate(unicodes=options.unicodes)
                subsetter.subset(font)

                # Save as WOFF2
                with open(output_path, "wb") as output_file:
                    font.flavor = "woff2"
                    font.save(output_file)

                print(f"Converted {file_name} to WOFF2 format.")
            except Exception as e:
                print(f"Failed to convert {file_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert TTF files to WOFF2 format with Basic Latin charset.")
    parser.add_argument("input_folder", help="Path to the folder containing TTF files.")
    parser.add_argument("output_folder", help="Path to the folder where WOFF2 files will be saved.")

    args = parser.parse_args()

    convert_ttf_to_woff2(args.input_folder, args.output_folder)
