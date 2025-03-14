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

