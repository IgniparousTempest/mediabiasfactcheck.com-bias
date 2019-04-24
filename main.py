from pathlib import Path

from analysis import simple_left_right_bias, data_table
from scraping import get_pages, scrape_sources, store_sources, load_sources

if __name__ == '__main__':
    if not Path('sources_file.csv').is_file():
        # print(scrape_source('http://mediabiasfactcheck.com/9-news-australia/'))
        pages = get_pages()
        sources, broken_sources = scrape_sources(pages)
        store_sources(sources)

    sources = load_sources()
    simple_left_right_bias(sources)
    data_table(sources)
