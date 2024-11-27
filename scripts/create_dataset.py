import os
import xml.etree.ElementTree as ET
import pandas as pd

def parse_source_xml(xml_file):
    """
    Parse the source XML file to extract information about the items
    where "bilingual" is true.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = []
    for item in root.findall("item"):
        bilingual = item.get("bilingual")
        # Filter items where bilingual is "true"
        if bilingual and bilingual.lower() == "true":
            link = item.get("link")
            language = item.get("language")
            filename = item.get("filename")
            data.append({"link": link, "language": language, "bilingual": bilingual, "filename": filename})
    
    return data

def load_text_file(file_path):
    """
    Load the content of a text file.
    """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        print(f"File not found: {file_path}")
        return None

def create_dataset(xml_file, output_dir):
    """
    Create a dataset from the source XML and the associated text files.
    """
    items = parse_source_xml(xml_file)

    # Organize data by language
    language_data = {}
    for item in items:
        lang = item["language"]
        content = load_text_file(item["filename"])
        if content:
            if lang not in language_data:
                language_data[lang] = []
            language_data[lang].append(content)

    # Save datasets for each language
    os.makedirs(output_dir, exist_ok=True)
    for lang, texts in language_data.items():
        output_file = os.path.join(output_dir, f"{lang}_dataset.txt")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(texts))
        print(f"Dataset for {lang} saved to {output_file}")

# Example usage
if __name__ == "__main__":
    source_xml = "sources.xml"  # Replace with your actual XML file path
    output_directory = "data/datasets"  # Directory to save the dataset
    create_dataset(source_xml, output_directory)


