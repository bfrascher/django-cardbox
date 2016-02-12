import requests

from bs4 import BeautifulSoup

from cardbox.models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
)

# Test cards are:
# ---
# http://magiccards.info/ori/en/60a.html
# http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=398434
# ---
# http://magiccards.info/dgm/en/121a.html
# http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=369041
# ---
# http://magiccards.info/dka/en/81a.html
# http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=262675
# ---
# http://magiccards.info/shm/en/28.html
# http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=154408
# ---
# http://magiccards.info/mm2/en/79.html
# http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=397830


class MTGBlockSetParser:
    class MagicCardsOnlineEngine:
        @staticmethod
        def _get_category(heading):
            category = heading.text
            if category == 'Expansions':
                return MTGBlock.CATEGORY_EXPANSION
            if category == 'Core Sets':
                return MTGBlock.CATEGORY_CORE_SET
            if category == 'MTGO':
                return MTGBlock.CATEGORY_MTGO
            if category == 'Special Sets':
                return MTGBlock.CATEGORY_SPECIAL_SET
            if category == 'Promo Cards':
                return MTGBlock.CATEGORY_PROMO_CARD
            return ''

        @staticmethod
        def _parse_sets(ul, block):
            sets = []
            for li in ul.find_all('li', recursive=False):
                name = li.a.string
                code = li.small.string.upper()
                mtgset = MTGSet(name=name, code=code, block=block)
                sets.append(mtgset)

            return sets

        @staticmethod
        def _parse_blockset(ul, category):
            for li in ul.find_all('li', recursive=False):
                block = MTGBlock(name=li.contents[0], category=category)
                sets = MTGBlockSetParser.MagicCardsOnlineEngine._parse_sets(
                    li.ul, block)
                yield block, sets


        @staticmethod
        def parse(base_url='http://magiccards.info/sitemap.html', lang='en'):
            html = requests.get(base_url).text
            soup = BeautifulSoup(html, 'html.parser')
            engine = MTGBlockSetParser.MagicCardsOnlineEngine
            for h2 in soup.find_all('h2'):
                if h2.small.text == lang:
                    blockset_table = h2.find_next('table')

            for td in blockset_table.find_all('td'):
                for h3 in td.find_all('h3'):
                    category = engine._get_category(h3)
                    yield from engine._parse_blockset(
                        h3.find_next('ul'), category)

    @staticmethod
    def parse(base_url='http://magiccards.info/sitemap.html', lang='en'):
        yield from MTGBlockSetParser.MagicCardsOnlineEngine.parse(
            base_url=base_url, lang=lang)


class MTGCardParser:
    def __init__(self, base_url='', lang='en'):
        pass

    def parse(self):
        pass


class MTGTokenParser:
    def __init__(self, base_url='', lang='en'):
        pass

    def parse(self):
        pass
