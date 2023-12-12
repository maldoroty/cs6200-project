import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

def load_json(json_file):
    """
    Load JSON data from a file.

    Parameters:
    - json_file (str): The path to the JSON file.

    Returns:
    - dict: The loaded JSON data.
    """
    with open(json_file) as file:
        return json.load(file)
    
def write_json(data, filename):
    """
    Write JSON data to a file.

    Parameters:
    - data (dict): The JSON data to be written.
    - filename (str): The path to the output JSON file.
    """
    json_data = json.dumps(data, indent=2)
    with open(filename, "w") as json_file:
        json_file.write(json_data)
    
def clean_website(website_text):
    """
    Clean and preprocess website text by removing extra spaces, converting to lowercase, 
        and stripping whitespaces.

    Parameters:
    - website_text (str): The raw text extracted from a website.

    Returns:
    - str: Website text.
    """
    website_text = re.sub(r"\s+", " ", website_text)
    website_text = website_text.lower().strip()
    return website_text

def extract_text_from_website(url):
    """
    Get content from a given website URL.

    Parameters:
    - url (str): The URL of the website.

    Returns:
    - str: Text content from the website.
    """
    url = r'{}'.format(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    website_text = soup.get_text()
    website_text = clean_website(website_text)
    return website_text

def scrape_websites(websites, filename):
    """
    Scrape and get text from a list of websites and save to a JSON file.

    Parameters:
    - websites (dict): A dictionary where keys are categories and values are lists of website URLs.
    - filename (str): The path to the output JSON file.
    """
    doc_data = {"documents": []}
    for category, urls in websites.items():
        for i, url in enumerate(urls, 1):
            doc_id = f"{category[:3]}{i}"
            text_data = extract_text_from_website(url)
            doc_data["documents"].append({"doc_id": doc_id, "text": text_data})

    write_json(doc_data, filename)

def annotate_data(queries, doc_data, filename):
    """
    Annotate the data based on queries and document data, and save to a JSON file.

    Parameters:
    - queries (list): A list of tuples where each tuple contains a query and a corresponding disease.
    - doc_data (dict): The document data containing text and document IDs.
    - filename (str): The path to the output JSON file.
    """
    annotated_data = {}
    for query, disease in queries:
        annotated_data[query] = {}
        disease_prefix = disease[:3]
        
        for document in doc_data["documents"]:
            doc_id = document["doc_id"]
            if doc_id[:3] == disease_prefix:
                score = 1
            else: 
                score = 0
            annotated_data[query][doc_id] = score

    write_json(annotated_data, filename)

def web_crawler(seed_urls, disease, max_pages=25):
    """
    Web crawling to collect URLs related to a specific disease.

    Parameters:
    - seed_urls (list): A list of URLs to start.
    - disease (str): The target disease.
    - max_pages (int): The maximum number of pages to crawl.

    Returns:
    - list: A list of collected URLs related to the specified disease.
    """
    visited = set()
    websites = seed_urls.copy()
    consecutive_same_length = 0

    while seed_urls and len(websites) < max_pages:
        url = seed_urls.pop(0)
        if not url.lower().startswith(('http://', 'https://')):
            continue
        text = requests.get(url).text
        soup = BeautifulSoup(text, 'html.parser')
        links = soup.find_all('a')
        current_length = len(websites)
        for link in links:
            href = link.get('href')
            if href:
                href = urljoin(url, href)
                if not href.lower().startswith(('http://', 'https://')):
                    continue
                if href not in visited:
                    seed_urls.append(href)
                    visited.add(href)
                if disease in href.lower() and href not in websites:
                    websites.append(href)

        if current_length == len(websites):
            consecutive_same_length += 1
        else:
            consecutive_same_length = 0
        if consecutive_same_length == 10:
            break         
    return websites

def update_websites_json(disease, new_links, websites, filename):
    """
    Update the list of websites related to a specific disease in a JSON file.

    Parameters:
    - disease (str): The target disease being updated.
    - new_links (list): A list of new links to be added.
    - websites (dict): The dictionary containing disease-wise lists of websites.
    - filename (str): The path to the output JSON file.
    """
    if disease in websites:
        existing_links = set(websites[disease])
        new_links_set = set(new_links)
        websites[disease] = list(existing_links.union(new_links_set))
    else:
        websites[disease] = new_links

    write_json(websites, filename)
