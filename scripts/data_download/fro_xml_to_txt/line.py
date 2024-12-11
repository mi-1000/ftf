import xml.etree.ElementTree as ET
import os
import shutil

def linefiles(file_name):
    """
    Process XML content to extract text from <lb> elements with proper formatting.
    """
    base_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/'
    end_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/'
    
    xml_file = base_path + file_name + ".xml"

    try:
        # Parse the XML content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Debug: Print XML structure
        # print("XML Structure:")
        # print(ET.tostring(root, encoding='unicode'))

        # Extract namespace from the root tag
        namespace = root.tag.split('}')[0].strip('{')
        ns = {'ns': namespace} if namespace else {}

        # Initialize an empty list to store lines
        lines = []


        # Iterate over <ab> elements with type="gv"
        for ab in root.findall('.//ns:ab[@type="gv"]', ns):
            current_line = []

            # Process each child element within <ab>
            for elem in ab:
                if elem.tag.endswith('lb'):  # Handle line break tags
                    # Append the current line to the output if not empty
                    if current_line:
                        lines.append(" ".join(current_line).strip())
                        current_line = []  # Reset for the next line
                # Handle text content and inline elements
                if elem.text:
                    current_line.append(elem.text.strip())
                if elem.tail:
                    current_line.append(elem.tail.strip())

            # Append the last line in the current <ab> if not empty
            if current_line:
                lines.append(" ".join(current_line).strip())


        # Join lines with a newline character
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

        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")


def process_folder(folder_path):
    """
    Process all XML files in a folder.   
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xml'):
            linefiles(f"{os.path.splitext(file_name)[0]}")

# Specify the input folder containing XML files and the output folder for TXT files
input_folder = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/'

process_folder(input_folder)