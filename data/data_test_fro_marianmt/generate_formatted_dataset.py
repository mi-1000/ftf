with open("chanson_de_roland_fr.txt", 'r', encoding="utf-8") as fr:
    with open("chanson_de_roland_fro.txt", 'r', encoding="utf-8") as fro:
        with open("fro.csv", "w", encoding="utf-8") as out:
            fr_lines = fr.readlines()
            fro_lines = fro.readlines()
            if not len(fr_lines) == len(fro_lines):
                print("Error")
                exit()
            text = ""
            for i in range(len(fr_lines)):
                text += f"\"{fr_lines[i].strip('\n ')}\"\t\"{fro_lines[i].strip('\n ')}\"\n"
            out.write(text)