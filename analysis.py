import csv
import re
from typing import List, Dict

from common import Factual, Source, AdFontesMediaSource


def simple_left_right_bias(sources: List[Source]) -> Dict[str, Dict[Factual, int]]:
    def fact():
        return {v: 0 for v in [Factual.HIGH, Factual.MIXED, Factual.QUESTIONABLE]}

    biases = {k: fact() for k in ['extremeleft', 'left', 'leftcenter', 'leastbiased', 'rightcenter', 'right', 'extremeright']}
    for source in sources:
        bias = re.findall('^([a-z]*)', source.img_url.split('/')[-1])[0]
        biases[bias][source.factual] += 1
    return biases


def simple_left_right_bias_percent(sources: List[Source]):
    biases = simple_left_right_bias(sources)
    for bias, d in biases.items():
        total = 0
        for number in d.values():
            total += number
        for factual, number in d.items():
            d[factual] = round(number / total * 100)
    return biases


def data_table(sources: List[Source]):
    print('<table id="table_id" class="display">')
    print('    <thead>')
    print('    <tr>')
    print('        <th>Name</th>')
    print('        <th>Factual Reporting</th>')
    print('        <th>Bias</th>')
    print('        <th>Estimated Bias Value</th>')
    print('        <th>Left-Right Spectrum Image</th>')
    print('        <th>Page Link</th>')
    print('    </tr>')
    print('    </thead>')
    print('    <tbody>')
    for source in sources:
        factual = str(source.factual).split('.')[1]
        image = source.img_url.split('/')[-1]
        bias = re.findall('^([a-z]*)', source.img_url.split('/')[-1])[0]
        if bias == 'extremeleft':
            bias = 'Extreme Right'
        elif bias == 'left':
            bias = 'Left'
        elif bias == 'leftcenter':
            bias = 'Left Centre'
        elif bias == 'leastbiased':
            bias = 'Least Biased'
        elif bias == 'rightcenter':
            bias = 'Right Centre'
        elif bias == 'right':
            bias = 'Right'
        elif bias == 'extremeright':
            bias = 'Extreme Right'
        print(f'    <tr>')
        print(f'        <th>{source.name}</th>')
        print(f'        <th>{factual}</th>')
        print(f'        <th>{bias}</th>')
        print(f'        <th>{source.bias}</th>')
        print(f'        <th><a href="{source.img_url}">{image}</a></th>')
        print(f'        <th><a href="{source.page_url}">link</a></th>')
        print(f'    </tr>')
    print('    </tbody>')
    print('</table>')


def load_adfontesmedia_sources(file_name: str) -> List[AdFontesMediaSource]:
    sources = []
    with open(file_name) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        next(reader, None)  # skip the headers
        for row in reader:
            sources.append(AdFontesMediaSource(name=row[0], vertical_rank=int(row[1]), horizontal_rank=int(row[2])))
    return sources


def compare_to_adfontesmedia(sources: List[Source], csv_adfontesmedia_path='Media Bias Chart Version 4.0 - ad fontes media.csv'):
    adfontesmedia_data = load_adfontesmedia_sources(csv_adfontesmedia_path)
    data = []
    for source in sources:
        for datum in adfontesmedia_data:
            if source.name == datum.name:
                data.append([source, datum])

    data = sorted(data, key=(lambda i: ((i[0].bias + i[1].horizontal_rank) / 2 + 100)))
    for d in data:
        print(f'{{ y: [{d[0].bias}, {d[1].horizontal_rank}], label: "{d[0].name}", difference: {d[1].horizontal_rank - d[0].bias} }},')

    print(["rgb(255, 127, 14)" if d[1].horizontal_rank > d[0].bias else "rgb(31, 119, 180)" for d in data])
