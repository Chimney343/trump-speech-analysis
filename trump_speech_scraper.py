"""
trump_speech_scraper.py

GOAL:
Download Donald Trumps' speeches from factba.se and store them in a .json file.

The main speches page ('https://factba.se/transcripts/speeches') contains links to separate speeches. The page has a
lazy-loading scheme, so the selenium webdriver scrolls it down every now and then, searches for new speech links
, accesses and scrapes them, and finally stores them in a .json file.

RESULT:
A .json file containing speech id, url and speech text.
"""

# PARAMETERS
URL = 'https://factba.se/transcripts/speeches'
N_SCRAPES = 2000
RESULT = 'trump_speeches'

# DO NOT EDIT BELOW THIS POINT
# IMPORTS
import time
import datetime
import json
import requests
import traceback
from selenium import webdriver
from bs4 import BeautifulSoup


def scrape_speech(url):
    keys = ['url', 'title', 'date', 'speech']
    speech_data = dict.fromkeys(keys)
    speech_data['url'] = url
    try:
        # Access url.
        print("Accessing url: {}".format(url))
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        # Get title.
        title = soup.find(attrs={"name": "description"})['content']
        speech_data['title'] = title
        print('{}\n'.format(title))
#       Get date.
        raw_date = speech_data['title'].split('-')[-1].strip()
        date = datetime.datetime.strptime(raw_date, '%B %d, %Y')
        speech_data['date'] = date
        # Get speech text.
        results = soup.find('script', {'type': 'application/ld+json'})
        content = json.loads(results.contents[0], strict=False)
        speech = content['articleBody'].strip()
        speech_data['speech'] = speech
    except Exception as e:
        error = traceback.format_exc()
        speech_data['title'] = error
        speech_data['speech'] = error
    return speech_data


def main():
    # Run webdriver and open the main webpage.
    driver = webdriver.Firefox()
    driver.get(URL)
    # Create containers and counters.
    speeches = []
    scrape_count = 0
    print("Commencing scraping.")
    while scrape_count <= N_SCRAPES:
        try:
            content = driver.find_elements_by_xpath(
                '/html/body/div[3]/div[1]/div[2]/div[1]/div[1]/ul/li[{}]/div[2]/div[1]/h3/a'.format(scrape_count))
            url = content[0].get_attribute('href')
            speech_data = scrape_speech(url)
            speeches.append(speech_data)
        except:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        scrape_count += 1
    print("Finished. Saving to .json.")
    with open('{}_{}.json'.format(RESULT, time.asctime().replace(':', '-').replace(' ', '_')), 'w') as fout:
        json.dump(speeches, fout)


if __name__ == '__main__':
    main()
