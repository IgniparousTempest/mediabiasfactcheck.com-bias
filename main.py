from pathlib import Path

from analysis import simple_left_right_bias, data_table, simple_left_right_bias_percent, compare_to_adfontesmedia
from scraping import get_pages, scrape_sources, store_sources, load_sources

if __name__ == '__main__':
    if not Path('sources_file.csv').is_file():
        # print(scrape_source('http://mediabiasfactcheck.com/9-news-australia/'))
        pages = get_pages()
        sources, broken_sources = scrape_sources(pages)
        store_sources(sources)

    sources = load_sources()
    print('\nNumbers:')
    biases = simple_left_right_bias(sources)
    for k, v in biases.items():
        print(k, v)

    print('\nPercents:')
    biases = simple_left_right_bias_percent(sources)
    for k, v in biases.items():
        print(k, v)

    # data_table(sources)
    print('\nAd Fontes Media:')
    compare_to_adfontesmedia(sources)
