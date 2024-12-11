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

    # Initialize an empty list for the output lines
    lines = []

        # Find all <l> elements
    for l in root.findall('.//ns:l', ns):
        current_line = []

        # Process child elements inside <l>
        for elem in l:
            if elem.tag.endswith('w'):  # Process <w> tags
                word = ""
                # Handle <supplied> content if present
                supplied = elem.find('.//ns:supplied', ns)
                if supplied is not None and supplied.text:
                    word += supplied.text.strip()  # Add <supplied> content

                # Add the remaining text from <w> (excluding nested tags)
                if elem.text:
                    word += elem.text.strip()

                # Check for <choice> and prioritize <orig>
                choice = elem.find('.//ns:choice', ns)
                if choice is not None:
                    orig = choice.find('.//ns:orig', ns)
                    if orig is not None and orig.text:  # Ensure <orig> exists and has non-None text
                        word += orig.text.strip()  # Add <orig> content

                # Handle <ex> content inside <w>
                for ex in elem.findall('.//ns:ex', ns):
                    if ex.text:
                        word += ex.text.strip()  # Add <ex> text
                    if ex.tail:
                        word += ex.tail.strip()  # Add <ex> tail content

                # Add the tail text of the last nested tag
                if supplied is not None and supplied.tail:
                    word += supplied.tail.strip()
                elif choice is not None and choice.tail:
                    word += choice.tail.strip()
                

                # Append the completed word to the current line
                if word:
                    current_line.append(word)

            elif elem.tag.endswith('pc'):  # Process <pc> tags
                # Similar handling for punctuation if <choice> exists
                choice = elem.find('.//ns:choice', ns)
                if choice is not None:
                    orig = choice.find('.//ns:orig', ns)
                    if orig is not None and orig.text:  # Ensure <orig> exists and has non-None text
                        current_line.append(orig.text.strip())
                elif elem.text:
                    current_line.append(elem.text.strip())  # Fallback to <pc> text

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
# xml_id_files("Auberee_Berlin-257")
