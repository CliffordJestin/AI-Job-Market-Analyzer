# nakuri_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

from db_utils import create_database, insert_job

# Your ChromeDriver path
CHROMEDRIVER_PATH = r"D:\webdriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Roles to scrape
roles = [
    "Data Analyst",
    "Data Scientist",
    "Software Developer",
    "Machine Learning Engineer",
    "AI Engineer",
    "Business Analyst",
    "NLP Researcher",
    "Cloud Computing",
    "QA Testing"

]

def get_job_links(role, max_pages=5):
    options = Options()
    # options.add_argument('--headless')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    job_links = []
    try:
        for page in range(1, max_pages + 1):
            url = f"https://www.naukri.com/{role.replace(' ', '-')}-jobs-{page}?k={role.replace(' ', '%20')}"
            print(f"🔗 Visiting: {url}")
            driver.get(url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.title"))
            )
            time.sleep(2)

            links = driver.find_elements(By.CSS_SELECTOR, "a.title")
            page_links = [link.get_attribute("href") for link in links if link.get_attribute("href")]
            print(f"✅ Found {len(page_links)} job links")
            job_links.extend(page_links)

            if len(page_links) < 20:
                break

    except Exception as e:
        print(f"❌ Error getting job links for role '{role}' page {page}: {e}")
    finally:
        driver.quit()

    return job_links

def scrape_job_details(driver, job_url):
    try:
        driver.get(job_url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        job_title_elem = soup.select_one("h1.styles_jd-header-title__rZwM1")
        job_title = job_title_elem.text.strip() if job_title_elem else "N/A"

        company_elem = soup.select_one("a[title$='Careers']")
        company_name = company_elem.text.strip() if company_elem else "N/A"

        exp_elem = soup.find("span", string=lambda x: x and "year" in x.lower())
        experience = exp_elem.text.strip() if exp_elem else "N/A"

        salary_elem = soup.find_all("span")
        salary = "N/A"
        for span in salary_elem:
            if "lacs" in span.text.lower() or "disclosed" in span.text.lower():
                salary = span.text.strip()
                break

        desc_elem = soup.find("p")
        description = desc_elem.text.strip() if desc_elem else "N/A"

        ### --- Location extraction ---
        location_links = soup.select('a[title*="Jobs in"]')
        all_locations = [link.text.strip() for link in location_links]

        remote_explicit = False
        remote_link = soup.select_one('a.styles_jhc__wfhmode-link__aHmrK')
        if remote_link and 'remote' in remote_link.text.strip().lower():
            remote_explicit = True

        remote_location_block = soup.select_one('div.styles_jhc__loc___Du2H')
        remote_location_text_elem = remote_location_block.select_one('a') if remote_location_block else None
        if remote_location_text_elem and 'remote' in remote_location_text_elem.text.strip().lower():
            remote_explicit = True

        if remote_explicit:
            location = "Remote"
        elif all_locations:
            unique_locations = list(dict.fromkeys(all_locations))
            location = ', '.join(unique_locations)
        else:
            location = "N/A"
        posted_date = "N/A"
        try:
            label_elem = soup.find("label", string=re.compile(r"Posted", re.I))
            if label_elem and label_elem.find_next("span"):
                posted_date = label_elem.find_next("span").text.strip()
        except Exception as e:
            print(f"⚠️ Could not extract posted date: {e}")

        ### --- Skills extraction ---
        skills_spans = soup.select('div.styles_heading__veHpg + div a span')
        skills = [span.text.strip() for span in skills_spans]
        skills_string = ', '.join(skills) if skills else "N/A"
        # --- Posted Date Extraction ---
        posted_elem = soup.find('label', string=re.compile('Posted', re.I))
        posted_text = "N/A"
        if posted_elem:
            sibling = posted_elem.find_next_sibling("span")
            if sibling:
                posted_text = sibling.text.strip()


        return {
            "title": job_title,
            "company": company_name,
            "experience": experience,
            "salary": salary,
            "location": location,
            "description": description,
            "url": job_url,
            "skills": skills_string,
            "posted_date": posted_date

        }

    except Exception as e:
        print(f"❌ Error scraping job at {job_url}: {e}")
        return None

def main():
    create_database(drop_existing=True)
    options = Options()
    # options.add_argument('--headless')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    for role in roles:
        print(f"\n🔍 Scraping role: {role}")
        job_links = get_job_links(role)
        print(f"🌐 Scraping {len(job_links)} job pages for role: {role}")

        for url in job_links:
            job_data = scrape_job_details(driver, url)
            if job_data:
                job_data['role'] = role
                insert_job(job_data)

    driver.quit()
    print("\n✅ Scraping done and data saved to jobs.db!")

if __name__ == "__main__":
    main()
