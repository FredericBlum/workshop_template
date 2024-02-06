from lexibank_northernperu import Dataset
from lingpy import Alignments, Wordlist, LexStat


cols = ['concept_id', 'concept_name', 'language_id', 'language_name', 'value',
        'form', 'segments', 'glottocode', 'concept_concepticon_id',
        'comment']

# Load dataset
DS = Dataset()
wl = Wordlist.from_cldf(
    DS.cldf_dir.joinpath('cldf-metadata.json'),
    columns=cols,
    namespace=(
        ("language_id", "doculect"),
        ("concept_name", "concept"),
        ("segments", "tokens")
    ))

for idx in wl:
    wl[idx, "tokens"] = [x for x in wl[idx, "tokens"] if x != "+"]

# Run AutoCogid
lex = LexStat(wl)
lex.get_scorer(runs=10000)
lex.cluster(threshold=0.55, method="lexstat", cluster_method="infomap", ref="cogid")

# Align data
alms = Alignments(lex, ref="cogid")
alms.align()
alms.add_entries("morphemes", "tokens", lambda x: "")
alms.add_entries("note", "comment", lambda x: x if x else "")

# Output data
D = {0: ["doculect", "value", "form","concept",
    "tokens", "cogid", "morphemes", "alignment", "note"]}
for idx in alms:
    D[idx] = [alms[idx, h] for h in D[0]]

# Create sqlite
lex.output('tsv', filename="ipc_edictor", ignore="all")
