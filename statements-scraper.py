import re
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from sys import stderr, exit
from urllib.parse import urljoin
from weasyprint import HTML

BASE_URL = 'https://www.ietf.org'
URL = f'{BASE_URL}/about/groups/iesg/statements/'


def save_content(url, filename):
    '''Save content as markdown. If image is present, save the PDF as well.'''

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the main content of the page
    main_content = soup.find('main')

    # find and delete unwanted
    for element_type in ['nav', 'form', 'button']:
        elements = main_content.find_all(element_type)
        for element in elements:
            element.decompose()
    filter_by = main_content.find('h6')
    if filter_by:
        filter_by.decompose()
    social = main_content.find('h2', string='Share this page')
    while social:
        next_element = social.nextSibling
        social.decompose()
        social = next_element

    # save markdown
    markdown = md(str(main_content))

    # write to markdown file
    with open(f'{filename}.md', 'w') as file:
        file.write(markdown)
        print(f'saved to {filename}.md')

    # check if images are present
    if len(main_content.find_all('img')) > 0:
        # save PDF file
        style = '<style>img { max-width: 100%; }</style>'
        html = f'<html><head>{style}</head><body>{main_content}</body></html>'
        HTML(string=html, base_url=BASE_URL).write_pdf(f'{filename}.pdf')
        print(f'saved to {filename}.pdf')


response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# find minutes entries
main_content = soup.find('main')
statements = main_content.select('tr')

# process statements
for statement in statements:
    tds = statement.find_all('td')
    # get meeting date
    date = tds[0].text
    match  = re.search(r'\d{4}-\d{2}-\d{2}', date)
    if match:
        date = match.group()
    else:
        stderr.write(f'Can not determine statement date from {date}')
        exit(1)
    print(f'processing statement on {date}')

    stement_link = urljoin(BASE_URL, tds[1].find('a')['href'])

    save_content(stement_link, date)
