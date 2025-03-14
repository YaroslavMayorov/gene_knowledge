# Gene Knowledge Base Web Service

## Table of Contents

1. [Overview](#overview)  
2. [Project structure](#project-structure)
3. [Setup and Installation](#setup-and-installation)
4. [Usage](#usage)
5. [FAQ](#faq)
6. [Contacts](#contacts)

---

## Project Structure

```bash
.
├── assets
│   └── style.css               # CSS file for styling
├── data
│   └── NIHMS1635539-supplement-1635539_Sup_tab_4.xlsx  
│       # Main Excel file containing:
│       # - "S4B limma results" sheet (for volcano plot data)
│       # - "S4A values" sheet (for boxplot data)
├── main.py                     # Main Flask + Dash application entry point
├── requirements.txt            # Python dependencies for the project
└── README.md
```

---

## Setup and Installation

1. Clone the repository:
```bash
git clone git@github.com:YaroslavMayorov/gene_knowledge.git
cd gene_knowledge
```

2. Create a virtual environment:
```bash
python3.10 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

1. Launch the web service:
```bash
python main.py
```

2. Open a browser:

Go to the address that is displayed in the console, usually this **http://127.0.0.1:8050** .

3. Interact with the volcano plot:

Hover over the pointx to see information about the gene's symbol, p-value and fold change. Use sliders to move the threshold lines to highlight significant points.

4. Click on the point to see the boxplot:

The canvas will appear, which show comparison between protein concentraction in young and old samples for selected gene. 

5. Viewing medical publication with MyGene.info:

When you select a gene, you will see a link and the pubmed id of scientific articles on this gene.
