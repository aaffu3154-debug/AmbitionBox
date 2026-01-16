import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def clean_salary_job(val):
    if pd.isna(val):
        return np.nan

    val = str(val).strip()

    if val.isnumeric():
        return int(val)

    if val.endswith("L"):
        return float(val.replace("L","")) * 100000

    if val.endswith("k"):
        return float(val.replace("k","")) * 1000

li=["new delhi","mumbai","pune","jaipur","ahmedabad","noida","hyderabad"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

for city in li:
    url_for_city=f"https://www.ambitionbox.com/companies-in-{city}"
    number_of_page=10
    dictonary={"title":[],"rating":[],"bio":[],"salary":[],"job":[],"founded_in":[]}
    for page in range(1,number_of_page):
        pages_url=f"{url_for_city}?page={page}"
        resp=requests.get(pages_url,headers=headers)
        soup=BeautifulSoup(resp.content)
        company_card_wrapper=soup.find_all("div",class_="companyCardWrapper")
        for data in company_card_wrapper:
            title=data.find("h2").text.strip()
            rating=data.find("div",class_="rating_text").text.strip()
            bio=data.find("span",class_="companyCardWrapper__interLinking").text.strip()
            if title:
                dictonary["title"].append(title.strip())
            else:
                dictonary["title"].append(np.nan)

            if rating:
                dictonary["rating"].append(rating.strip())
            else:
                dictonary["rating"].append(np.nan)
            if bio:
                dictonary["bio"].append(bio.strip())
            else:
                dictonary["bio"].append(np.nan)
                

            overview_url="https://www.ambitionbox.com/overview/{}-overview".format(title.strip())
            resp1=requests.get(overview_url,headers=headers)
            new_soup=BeautifulSoup(resp1.content)

            a_tag=new_soup.find("a",title=f"{title.strip()} Salaries")
            if a_tag:
                salary=a_tag.find("div",class_="text-primary-text font-pn-600 text-xs")
                if salary:
                    dictonary["salary"].append(salary.text)
                else:
                    dictonary["salary"].append(np.nan)
            else:
                dictonary["salary"].append(np.nan)
                
            job_tab=new_soup.find("a",title=f"{title.strip()} Jobs")
            if job_tab:
                job=job_tab.find("div",class_="text-primary-text font-pn-600 text-xs")
                if job:
                    dictonary["job"].append(job.text)
                else:
                    dictonary["job"].append(np.nan)
            else:
                dictonary["job"].append(np.nan)

            year=new_soup.find_all("div",class_="inline whitespace-pre-wrap break-words text-primary-text text-sm font-pn-600 flex-[6] md:flex-[auto]")
            if year:
                dictonary["founded_in"].append(year[0].text)
            else:
                dictonary["founded_in"].append(np.nan)
    df=pd.DataFrame(dictonary)
    df.to_csv(f"{city}.csv")


# fill all null values by the median-------------
for city in li:
    df=pd.read_csv(r"C:\Users\Mr Aftab\Desktop\AmbitionJobAnalysisBox\{}.csv".format(city.strip()))
    df["job"]=df["job"].apply(clean_salary_job)
    median=df["job"].median()
    df["job"].fillna(median,inplace=True)

    df["salary"]=df["salary"].apply(clean_salary_job)
    median=df["salary"].median()
    df["salary"].fillna(median,inplace=True)
    df.to_csv(r"C:\Users\Mr Aftab\Desktop\AmbitionJobAnalysisBox\{}.csv".format(city.strip()),index=False)


# show how many missing values are present in job and salary columns-------------
for city in li:
    df=pd.read_csv(r"C:\Users\Mr Aftab\Desktop\AmbitionJobAnalysisBox\{}.csv".format(city.strip()))
    print("{city} -------------->")
    print(f"job :- {df["job"].isnull().sum()}")
    print(f"salary :- {df["salary"].isnull().sum()}")
    print()

# divide bio column into field and other column---------
for city in li:
    df=pd.read_csv(r"C:\Users\Mr Aftab\Desktop\AmbitionJobAnalysisBox\{}.csv".format(city.strip()))
    df[["field","other"]]=df["bio"].str.split("|",n=1,expand=True)   
    df.to_csv(r"C:\Users\Mr Aftab\Desktop\AmbitionJobAnalysisBox\{}.csv".format(city.strip()),index=False)