# CS6200 Final Project
by Hajera Siddiqui and Michael Aldoroty
Decemeber 13, 2023

## Overview
The task achieved by this project was an information retrieval system for medical documents. Essentially, users should use this system to query their symptoms of a currently unknown disease and the model should help bridge the information gap to give an idea of what disease the user may be suffering from. The documents retrieved will have information for treatment, causes, and more. To summarize, the search engine aggregates data from documents across many healthcare websites, creating a search engine with more information than just a website like WebMD. 
 

## Packages Used
- Counter
- BeautifulSoup

## Important Files
- Final_Model.py
    - This file contains the final iteration of the retreival model for the project.
- Final_Model_Testing.ipynb
    - This notebook contains testing scripts with evaluating the final model with web scrapped data.
- web_crawler_data_set_up.py
    - This file sets up the web crawler implementation that will retrieve the expanded dataset.

All of the other files were for testing purposes. 

## Dataset
Using BeautifulSoup, we scraped multiple different medical information websites such as WebMD. A list of the websites we scraped can be found in this repo.

## How to Run
Please see the notebooks in this repo to see a demo of how the models are implemented and how they can be used.
