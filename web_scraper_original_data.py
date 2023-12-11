import requests
from bs4 import BeautifulSoup
import json
import re
from BM25 import BM25
from urllib.parse import urljoin

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

def scrape_websites(websites, filename):
    doc_data = {"documents": []}
    for category, urls in websites.items():
        for i, url in enumerate(urls, 1):
            doc_id = f"{category[:3]}{i}"
            text_data = extract_text_from_website(url)
            doc_data["documents"].append({"doc_id": doc_id, "text": text_data})

    write_json(doc_data, filename)

def annotate_data(queries, doc_data, filename):
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
    if disease in websites:
        existing_links = set(websites[disease])
        new_links_set = set(new_links)
        websites[disease] = list(existing_links.union(new_links_set))
    else:
        websites[disease] = new_links

    write_json(websites, filename)

def main():
    
    websites = load_json("websites.json")
    scrape_websites(websites, "doc_data.json")
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
    annotate_data(queries, doc_data, "annotated_data.json")
    relevance_data = load_json("annotated_data.json")
    queries = [query[0] for query in queries]
    model = BM25(doc_data)

    print(model.mean_avg_precision(queries, relevance_data, 5))

    # NOW EVALUATING BM25 FOR MANY DOCUMENTS
    print("Expanded Model More Data")
    flu_seeds = ["https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
        "https://www.mayoclinic.org/diseases-conditions/search-results?q=flu",
        "https://my.clevelandclinic.org/health/diseases/4335-influenza-flu",
        "https://www.healthline.com/health/flu-causes",
        "https://www.yalemedicine.org/conditions/flu",
        "https://www.cdc.gov/flu/symptoms/symptoms.htm"
    ]
    
    covid_seeds = [
        "https://www.who.int/emergencies/diseases/novel-coronavirus-2019",
        "https://www.cdc.gov/coronavirus/2019-ncov/index.html",
        "https://www.mayoclinic.org/diseases-conditions/coronavirus/symptoms-causes/syc-20479963",
        ]

    diabetes_seeds = [
        "https://www.medicalnewstoday.com/info/diabetes",
        "https://www.mayoclinic.org/diseases-conditions/diabetes/symptoms-causes/syc-20371444",
        "https://www.cdc.gov/diabetes/index.html",
        ]

    addisons_seeds = ["https://www.niddk.nih.gov/health-information/endocrine-diseases/addisons-disease",
        "https://www.medicalnewstoday.com/articles/164648",
        "https://www.healthline.com/health/addisons-disease",
        "https://rarediseases.org/rare-diseases/addisons-disease/",
        "https://www.mayoclinic.org/diseases-conditions/addisons-disease/symptoms-causes/syc-20350293",
        "https://www.webmd.com/a-to-z-guides/addisons-disease#1",
        "https://rarediseases.info.nih.gov/diseases/5779/addisons-disease",
        "https://www.cedars-sinai.org/health-library/diseases-and-conditions/a/addisons-disease.html",
        "https://www.uptodate.com/contents/addisons-disease-clinical-manifestations-diagnosis-and-treatment",
        "https://patient.info/doctor/addisons-disease",
        "https://emedicine.medscape.com/article/116467-overview",
        "https://www.cdc.gov/genomics/resources/diseases/addisons.htm"
        ]   
    
    depression_seeds = [
        "https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007",
        "https://www.webmd.com/depression/default.htm",
        "https://www.psychologytoday.com/us/basics/depression",
        "https://www.nimh.nih.gov/health/topics/depression/index.shtml",
        ]
    
    cardiac_arrest_seeds = ["https://www.heart.org/en/health-topics/heart-attack",
        "https://www.healthline.com/health/heart-attack",
        "https://www.mayoclinic.org/diseases-conditions/sudden-cardiac-arrest/symptoms-causes/syc-20350634",
        "https://www.heart.org/en/health-topics/cardiac-arrest",
        "https://www.nhlbi.nih.gov/health-topics/sudden-cardiac-arrest",
        "https://www.medicinenet.com/sudden_cardiac_arrest/article.htm",
        "https://www.health.harvard.edu/heart-health/sudden-cardiac-arrest-what-you-need-to-know",
        "https://www.nhs.uk/conditions/cardiac-arrest/",
        "https://www.heart.org/en/news/2023/02/09/this-is-what-a-cardiac-arrest-looks-like-and-why-you-need-to-know"
        ]

    asthma_seeds = [
        "https://www.mayoclinic.org/diseases-conditions/asthma/symptoms-causes/syc-20369653",
        "https://www.webmd.com/asthma/default.htm",
        "https://www.lung.org/lung-health-diseases/lung-disease-lookup/asthma",
        "https://www.cdc.gov/asthma/index.html",
        "https://www.nhlbi.nih.gov/health-topics/asthma",
        "https://www.healthline.com/health/asthma",
        "https://www.medicalnewstoday.com/articles/323129",
        "https://www.aaaai.org/conditions-and-treatments/asthma",
        ]

    glaucoma_seeds = [
        "https://www.mayoclinic.org/diseases-conditions/glaucoma/symptoms-causes/syc-20372839",
        "https://www.webmd.com/eye-health/glaucoma/default.htm",
        "https://www.aao.org/eye-health/diseases/what-is-glaucoma",
        "https://www.glaucoma.org/glaucoma/",
        ]

    leukemia_seeds = [
        "https://www.cancer.org/cancer/leukemia.html",
        "https://www.mayoclinic.org/diseases-conditions/leukemia/symptoms-causes/syc-20374373",
        "https://www.webmd.com/cancer/lymphoma/understanding-leukemia-basics",
        "https://www.lls.org/leukemia",
        "https://www.cancer.gov/types/leukemia",
        "https://www.cancer.net/cancer-types/leukemia-acute-lymphoblastic-all/statistics",
        "https://www.medicalnewstoday.com/articles/142595",
        "https://www.healthline.com/health/leukemia",
        ]
    
    crohns_disease_seeds = [
        "https://www.mayoclinic.org/diseases-conditions/crohns-disease/symptoms-causes/syc-20353304",
        "https://www.webmd.com/ibd-crohns-disease/default.htm",
        "https://www.crohnscolitisfoundation.org/what-is-crohns-disease",
        "https://www.cdc.gov/ibd/data-statistics.htm",
        "https://www.niddk.nih.gov/health-information/digestive-diseases/crohns-disease",
        "https://www.medicalnewstoday.com/articles/151620",
        "https://www.healthline.com/health/crohns-disease",
        "https://www.gastro.org/practice-guidance/gi-patient-center/topic/crohns-disease",
        ]
    
    flu_websites = web_crawler(flu_seeds, "flu")
    covid_websites = web_crawler(covid_seeds, "covid")
    diabetes_websites = web_crawler(diabetes_seeds, "diabetes")
    addisons_websites = web_crawler(addisons_seeds, "addisons")
    depression_websites = web_crawler(depression_seeds, "depression")
    cardiac_arrest_websites = web_crawler(cardiac_arrest_seeds, "cardiac")
    asthma_websites = web_crawler(asthma_seeds, "asthma")
    glaucoma_websites = web_crawler(glaucoma_seeds, "glaucoma")
    leukemia_websites = web_crawler(leukemia_seeds, "leukemia")
    crohns_disease_websites = web_crawler(crohns_disease_seeds, "crohns-disease")

    update_websites_json("Flu", flu_websites, websites, "updated_websites.json")
    update_websites_json("Covid", covid_websites, websites, "updated_websites.json")
    update_websites_json("Diabetes", diabetes_websites, websites, "updated_websites.json")
    update_websites_json("Addisons Disease", addisons_websites, websites, "updated_websites.json")
    update_websites_json("Depression", depression_websites, websites, "updated_websites.json")
    update_websites_json("Cardiac Arrest", cardiac_arrest_websites, websites, "updated_websites.json")
    update_websites_json("Asthma", asthma_websites, websites, "updated_websites.json")
    update_websites_json("Glaucoma", glaucoma_websites, websites, "updated_websites.json")
    update_websites_json("Leukemia", leukemia_websites, websites, "updated_websites.json")
    update_websites_json("Crohns Disease", crohns_disease_websites, websites, "updated_websites.json")
    
    websites = load_json("updated_websites.json")
    scrape_websites(websites, "updated_doc_data.json")
    doc_data = load_json("updated_doc_data.json")
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
    annotate_data(queries, doc_data, "updated_annotated_data.json")
    relevance_data = load_json("updated_annotated_data.json")
    queries = [query[0] for query in queries]
    relevance_data = load_json("updated_annotated_data.json")
    model = BM25(doc_data)

    print(model.mean_avg_precision(queries, relevance_data, 5))
if __name__ == "__main__":
    main()
