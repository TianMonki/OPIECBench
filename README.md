# Benchmarking Synonymy and Homonymy in Open Knowledge Base Canonicalization


This repository contains two OPIEC-derived benchmarks and a two-stage canonicalization framework.

## Repository structure

```text
.
├── code_main/      # Two-stage canonicalization model
├── code_dataset/   # OPIEC benchmark construction
├── data/           # Final benchmark data and entity-linking evidence
├── init_dict/      # Pretrained word vectors
├── plm/            # Local pretrained language model
├── requirements.txt
```

Generated files are written to `file/` and `output/` and excluded from version control.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader punkt
```

## Data

Place the final benchmarks and entity-linking evidence under `data/` as described in [`data/README.md`](data/README.md).
```

Benchmark construction

Prepare the OPIEC-Linked AVRO corpus and the following files:

```text
OPIEC-master/avroschema/TripleLinked.avsc
OPIEC-Linked/OPIEC-Linked-triples/part-r-*.avro
ent_link_desc/ent_link_dict
ent_link_desc/ent_link_des
```
Run the construction pipeline from `code_dataset/`:
```

Experiment data

```text
data/
├── name_ambi/OPIEC_name_ambi_triples https://drive.google.com/file/d/1eOmLIsjVvkAK3tJUXOlQIf8IQDHY0cCA/view?usp=drive_link
├── ent_multi/OPIEC_ent_multi_triples https://drive.google.com/file/d/11BDs5YT19q32nEFIPKtUbKtRVRQ-SwW-/view?usp=drive_link
└── ent_link/
    ├── name_ambi_ent_link
    └── ent_multi_ent_link
```
Intermediate files are written to `file/`; final datasets are written to `data/`.


## Environment

Computational platform: PyTorch 1.4.0, NVIDIA Geforce RTX 3090 (GPU), Inter i9-10900X (CPU), CUDA Toolkit 10.0


## Running the model

Run experiments from `code_main/`:

```bash
cd code_main
python main.py -data name_ambi --reset
python main.py -data ent_multi --reset
```

The default HAC distance threshold is `0.5`, and the high-confidence filtering ratio is `0.1`.
