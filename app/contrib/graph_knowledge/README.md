# Clinical-Trials-Knowledge-Graph-Project
A streamlined Python toolkit to convert clinical trial data into an interactive knowledge graph, revealing key trends and relationships in medical research.

## Project Overview
This project aims to extract valuable insights from clinical trial data and medical documents to construct a knowledge graph that can be displayed on the web. By applying Natural Language Processing (NLP) and other analytical methods to both structured and unstructured data, the project will enable users to identify relationships and trends in healthcare research.

## Repository Structure
- `/data`: Contains raw and processed data used in the analysis.
- `/notebooks`: Jupyter notebooks for exploratory data analysis and result presentation.
- `/src`: Source code for the project, including data preprocessing, analysis, model training, and visualization scripts.
- `/tests`: Test scripts to ensure the correctness of the codebase.

### Data
The `data` directory is divided into raw and processed data. The raw data is the unaltered dump of clinical trial information, while processed data has been cleaned and structured, ready for analysis.

### Source Code
The `src` directory is organized into modules:
- `data_preprocessing`: Scripts to clean and tokenize the data.
- `analysis`: Scripts to perform NLP analysis and graph analysis.
- `models`: Scripts to build and evaluate prediction models.
- `visualization`: Scripts to generate the knowledge graph.

### Tests
Unit tests for each part of the source code are located in the `tests` directory, ensuring that each function and module operates correctly.

### Getting Started
To get started with this project, clone this repository and install the required dependencies:

bash
```
git clone https://github.com/Eng-ZeyadTarek/Clinical-Trials-Knowledge-Graph-Project
cd path/Clinical-Trials-Knowledge-Graph-Project
pip install -r requirements.txt
```
Then navigate to the src directory to run the preprocessing and analysis scripts.


### Acknowledgments
- Zeyad for data preprocessing, analysis, and model building for creating graphs.
- Howard's data team for assistance with labeling and tagging, as well as data assessment.
