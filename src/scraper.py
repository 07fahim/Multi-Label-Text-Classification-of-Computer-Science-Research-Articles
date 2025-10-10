from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import logging
from pathlib import Path
import random


YEAR = 2025
SHOW = 2000  
MAX_PAPERS_PER_YEAR = 10000  
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_driver():
    options = Options()
    options.add_argument('--headless=new')  # fully headless
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 60)
    return driver, wait

def scrape_page(driver, wait, url):
    papers = []
    try:
        driver.get(url)
        logging.info(f"Opening page: {url}")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'dl#articles')))
        time.sleep(random.uniform(2, 4))
        paper_entries = driver.find_elements(By.CSS_SELECTOR, 'dl#articles > dt')
        detail_entries = driver.find_elements(By.CSS_SELECTOR, 'dl#articles > dd')
        for i in range(len(paper_entries)):
            try:
                dt = paper_entries[i]
                dd = detail_entries[i]
                # Title
                title_elem = dd.find_element(By.CSS_SELECTOR, 'div.list-title')
                title = title_elem.text.replace('Title:', '').strip()
                # URL
                abs_url_elem = dt.find_element(By.CSS_SELECTOR, 'a[title="Abstract"]')
                abs_url = abs_url_elem.get_attribute('href').strip()
                full_url = abs_url if abs_url.startswith('http') else f'https://arxiv.org{abs_url}'
                # Authors
                authors_elem = dd.find_element(By.CSS_SELECTOR, 'div.list-authors')
                authors_text = authors_elem.text.replace('Authors:', '').strip()
                authors = [a.strip() for a in authors_text.split(',') if a.strip()]
                # Subjects
                subjects_elem = dd.find_element(By.CSS_SELECTOR, 'div.list-subjects')
                subjects_text = subjects_elem.text.replace('Subjects:', '').strip()
                subjects = [s.strip() for s in subjects_text.split(';') if s.strip()]
                papers.append({
                    'title': title,
                    'abstract': "",
                    'subjects': subjects,
                    'url': full_url,
                    'authors': authors
                })
            except Exception as e:
                logging.warning(f"Error parsing paper {i+1}: {e}")
                continue
        logging.info(f"Scraped {len(papers)} papers from {url}")
        return papers
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}")
        return []

def fetch_abstract(driver, wait, paper):
    try:
        driver.get(paper['url'])
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'blockquote.abstract')))
        abstract_elem = driver.find_element(By.CSS_SELECTOR, 'blockquote.abstract')
        paper['abstract'] = abstract_elem.text.replace('Abstract:', '').strip()
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        logging.warning(f"Failed to fetch abstract for {paper['url']}: {e}")
        paper['abstract'] = ""
    return paper


driver, wait = create_driver()  
all_papers = []

# Calculate how many pages are needed to reach 10k
pages_needed = MAX_PAPERS_PER_YEAR // SHOW
logging.info(f"Scraping {pages_needed} pages (~{MAX_PAPERS_PER_YEAR} papers) for {YEAR}")

for page_num in range(pages_needed):
    skip = page_num * SHOW
    if page_num == 0:
        url = f"https://arxiv.org/list/cs/{YEAR}?show={SHOW}"
    else:
        url = f"https://arxiv.org/list/cs/{YEAR}?skip={skip}&show={SHOW}"
    page_papers = scrape_page(driver, wait, url)
    all_papers.extend(page_papers)
all_papers = all_papers[:MAX_PAPERS_PER_YEAR]
logging.info(f"Total papers scraped: {len(all_papers)}")

# Fetch abstracts
for idx, paper in enumerate(all_papers, 1):
    all_papers[idx-1] = fetch_abstract(driver, wait, paper)
    if idx % 50 == 0:
        logging.info(f"Fetched {idx} abstracts so far...")

# Save CSV
output_file = OUTPUT_DIR / f"cs_{YEAR}_papers_10k.csv"
df = pd.DataFrame(all_papers)
df.to_csv(output_file, index=False, encoding='utf-8')
logging.info(f"Saved papers to {output_file}")

driver.quit()
