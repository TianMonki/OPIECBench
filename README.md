# OPIEC-Poly / OPIEC-Syno

Implementation of *Benchmarking Synonymy and Polysemy in Open Knowledge Base Canonicalization*.

This repository provides two OPIEC-derived benchmarks and a two-stage canonicalization framework:

1. **Precision-oriented polysemy resolution** uses contextual BERT representations, hierarchical agglomerative clustering, and entity-linking supervision to construct high-purity proto-entities.
2. **Recall-oriented synonymy consolidation** combines semantic and TransE-based factual views to merge synonymous proto-entities.

## Repository structure

```text
.
├── code_main/      # Two-stage canonicalization model
├── code_dataset/   # OPIEC benchmark construction
├── data/           # Final benchmark data and entity-linking evidence
├── init_dict/      # Pretrained word vectors
├── plm/            # Local pretrained language model
├── requirements.txt
└── todolist.md
```

Generated caches, embeddings, checkpoints, and experiment outputs are written to `file/` and `output/`. They are excluded from version control.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader punkt
```

## Data

Place the final benchmarks and entity-linking evidence under `data/` as described in [`data/README.md`](data/README.md).

The model also requires:

```text
init_dict/crawl-300d-2M.vec
plm/unsup-simcse-bert-base-uncased/
```

## Benchmark construction

Download the OPIEC-Linked AVRO corpus and prepare:

```text
OPIEC-master/avroschema/TripleLinked.avsc
OPIEC-Linked/OPIEC-Linked-triples/part-r-*.avro
ent_link_desc/ent_link_dict
ent_link_desc/ent_link_des
```

Run the construction pipeline from `code_dataset/`:

```bash
cd code_dataset
python 1_first_filtration.py
python 2_filtration_redirect_rm.py

python 3_name_ambi.py
python 4_final_dataset.py name_ambi

python 3_ent_multi.py
python 4_final_dataset.py ent_multi
```

Intermediate construction artifacts are written to `file/`. The final benchmark files are written to `data/`.

## Running the model

Run experiments from `code_main/`:

```bash
cd code_main
python main.py -data name_ambi --reset
python main.py -data ent_multi --reset
```

The entry point calls `embedding_final.Embeddings.fit()` to run Stage 1 followed by Stage 2. The default HAC distance threshold is `0.5`, and the high-confidence filtering ratio is `0.1`.

See [`todolist.md`](todolist.md) for pending release and reproducibility work.
