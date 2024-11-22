import os
import re

def generate_metadata_item(filename: str, language: str = "latin") -> str:
    """Generate XML item string for a given filename."""
    # Extracting a numeric part from the filename for the link
    match = re.search(r'(\d+)', filename)
    if match:
        number = match.group(1)
        return f'<item link="latin.packhum.org/author/texts\\{number}" language="{language}" filename="data/raw/data_latin/texts\\{filename}" date="" place="" />'
    else:
        print(f"Skipping file '{filename}' as it does not contain a numeric part.")
        return None

def add_to_metadata(file_path: str, text_dir: str = "texts"):
    """Add metadata items to the XML file from the specified text directory."""
    metadata_file = file_path
    existing_items = set()

    # Read existing items from the metadata file to avoid duplicates
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            for line in f:
                if '<item ' in line:
                    existing_items.add(line.strip())

    # Collect all .txt files in the specified directory
    for root, dirs, files in os.walk(text_dir):
        for file in files:
            if file.endswith('.txt'):
                item = generate_metadata_item(file)
                if item and item not in existing_items:
                    existing_items.add(item)

    # Write all unique items back to the metadata file
    with open(metadata_file, "w", encoding="utf-8") as f:
        for item in existing_items:
            f.write(item + "\n")

if __name__ == "__main__":
    metadata_file_path = "metadata_packhum.xml"
    add_to_metadata(metadata_file_path)
    print(f"Metadata added to {metadata_file_path}.")
