import re
from typing import List

from common import Factual, Source


def simple_left_right_bias(sources: List[Source]):
    def fact():
        return {v: 0 for v in [Factual.HIGH, Factual.MIXED, Factual.QUESTIONABLE]}

    biases = {k: fact() for k in ['extremeleft', 'left', 'leftcenter', 'leastbiased', 'rightcenter', 'right', 'extremeright']}
    for source in sources:
        bias = re.findall('^([a-z]*)', source.img_url.split('/')[-1])[0]
        biases[bias][source.factual] += 1
    for k, v in biases.items():
        print(k, v)


def data_table(sources: List[Source]):
    print('<table id="table_id" class="display">')
    print('    <thead>')
    print('    <tr>')
    print('        <th>Name</th>')
    print('        <th>Factual Reporting</th>')
    print('        <th>Bias</th>')
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
        print(f'        <th><a href="{source.img_url}">{image}</a></th>')
        print(f'        <th><a href="{source.page_url}">link</a></th>')
        print(f'    </tr>')
    print('    </tbody>')
    print('</table>')
