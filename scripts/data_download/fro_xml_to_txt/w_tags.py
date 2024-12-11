import xml.etree.ElementTree as ET
import os
import shutil
from lxml import etree

def xml_id_files(file_name):
    """
    Process XML content to extract text from <lb> elements with proper formatting.
    """
    base_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/'
    end_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/'
    
    xml_file = base_path + file_name + ".xml"

    # try:
    # Parse the XML content
    tree = etree.parse(xml_file)
    root = tree.getroot()

    # Debug: Print XML structure
    # print("XML Structure:")
    # print(ET.tostring(root, encoding='unicode'))

    # Extract namespace from the root tag
    namespace = root.tag.split('}')[0].strip('{')
    ns = {'ns': namespace} if namespace else {}

    # Initialize variables for processed lines
    lines = []
    current_line = []

# Find all <w> elements
    for w in root.findall('.//ns:w', ns):
        # Initialize the word with the text of <w> (if present)
        word = w.text.strip() if w.text else ''

        # Handle <ex> tags inside <w>
        for ex in w.findall('.//ns:ex', ns):
            if ex.text:
                word += ex.text.strip()  # Append <ex> content
            if ex.tail:
                word += ex.tail.strip()  # Append any tail content after <ex>

        # Check if the word ends with punctuation requiring a new line
        if word == ('.' or '!' or '?'):
            current_line.append(word)
            lines.append("".join(current_line).strip())  # Complete the current line
            current_line = []  # Start a new line
        else:
            # If the word ends with "'", don't add a space before the next word
            if word.endswith("'"):
                current_line.append(word)
            else:
                current_line.append(word + " ")

    # Add the processed line to the output
    if current_line:
        lines.append(" ".join(current_line).strip())

    # Join the lines with a newline character
    formatted_text = "\n".join(lines)

    if formatted_text.strip() != "":
        done_file = end_path + file_name + ".txt"
        # print(done_file)

        shutil.move(xml_file, end_path + file_name + ".xml")
        print(f"Moved: {file_name} to {end_path}")

        # Write the processed text to the output file
        with open(done_file, 'w', encoding='utf-8') as f:
            f.write(formatted_text)

        print(f"Processed: {file_name}")



def process_folder(folder_path):
    """
    Process all XML files in a folder.   
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xml'):
            xml_id_files(f"{os.path.splitext(file_name)[0]}")

# Specify the input folder containing XML files and the output folder for TXT files
input_folder = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/'

process_folder(input_folder)
# xml_id_files("belinc")
