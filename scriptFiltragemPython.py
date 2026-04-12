import bibtexparser
import re
import os
from glob import glob

# ===== CONFIG =====
dir_entrada = "bibtex"
dir_saida = "bibtex_saida"
os.makedirs(dir_saida, exist_ok=True)

# ===== SUA STRING (aplicada em TÍTULO + ABSTRACT) =====
grupo_A = ["develop", "program", "software engineer", "professional", "practitioner"]
grupo_B = ["accessib"]
grupo_C = [
    "challeng", "barrier", "difficult", "problem", "practice",
    "percept", "perspective", "experience", "awareness"
]

def normalize(text: str) -> str:
    return re.sub(r"[{}]", "", text or "").lower()

def contains_term_or_prefix(text: str, term: str) -> bool:
    text = normalize(text)
    term = term.lower()

    # frase (ex: "software engineer*")
    if " " in term:
        return term in text

    # prefixo tipo wildcard (ex: accessib*)
    return re.search(rf"\b{re.escape(term)}\w*", text) is not None

def match_group(text: str, terms) -> bool:
    return any(contains_term_or_prefix(text, t) for t in terms)

def string_busca_match_title(entry) -> bool:
    texto = entry.get("title", "")
    return (
        match_group(texto, grupo_A) and
        match_group(texto, grupo_B) and
        match_group(texto, grupo_C)
    )

# ===== PROCESSAMENTO =====
arqs_entrada = glob(os.path.join(dir_entrada, "*.bib"))

for arq_entrada in arqs_entrada:
    with open(arq_entrada, encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    filtered_entries = []
    removed_entries = []

    print(f"\nBibTeX analisado: {arq_entrada} - {len(bib_database.entries)} entradas")

    for entry in bib_database.entries:
        if string_busca_match_title(entry):
            filtered_entries.append(entry)
        else:
            removed_entries.append(entry)

    bib_database_filtered = bibtexparser.bibdatabase.BibDatabase()
    bib_database_filtered.entries = filtered_entries

    bib_database_removed = bibtexparser.bibdatabase.BibDatabase()
    bib_database_removed.entries = removed_entries

    base_name = os.path.basename(arq_entrada).replace(".bib", "")

    with open(os.path.join(dir_saida, f"{base_name}_filtrado.bib"), "w", encoding="utf-8") as f:
        bibtexparser.dump(bib_database_filtered, f)

    with open(os.path.join(dir_saida, f"{base_name}_removido.bib"), "w", encoding="utf-8") as f:
        bibtexparser.dump(bib_database_removed, f)

    print(f"Filtrados: {len(filtered_entries)} | Removidos: {len(removed_entries)}")
