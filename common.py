from dataclasses import dataclass
from enum import Enum


class Factual(Enum):
    HIGH = 1
    MIXED = 2
    QUESTIONABLE = 3


@dataclass
class Source(object):
    name: str
    page_url: str
    img_url: str
    factual: Factual


@dataclass
class BrokenSource(object):
    page_url: str
    error_message: str