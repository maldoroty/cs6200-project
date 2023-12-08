import requests
from bs4 import BeautifulSoup
import json
import re

def load_json(json_file):
    with open(json_file) as file:
        return json.load(file)
    
def write_json(data, filename):
    json_data = json.dumps(data, indent=2)
    with open(filename, "w") as json_file:
        json_file.write(json_data)
    
def clean_website(website_text):
    website_text = re.sub(r"\s+", " ", website_text)
    website_text = website_text.lower().strip()
    return website_text

def extract_text_from_website(url):
    url = r'{}'.format(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    website_text = soup.get_text()
    website_text = clean_website(website_text)
    return website_text

def scrape_websites(websites):
    doc_data = {"documents": []}
    for category, urls in websites.items():
        for i, url in enumerate(urls, 1):
            doc_id = f"{category[:3]}{i}"
            text_data = extract_text_from_website(url)
            doc_data["documents"].append({"doc_id": doc_id, "text": text_data})

    write_json(doc_data, "doc_data.json")

def annotate_data(queries, doc_data):
    annotate_data = []
    for i, (query, disease) in enumerate(queries):
        annotate_data.append({query: {}})
        disease = disease[:3]
        documents = doc_data["documents"]
        for document in documents:
            doc_id = document["doc_id"]
            if doc_id[:3] == disease:
                annotate_data[i][query][doc_id] = 1
            else:
                annotate_data[i][query][doc_id] = 0

    write_json(annotate_data, "annotated_data.json")

def main():
    
    websites = load_json("websites.json")
    scrape_websites(websites)
    doc_data = load_json("doc_data.json")
    queries = [
        ("sudden fever body aches", "Flu"),
        ("difficulty breathing loss smell event", "Covid"),
        ("increased thirst unexpected weight loss", "Diabetes"),
        ("extreme fatigue normal sleep routine", "Addisons"),
        ("persistent sadness low energy", "Depression"),
        ("chest pain heart palpitations", "Cardiac Arrest"),
        ("wheezing exhaling worsened respiratory virus", "Asthma"),
        ("blurred vision blind spots halos around lights", "Glaucoma"),
        ("swollen lymph nodes tiny red spots skin easy bruising", "Leukemia"),
        ("bloody stool feel need pass stools bowels empty", "Crohns Disease")
    ]
    annotate_data(queries, doc_data)
    
if __name__ == "__main__":
    main()
