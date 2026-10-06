import requests
import os
from dotenv import load_dotenv
from database import insert_job, init_db

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Define categories and their search keywords
JOB_CATEGORIES = {
    'Tech': ['python', 'sde intern', 'developer intern', 'mern', 'react', 'java', 'data science'],
    'Non-Tech': ['marketing', 'sales', 'hr', 'finance', 'content writer', 'operations'],
    'Design': ['ui ux', 'graphic designer', 'product designer', 'video editor']
}

# =====================================
# RemoteOK API
# =====================================
def fetch_remoteok_jobs(keyword='python', category='Tech'):
    print(f"Fetching from RemoteOK for '{keyword}' ({category})...")
    url = "https://remoteok.com/api"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        jobs = data[1:] if len(data) > 0 else []

        count = 0
        for job in jobs:
            title = job.get('position', 'N/A')
            company = job.get('company', 'N/A')
            location = job.get('location', 'Remote')
            job_url = job.get('url', '')
            posted = job.get('date', 'N/A')

            if keyword.lower() in title.lower():
                added = insert_job(title, company, location, 'RemoteOK', job_url, posted, category)
                if added:
                    count += 1
        print(f"RemoteOK: {count} new jobs added for {category}")
        return count
    except Exception as e:
        print(f"RemoteOK Error: {e}")
        return 0

# =====================================
# Adzuna API
# =====================================
def fetch_adzuna_jobs(keyword='python intern', category='Tech', country='in', pages=1):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Adzuna API keys not found - skipping Adzuna fetch")
        return 0

    print(f"Fetching from Adzuna for '{keyword}' ({category})...")
    total_count = 0

    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'results_per_page': 20,
            'what': keyword,
            'content-type': 'application/json'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            for job in data.get('results', []):
                title = job.get('title', 'N/A')
                company = job.get('company', {}).get('display_name', 'N/A')
                location = job.get('location', {}).get('display_name', 'N/A')
                job_url = job.get('redirect_url', '')
                posted = job.get('created', 'N/A')[:10]

                added = insert_job(title, company, location, 'Adzuna', job_url, posted, category)
                if added:
                    total_count += 1
        except Exception as e:
            print(f"Adzuna Error: {e}")
            break

    print(f"Adzuna: {total_count} new jobs added for {category}")
    return total_count

# =====================================
# Run all fetchers
# =====================================
def fetch_all():
    init_db()
    total = 0
    for category, keywords in JOB_CATEGORIES.items():
        for kw in keywords:
            total += fetch_remoteok_jobs(kw, category)
            total += fetch_adzuna_jobs(kw, category)
    print(f"\nTotal new jobs added: {total}")
    return total

if __name__ == '__main__':
    fetch_all()