# BGH Gender Counterfactuals

Legal document analysis and augmentation with LLMs for the BGH Civil Appeals dataset with gender counterfactuals.

## Overview

This project provides a complete pipeline for:
1. **Scraping** legal documents from online sources
2. **Labeling** documents with metadata and classifications
3. **Augmentation** of documents using LLM-generated variations
4. **Dataset creation** with train/test splits for machine learning

The pipeline processes German Federal Court of Justice (BGH) civil appeals cases and creates gender counterfactual versions to study bias in legal decision-making.

## Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager

### Dependencies

Install the required dependencies using the setup.py file:

```bash
pip install -e .
python -m spacy download de_core_news_lg
```

This will install all required packages including:
- OpenAI API client (openai==1.95.1)
- HTTP client (httpx==0.28.1)
- Data processing (pandas==2.3.1, scikit-learn==1.7.0)
- PDF processing (pymupdf==1.26.3, lxml==6.0.0)
- ML datasets (datasets==4.0.0)
- Jupyter notebook (jupyter==1.1.1)
- Natural language processing (spacy==3.8.7)
- Utilities (tqdm, pydantic, tenacity, python-dotenv)

## Usage

### Running the Complete Pipeline

Execute the main notebook to run the full data processing pipeline:

```bash
jupyter notebook notebooks/main.ipynb
```

The notebook contains four main sections:

#### 1. Scraping
- Scrapes document IDs from legal databases
- Downloads legal documents
- Extracts text from PDF files
- Parses documents into structured format

#### 2. Labeling
- Applies automated labeling to documents
- Extracts case metadata and classifications

#### 3. Augmentation
- Creates gender counterfactual versions of documents
- Uses LLMs to generate alternative text while preserving legal meaning

#### 4. Train and Test Sets
- Splits data into balanced train/test sets
- Creates HuggingFace dataset format
- Uploads dataset to HuggingFace Hub

### Bias Analysis

To analyze gender bias in legal decision predictions, run the bias analysis notebook:

```bash
jupyter notebook notebooks/bias_analysis.ipynb
```

This notebook demonstrates:
- **Baseline Model Training**: Creates a text classification model using TF-IDF and Naive Bayes
- **Bias Detection**: Tests for gender bias by comparing predictions on original vs. gender-swapped case facts
- **Statistical Analysis**: Uses t-tests to measure bias significance
- **Bias Mitigation**: Shows how data augmentation with counterfactuals can reduce bias
- **Performance Evaluation**: Compares model accuracy before and after bias mitigation

The analysis reveals how gender-related language in legal cases can influence automated decision predictions and provides a methodology for detecting and reducing such biases.

### Configuration

The project uses environment variables for configuration. Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_TOKEN=your_huggingface_token
```

## Project Structure

```
bgh-gender-counterfactuals/
├── src/                    # Source code modules
│   ├── common/            # Configuration and utilities
│   ├── scraping/          # Document scraping functionality
│   ├── labeling/          # Document labeling
│   └── augmentation/      # LLM-based augmentation
├── notebooks/             # Jupyter notebooks
│   ├── main.ipynb        # Main pipeline notebook
│   └── bias_analysis.ipynb # Gender bias analysis example
├── data/                  # Generated datasets
├── prompt_templates/      # LLM prompt templates
├── cache/                 # Cached API responses
└── requirements.txt       # Python dependencies
```

## Output

The pipeline generates several datasets:
- `documents.jsonl` - Raw scraped documents
- `documents_parsed.jsonl` - Parsed and structured documents  
- `documents_labeled.jsonl` - Documents with labels and metadata
- `documents_augmented.jsonl` - Final dataset with gender counterfactuals

The final dataset is available at https://huggingface.co/datasets/nlietzow/BGH-CivAppeals-GenderCF.

## License

MIT License