import requests
from bs4 import BeautifulSoup
import json
import re

def clean_website(website_text):
    website_text = re.sub(r'\s+', ' ', website_text)
    website_text = website_text.lower().strip()
    return website_text

def extract_text_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
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

    json_data = json.dumps(doc_data, indent=2)
    with open('output_doc.json', 'w') as json_file:
        json_file.write(json_data)

def main():

    websites = {
    "Flu": [
        r'https://www.mayoclinic.org/diseases-conditions/flu/symptoms-causes/syc-20351719',
        r'https://www.cdc.gov/flu/symptoms/symptoms.htm',
        r'https://my.clevelandclinic.org/health/diseases/4335-influenza-flu',
        r'https://en.wikipedia.org/wiki/Influenza',
        r'https://www.webmd.com/cold-and-flu/ss/slideshow-flu-symptoms-treatment'
    ],
    "Covid": [
        r'https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html',
        r'https://www.who.int/health-topics/coronavirus#tab=tab_3',
        r'https://www.mayoclinic.org/diseases-conditions/coronavirus/symptoms-causes/syc-20479963',
        r'https://en.wikipedia.org/wiki/COVID-19',
        r'https://www.nhs.uk/conditions/covid-19/covid-19-symptoms-and-what-to-do/'
    ],
    "Diabetes": [
        r'https://www.mayoclinic.org/diseases-conditions/diabetes/symptoms-causes/syc-20371444',
        r'https://www.webmd.com/diabetes/understanding-diabetes-symptoms',
        r'https://www.cdc.gov/diabetes/basics/symptoms.html',
        r'https://www2.diabetes.org/diabetes/type-1/symptoms',
        r'https://www.mayoclinic.org/diseases-conditions/diabetes/in-depth/diabetes-symptoms/art-20044248'
    ],
    "Addisons Disease": [
        r'https://www.mayoclinic.org/diseases-conditions/addisons-disease/symptoms-causes/syc-20350293',
        r'https://my.clevelandclinic.org/health/diseases/15095-addisons-disease',
        r'https://www.hopkinsmedicine.org/health/conditions-and-diseases/underactive-adrenal-glands--addisons-disease',
        r'https://www.webmd.com/a-to-z-guides/understanding-addisons-disease-symptoms'
    ],
    "Depression": [
        r'https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007',
        r'https://www.medicalnewstoday.com/articles/326769',
        r'https://my.clevelandclinic.org/health/diseases/9290-depression',
        r'https://www.healthline.com/health/depression/recognizing-symptoms',
        r'https://www.nimh.nih.gov/health/topics/depression'
    ],
    "Cardiac Arrest": [
        r'https://www.hopkinsmedicine.org/health/conditions-and-diseases/cardiac-arrest',
        r'https://www.mayoclinic.org/diseases-conditions/sudden-cardiac-arrest/symptoms-causes/syc-20350634',
        r'https://www.nhlbi.nih.gov/health/cardiac-arrest/symptoms',
        r'https://www.cdc.gov/heartdisease/cardiac-arrest.htm',
        r'https://www.heart.org/en/health-topics/cardiac-arrest/emergency-treatment-of-cardiac-arrest'
    ],
    "Asthma": [
        r'https://www.mayoclinic.org/diseases-conditions/asthma/symptoms-causes/syc-20369653',
        r'https://www.webmd.com/asthma/asthma-symptoms',
        r'https://www.nhlbi.nih.gov/health/asthma/symptoms',
        r'https://www.nhlbi.nih.gov/health/asthma/causes',
        r'https://acaai.org/asthma/symptoms/',
        r'https://my.clevelandclinic.org/health/diseases/6424-asthma'
    ],
    "Glaucoma": [
        r'https://www.mayoclinic.org/diseases-conditions/glaucoma/symptoms-causes/syc-20372839',
        r'https://my.clevelandclinic.org/health/diseases/4212-glaucoma',
        r'https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/glaucoma',
        r'https://www.aao.org/eye-health/diseases/what-is-glaucoma',
        r'https://www.webmd.com/eye-health/glaucoma-eyes'
    ],
    "Leukemia": [
        r'https://www.mayoclinic.org/diseases-conditions/leukemia/symptoms-causes/syc-20374373',
        r'https://my.clevelandclinic.org/health/diseases/4365-leukemia',
        r'https://www.mskcc.org/cancer-care/types/leukemias/symptoms',
        r'https://www.hematology.org/education/patients/blood-cancers/leukemia',
        r'https://www.webmd.com/cancer/lymphoma/understanding-leukemia-basics'
    ],
    "Crohns Disease": [
        r'https://www.mayoclinic.org/diseases-conditions/crohns-disease/symptoms-causes/syc-20353304#:~:text=Crohn\'s%20disease%20is%20an%20inflammatory,deeper%20layers%20of%20the%20bowel.',
        r'https://www.crohnscolitisfoundation.org/what-is-crohns-disease/symptoms',
        r'https://medlineplus.gov/crohnsdisease.html',
        r'https://my.clevelandclinic.org/health/diseases/9357-crohns-disease',
        r'https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z/crohns-disease'
    ]
}



    scrape_websites(websites)

if __name__ == "__main__":
    main()
