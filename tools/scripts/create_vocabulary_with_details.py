from googletrans import Translator
import pandas as pd

csv_path = r"PATH_TO_FILE"

source_lang_name = "angličtina"
dest_lang_name = "čeština"
col_names = ["source_lang", "dest_lang", "source", "dest"]

df = pd.read_csv(csv_path, header=None, names=col_names)
df["en"] = df["cz"] = df["synonyms"] = df["definitions"] = ""

translator = Translator()

for df_i, source_lang, dest_lang, source, dest, *_ in df.itertuples():
    en = df["en"][df_i] = source if source_lang == source_lang_name else dest
    df["cz"][df_i] = dest if source_lang == source_lang_name else source

translations = translator.translate(list(df["en"]), dest="cs")

synonyms = []
definitions = []

for t in translations:
    if t.extra_data["synonyms"]:
        synonyms_types = [i[1] for i in t.extra_data["synonyms"]]
        for i in synonyms_types:
            synonyms_lists = [j[0] for j in i]
        synonyms_types_appended = [i[0] for i in synonyms_lists]
        synonyms.append(", ".join(synonyms_types_appended))

    else:
        synonyms.append("")

    if t.extra_data["definitions"]:
        definitions_types = [i[0] for i in t.extra_data["definitions"]]
        definitions_content = [i[1] for i in t.extra_data["definitions"]]
        definitions_content = [
            f"{i[0][0]} --- {i[0][2]}" if len(i[0]) > 2 else i[0][0] for i in definitions_content
        ]
        definitions.append("\n".join([f"{a}:  {b}" for a, b in zip(definitions_types, definitions_content)]))
    else:
        definitions.append("")

df["synonyms"] = synonyms
df["definitions"] = definitions

df.drop(col_names, axis=1, inplace=True)

df.to_excel("vocabulary.xlsx", header=False)
