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
    bias: int


@dataclass
class BrokenSource(object):
    page_url: str
    error_message: str


@dataclass
class AdFontesMediaSource(object):
    name: str
    vertical_rank: int
    horizontal_rank: int
