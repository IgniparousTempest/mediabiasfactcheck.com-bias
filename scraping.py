import csv
import warnings
from typing import List, Tuple
from urllib import request

import cv2
import numpy as np
from requests import get
from requests.exceptions import HTTPError
from contextlib import closing
from bs4 import BeautifulSoup

from common import Source, BrokenSource, Factual
from image_processing import analyse_left_right_image


class NotANewsSourceError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise raise Exception.
    """
    with closing(get(url, stream=True)) as resp:
        if is_good_response(resp):
            return resp.content
        else:
            resp.raise_for_status()


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def get_pages() -> List[str]:
    """
    Gets all known media pages from the category pages specified in the function.
    :return: The media pages to be scraped.
    """
    sources = ['https://mediabiasfactcheck.com/fake-news/', 'https://mediabiasfactcheck.com/left/',
               'https://mediabiasfactcheck.com/leftcenter/', 'https://mediabiasfactcheck.com/center/',
               'https://mediabiasfactcheck.com/right-center/', 'https://mediabiasfactcheck.com/right/']
    pages: List[str] = []

    for source in sources:
        print('# # # # # # # # # # # # # #')
        print('Finding pages in this category:')
        print(source)
        print('# # # # # # # # # # # # # #')
        raw_html = simple_get(source)
        bs = BeautifulSoup(raw_html, 'html.parser')
        links = bs.find('p', attrs={'style': 'text-align: center;'})
        for a in links.select('a'):
            print(a['href'])
            pages.append(a['href'])
        print()

    return pages


def scrape_sources(urls: List[str]) -> Tuple[List[Source], List[BrokenSource]]:
    broken_sources = []
    sources = []
    for url in urls:
        try:
            sources.append(scrape_source(url))
        except NotANewsSourceError as e:
            broken_sources.append(BrokenSource(page_url=url, error_message=str(e)))
            warnings.warn(str(e))
    return sources, broken_sources


def scrape_source(url: str) -> Source:
    try:
        raw_html = simple_get(url)
    except HTTPError as e:
        raise NotANewsSourceError(f'The page "{url}" did not contain valid content.')
    bs = BeautifulSoup(raw_html, 'html.parser')

    try:
        source_name = bs.find('h1', attrs={'class', 'page-title page-title-layout1'}).getText()
    except Exception as e:
        raise NotANewsSourceError(f'The page "{url}" does not have a name')

    try:
        headings = bs.find_all('h1')
        images = []
        for heading in headings:
            images += heading.find_all('img', recursive=True)
        image = images[0]
        # images = bs.find_all('img', attrs={'class', 'aligncenter'})
        # image = [i for i in filter(lambda img: img['alt'] != '', images)][0]
        image_url: str = image["src"]
        image_url = image_url[:image_url.find('?')]
    except Exception as e:
        # print(images)
        # print(e)
        raise NotANewsSourceError(
            f'The source "{source_name}" with url "{url}" does not contain a left-right bias image.')

    try:
        def _get_factual(text):
            if 'MIXED' in text:
                return Factual.MIXED
            elif 'HIGH' in text or 'Factual Reporting: High' in text:
                return Factual.HIGH
            elif 'QUESTIONABLE SOURCE' in text:
                return Factual.QUESTIONABLE
            else:
                return None

        description = bs.find('meta', property='og:description')['content'].replace('\u00a0', ' ')
        factual = _get_factual(description)

        factual_text = None
        if factual is None:
            paragraphs = bs.find_all('p')
            for p in paragraphs:
                factual_text = p.getText().replace('\u00a0', ' ').lower()
                if 'factual reporting:' in factual_text:
                    factual = _get_factual(p.find('span').find('strong').getText().strip().upper())
                    break
        if factual is None:
            raise Exception()
    except Exception as e:
        raise NotANewsSourceError(f'Could not find factual information on "{source_name}" with url "{url}"')

    bias = analyse_left_right_image(left_right_image_from_url(url))

    print(f'Scraping {url} with name "{source_name}", img "{image_url}", and bias {bias}')
    return Source(name=source_name, img_url=image_url, page_url=url, factual=factual, bias=bias)


def store_sources(sources: List[Source], file_name='sources_file.csv'):
    with open(file_name, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for source in sources:
            writer.writerow([source.name, source.page_url, source.img_url, source.factual, source.bias])


def load_sources(file_name='sources_file.csv') -> List[Source]:
    sources = []
    with open(file_name) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            sources.append(Source(name=row[0], img_url=row[2], page_url=row[1], factual=Factual[row[3].split('.')[1]], bias=int(row[4])))
    return sources


def left_right_image_from_url(url: str) -> np.ndarray:
    req = request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)  # 'Load it as it is'

    # return the image
    return img
