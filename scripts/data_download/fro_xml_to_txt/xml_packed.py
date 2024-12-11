import xml.etree.ElementTree as ET
import os
import shutil
from lxml import etree

def xml_id_files(file_name):
    """
    Extract words from <ns1:wf> elements in the XML file, ensuring proper spacing,
    and new lines after ".", "!", or "?".
    """

    base_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/'
    end_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/'
    
    xml_file = base_path + file_name + ".xml"

    # Parse the XML file
    tree = etree.parse(xml_file)
    root = tree.getroot()

    # Debug: Print XML structure
    # print("XML Structure:")
    # print(ET.tostring(root, encoding='unicode'))

    # Define namespaces
    namespaces = {
        'x': 'http://www.atilf.fr/allegro',  # For <x:wf>
        'tei': 'http://www.tei-c.org/ns/1.0'  # For <l> or other TEI elements
    }

    # Initialize variables for processed lines
    lines = []
    current_line = []

    # Find all <x:wf> elements
    wf_elements = root.findall('.//x:wf', namespaces)
    print(f"Found {len(wf_elements)} <x:wf> elements")  # Debug: Verify element count

    for wf in wf_elements:
        word = wf.get('word', '').strip()  # Get the 'word' attribute

        # Check if the word ends with punctuation requiring a new line
        if word in ('.', '!', '?'):
            current_line.append(word)
            lines.append("".join(current_line).strip())  # Complete the current line
            current_line = []  # Start a new line
        else:
            # If the word ends with "'", don't add a space before the next word
            if word.endswith("'"):
                current_line.append(word)
            else:
                current_line.append(word + " ")

    # Add the last line if it's not empty
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
    else:
        print(lines)



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
# xml_id_files("Gormont_et_Isembart")
