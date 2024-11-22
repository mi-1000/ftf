import xml.etree.cElementTree as ET

import os
import statistics

def get_metadata_fabliaux():
    metadata = ""
    
    path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TEI")
    if not os.path.exists(path):
        print("Path not found.")
        return
    for abs in os.listdir(path):
        file = os.path.join(path, abs)
        tree = ET.parse(file)
        root = tree.getroot()
        
        try:
            namespaces = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            origin_elements = root.findall('.//ns:origin', namespaces) if namespaces else root.findall('.//origin')
        except Exception as e:
            print(f'\tOrigin not found for {abs}: "{e}".')
        if not origin_elements:
            print("Error while iterating over origin elements.")
            return
        years = []
        try:
            for origin in origin_elements:
                not_before = int(origin.get('notBefore').split('-')[0])
                not_after = int(origin.get('notAfter').split('-')[0])
                year = round((not_before + not_after) / 2)
                years.append(year)
            avg_year = str(round(statistics.mean(years)))
        except Exception:
            avg_year = ""
        metadata += f'<item link="https://gitlab.huma-num.fr/fabliaux/public/fabliaux-textes-diffusion/-/blob/main/TEI-TXM/{abs}" language="old-french" filename="data/raw/data_old_french/{abs}" date="{avg_year}" place="" />\n'
    return metadata


if __name__ == "__main__":
    metadata = get_metadata_fabliaux()
    print(metadata)