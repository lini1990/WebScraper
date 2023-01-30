# WebScraper

## Executables
Windows
[Download here](https://github.com/lini1990/WebScraper/blob/main/executables/windows.zip)

Linux 
run from Source

## Screenshots
Todo


## Install source
pip install -r requirements.txt  
python main.py

## Input
### HTML: 
Add as many MPI-SHH MAscot Report GEnerator HTML files as you like. 
Will scrap the relevant information

The scraper expects the table inside of the HTML in the following layout:
<img src="https://github.com/lini1990/WebScraper/blob/main/screenshots/htmlTable.png" />

### Excel Sheet:

The Excel sheet should be in this style for the scraper to work.

| Speciem  | Accession  | Protein Description (GN=)  | Number of Peptides  |  Link |
|---|---|---|---|---|

## Output
| Speciem  | Accession  | Protein Description (GN=)  | Number of Peptides  |  Link | Tissue specificity  | Tissue expression cluster  | specific  | status  |
|---|---|---|---|---|---|---|---|---|
| | | | | | | |If Tissue specificity or  Tissue expression cluster contain the word "brain", it's yes else no  |0=not crawled, 1 = successfully crawled, 2= not found|

<img src="https://github.com/lini1990/WebScraper/blob/main/screenshots/output.png" />

## references
Insert DOI here
