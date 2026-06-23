from dataclasses import dataclass
from typing import Protocol
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import requests

SWISSWATCHEXPO_URLS = {
    'airking': 'https://www.swisswatchexpo.com/watches/rolex/air-king/',
    'cellini': 'https://www.swisswatchexpo.com/watches/rolex/cellini/',
    'date': 'https://www.swisswatchexpo.com/watches/rolex/date/',
    'datejust': 'https://www.swisswatchexpo.com/watches/rolex/datejust/',
    'datejust41': 'https://www.swisswatchexpo.com/watches/rolex/datejust-ii/',
    'daytona': 'https://www.swisswatchexpo.com/watches/rolex/daytona/',
    'explorer': 'https://www.swisswatchexpo.com/watches/rolex/explorer/',
    'gmt_master': 'https://www.swisswatchexpo.com/watches/rolex/gmtmaster/',
    'milgauss': 'https://www.swisswatchexpo.com/watches/rolex/milgauss/',
    'oyster_perpetual': 'https://www.swisswatchexpo.com/watches/rolex/oyster-perpetual/',
    'oysterquartz': 'https://www.swisswatchexpo.com/watches/rolex/oysterquartz/',
    'president': 'https://www.swisswatchexpo.com/watches/rolex/president/',
    'sea_dweller': 'https://www.swisswatchexpo.com/watches/rolex/seadweller/',
    'submariner': 'https://www.swisswatchexpo.com/watches/rolex/submariner/',
    'turn_o_graph': 'https://www.swisswatchexpo.com/watches/rolex/turn-o-graph/',
    'yacht_master': 'https://www.swisswatchexpo.com/watches/rolex/yachtmaster/',
}

VALID_LABELS = set(SWISSWATCHEXPO_URLS.keys())

@dataclass(frozen = True)
class ImageCandidate:
    label: str 
    source_name: str 
    listing_title: str 
    listing_url: str
    image_url: str

class SourceAdapter (Protocol): 
    source_name: str 

    def collect (self, label: str, limit: int): 
        
        return 

def validate_label (label: str): 
    if label not in VALID_LABELS: 
        raise ValueError(f'Label not known: {label}')
    
def parse_product_images (
    html:str,
    page_url: str, 
    label: str, 
    source_name: str, 
    product_selector: str, 
): 
    
    validate_label (label) 
    soup = BeautifulSoup (html, 'html.parser')
    page_title = soup.title.string.strip() if soup.title and soup.title.string else page_url
    candidates: list[ImageCandidate] = []

    for product in soup.select (product_selector): 
        image = product.find ('img')
        if image is None: 
            continue
        raw_image_url = image.get ('src') or image.get ('data-src')
        if not raw_image_url: 
            continue

        link = product.find ('a', href = True)
        listing_url = urljoin (page_url, link['href']) if link else page_url

        candidates.append (
            ImageCandidate(
                label = label, 
                source_name=source_name,
                listing_title=image.get('alt') or page_title,
                listing_url=listing_url,
                image_url=urljoin(page_url, raw_image_url)
            )
        )

    return candidates

def parse_next_page_url(html: str, page_url: str, current_page: int) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    page_links: list[tuple[int, str]] = []

    for link in soup.find_all("a", href=True):
        onclick = link.get("onclick") or ""
        match = re.search(r"changeCurrentPage\((\d+)\)", onclick)
        if not match:
            continue

        page_number = int(match.group(1))
        if page_number > current_page:
            page_links.append((page_number, urljoin(page_url, link["href"])))

    if not page_links:
        return None

    page_links.sort(key=lambda item: item[0])
    return page_links[0][1]

@dataclass(frozen=True)
class SwissWatchExpoSource:
    source_name = 'swisswatchexpo'
    timeout_seconds = 20
    max_pages = 100000

    def collect (self, label: str, limit: int): 
        validate_label(label)
        candidates = []
        next_url = SWISSWATCHEXPO_URLS[label]
        visited_urls = set()
        pages_fetched = 0
        current_page = 1

        while next_url and len(candidates) < limit and pages_fetched < self.max_pages:
            if next_url in visited_urls:
                break 

            visited_urls.add (next_url)
            response = requests.get(
                next_url,
                timeout = self.timeout_seconds,
                headers={'User-Agent': 'Webscraper/0.1'}
            )
            response.raise_for_status()
            pages_fetched += 1

            candidates.extend (
                parse_product_images(
                    html = response.text,
                    page_url = next_url,
                    label = label,
                    source_name=self.source_name,
                    product_selector='.product_box.catalog'
                )
            )
            next_url = parse_next_page_url(
                html = response.text,
                page_url = next_url,
                current_page = current_page,
            )
            current_page += 1
        return candidates[:limit]

def get_source (source_name: str):
    if source_name == 'swisswatchexpo':
        return SwissWatchExpoSource()
    raise ValueError(f'Source unknown: {source_name}')
