# 🧬 Automated Gene Sequence QC & Profiler Pipeline

A Streamlit application for interactive multi-FASTA quality control and sequence profiling.

## Features

- Multi-line multi-FASTA parsing
- Configurable minimum sequence length
- Optional ATG start-codon filtering
- GC% and AT% calculation
- DNA → RNA transcription
- Terminal stop-codon detection
- Passed-sequence results table
- GC/AT visualization
- CSV export
- Text summary report
- Complete ZIP export

## Project structure

```text
gene_sequence_qc_streamlit/
├── app.py
├── requirements.txt
├── README.md
└── backend/
    ├── __init__.py
    └── pipeline.py
```

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit deployment

Push the project folder to GitHub and deploy `app.py` as the main file.

No database or secrets are required.
