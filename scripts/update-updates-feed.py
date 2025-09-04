import os
import sys
import locale
import json
import feedparser
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

base_url = 'https://www.counter-strike.net'
content_url = base_url + '/news/updates'

# Define a list of languages to fetch and parse
language_map = {
    'english': ('en', 'en_US'),
}

# Set up a Chrome WebDriver in headless mode
try:
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
except:
    sys.exit(f'Failed to initialize the headless web browser.')

# Loop over the languages and generate an RSS feed for each language
for language_name, (language_code, language_locale) in language_map.items():
    # Construct the URL for the current language
    url = f'{content_url}?l={language_name}'

    # Launch the browser and navigate to the website to fetch its HTML content
    try:
        driver.get(url)

        # Wait for the contents to appear (thanks Valve for using reactJS)
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class^="-EouvmnKRMabN5fJonx-O"]'))
        )

        # Extract the (hopefully) complete HTML
        html_content = driver.page_source
    except TimeoutException:
        driver.quit()
        sys.exit(f'Unable to find the updates container in the given time frame.')
    except Exception as e:
        driver.quit()
        sys.exit(f'Failed to extract the HTML data.')

    # Parse the HTML content with BeautifulSoup and extract all relevant information
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all div containers with class names that contain "updatecapsule_UpdateCapsule"
    capsule_divs = soup.select('div[class^="-EouvmnKRMabN5fJonx-O"]')

    # Create an array of all update items
    updates = []

    # Set locale to parse the date, but dates are currently not localized anyways (Thanks Valve)
    locale.setlocale(locale.LC_TIME, f'en_US.UTF-8') # Switch to language_locale after it's fixed (if ever)
    date_format = '%d %B %Y' # English

    # For each update capsule, find all div containers with relevant information
    for capsule in capsule_divs:
        children = capsule.find_all('div', recursive=False)
        date = datetime.strptime(children[0].text.strip(), date_format)
        title = children[1].text.strip()
        desc = children[2].decode_contents().strip()

        # Remove trailing <br/> tags at the beginning of the update description (Thanks Valve)
        while desc.startswith('<br'):
            index = desc.index('>') + 1
            desc = desc[index:]

        updates.append({
            'guid': hashlib.sha256(f'{date.day}{date.month}{date.year}'.encode()).hexdigest(),
            'title': title,
            'date': date,
            'content': desc
        })

    # Parse an existing RSS feed file and compare the last entry
    github_workspace = os.getenv('GITHUB_WORKSPACE')

    if github_workspace:
        rss_feed_file = os.path.join(os.environ['GITHUB_WORKSPACE'], 'feeds', f'updates-feed-{language_code}.xml')
    else:
        rss_feed_file = os.path.join(os.pardir, 'feeds', f'updates-feed-{language_code}.xml')

    skip_file = False

    if os.path.exists(rss_feed_file):
        current_feed = feedparser.parse(rss_feed_file)
        if current_feed.entries and updates:
            current_description = current_feed.entries[0].description[:250]
            new_description = updates[0]['content'][:250]
            if current_description == new_description:
                skip_file = True

    # Generate the RSS feed with feedgen if the latest entry is different from the current RSS feed
    if not skip_file:
        feed_link = f'https://raw.githubusercontent.com/acefrogge/CS-RSS-Feed/master/feeds/updates-feed-{language_code}.xml'

        fg = FeedGenerator()
        fg.title(f'Counter-Strike 2 - Updates ({language_name.capitalize()})')
        fg.description('Counter-Strike 2 Updates Feed')
        fg.link(href=feed_link, rel='self')
        fg.language(language_code)

        # Add the extracted information as entries to the RSS feed
        for update in reversed(updates):
            fe = fg.add_entry()
            fe.source(url)
            fe.guid(update['guid'])
            fe.title(update['title'])
            fe.link({
                'href': url,
                'rel': 'alternate',
                'type': 'text/html',
                'hreflang': language_code,
                'title': update['title']
            })
            fe.pubDate(datetime.strftime(update['date'], '%Y-%m-%dT%H:%M:%SZ'))
            fe.author({'name':'Valve Corporation', 'email':'support@steampowered.com'})
            fe.content(update['content'], None, 'CDATA')
            fe.rights('Valve Corporation')

        rss_content = fg.rss_str(pretty=True)

        # Create or update XML File
        with open(rss_feed_file, "wb") as f:
            f.write(rss_content)

driver.quit()
sys.exit(0)
