# coding: utf-8

import datetime
import re
import requests

from bs4 import BeautifulSoup

from cardbox.models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGCardEdition,
)


class MTGBlockSetParser:
    class MCIEngine:
        """magiccards.info engine"""
        URL = 'http://magiccards.info/sitemap.html'

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
                sets = MTGBlockSetParser.MCIEngine._parse_sets(
                    li.ul, block)
                yield block, sets

        @staticmethod
        def parse(lang='en'):
            engine = MTGBlockSetParser.MCIEngine
            html = requests.get(engine.URL).text
            soup = BeautifulSoup(html, 'html.parser')
            for h2 in soup.find_all('h2'):
                if h2.small.text == lang:
                    blockset_table = h2.find_next('table')

            for td in blockset_table.find_all('td'):
                for h3 in td.find_all('h3'):
                    category = engine._get_category(h3)
                    yield from engine._parse_blockset(
                        h3.find_next('ul'), category)

    @staticmethod
    def parse(lang='en'):
        yield from MTGBlockSetParser.MCIEngine.parse(lang)


class MTGCardParser:
    class MCIEngine:
        """magiccards.info engine"""
        URL = 'http://magiccards.info'

        @staticmethod
        def _parse_types_stats(p):
            """Parse type, power, toughness, loyalty, mana and cmc.

            magiccards.info has a continuous text entry that includes
            all of the above mentioned stats in plain text.  The text
            has the following structure:

               <supertype> [— <subtypes>] ([<power>/<toughness>] | [(Loyalty: <loyalty)]), <mana> (<cmc>)

            All these information are extracted via regular
            expressions and then returned.

            """
            text = ' '.join(p.stripped_strings)
            regex_types = re.compile(r'\A[a-zA-Z—\- ]+')
            regex_pt = re.compile(r'([\d*+]+)/([\d*+]+)')
            regex_loyalty = re.compile(r'\(Loyalty: ([\d*+]+)\)')
            regex_mana = re.compile(r'\s[\dWUBRGCPX*{}/]+(\s|\Z)')
            regex_cmc = re.compile(r'\((\d+)\)')

            match = regex_types.search(text)
            types = match.group(0).strip()
            end = match.end()

            match = regex_pt.search(text[end:])
            power = match.group(1).strip() if match else None
            toughness = match.group(2).strip() if match else None
            if match:
                end += match.end()

            match = regex_loyalty.search(text[end:])
            loyalty = match.group(1).strip() if match else None
            if match:
                end += match.end()

            match = regex_mana.search(text[end:])
            mana = match.group(0).strip() if match else None
            if match:
                end += match.end()

            match_cmc = regex_cmc.search(text[end:])
            cmc = int(match_cmc.group(1)) if match_cmc else None

            return types, power, toughness, loyalty, mana, cmc

        @staticmethod
        def _parse_rulings(ul):
            """Return all rulings in the list.

            Each ruling is a ``li`` in the given ``ul`` and has the
            format:

               <b><date></b>: <ruling>
            """
            rulings = []
            for li in ul.find_all('li', recursive=False):
                parts = ' '.join(li.stripped_strings).split(':', maxsplit=1)
                month, day, year = parts[0].split('/')
                ruling = parts[1].strip()
                rulings.append(
                    MTGRuling(date=datetime.date(int(year),
                                                 int(month),
                                                 int(day)),
                              ruling=ruling))

            return rulings

        @staticmethod
        def _parse_legals(ul):
            """Parse the legal statuses in the list.

            Each list entry ``li`` has the following structure:

               <li class="(legal|banned|restriced)">(Legal|Banned|Restricted) in <format></li>

            In case the card isn't legal in any format the list has only one entry:

               <li class="banned">This card is not legal in any format</li>

            The parsed legal statuses are returned in a otherwise
            empty class:`cardbox.models.MTGCard` object.

            """
            card = MTGCard()
            legality = {}
            legality['Legal'] = MTGCard.LEGALITY_LEGAL
            legality['Restricted'] = MTGCard.LEGALITY_RESTRICTED
            legality['Banned'] = MTGCard.LEGALITY_BANNED
            for li in ul.find_all('li'):
                if li.text == "This card is not legal in any format":
                    break
                words = li.text.split(' ')
                if 'Vintage' == words[2]:
                    card.legal_vintage = legality[words[0]]
                elif 'Legacy' == words[2]:
                    card.legal_legacy = legality[words[0]]
                elif 'Extended' == words[2]:
                    card.legal_extended = legality[words[0]]
                elif 'Standard' == words[2]:
                    card.legal_standard = legality[words[0]]
                elif 'Classic' == words[2]:
                    card.legal_classic = legality[words[0]]
                elif 'Commander' == words[2]:
                    card.legal_commander = legality[words[0]]
                elif 'Modern' == words[2]:
                    card.legal_modern = legality[words[0]]
                # TODO(benedikt) Define else case

            return card

        @staticmethod
        def _parse_artist(p):
            """Return the artist in the paragraph.

            The format of the artist in the paragraph is:

               Illus. <artist name>

            It is assumed that the artist has only one last name.  All
            other parts of his name are considered to be first names.
            This assumption doesn't have much of an impact, as the
            name parts are almost always displayed together anyways.

            """
            split_artist = p.text.split(' ')
            # The first entry will always be 'Illus.'.  We assume that
            # every artist has only one last name.  This isn't a
            # problem since first and last name are always shown
            # together.
            return Artist(first_name=' '.join(split_artist[1:-1]),
                          last_name=split_artist[-1])

        @staticmethod
        def _parse_dual_type(name):
            # Every split card has it's name repeated in parentheses
            # (along with the names of it's other parts).
            if '(' in name:
                regex = re.compile(r'(.*) \(.*?/?\1/?.*?\)')
                if regex.search(name) is not None:
                    return MTGCard.DUAL_SPLIT
            return MTGCard.DUAL_FLIP

        @staticmethod
        def parse_card(setcode, number, card=None, lang='en'):
            """Parse a card from it's detail page on magiccards.info.

            Returns a :class:`cardbox.models.MTGCard` object that is
            partially filled (rarity and foreign keys are missing) as
            well as the artist, the dual card (if any) and all rulings
            (if any).

            """
            engine = MTGCardParser.MCIEngine
            if card is None:
                card = MTGCard()

            html = requests.get('{0}/{1}/{2}/{3}.html'.format(
                engine.URL, setcode, lang, number)).text
            soup = BeautifulSoup(html, 'html.parser')

            a_multiverseid = soup.find('a', {'href': re.compile(r'.*\?multiverseid=.*')})
            multiverseid = re.search(r'=(\d+)\Z',
                                     a_multiverseid.attrs['href']).group(1)
            card.multiverseid = int(multiverseid) if multiverseid else None

            a_name = soup.find('a', {'href':'/{0}/{1}/{2}.html'
                                     .format(setcode, lang, number)})
            card.name = a_name.text

            p_types_stats = a_name.find_next('p')
            types, power, toughness, loyalty, mana, cmc = engine._parse_types_stats(p_types_stats)
            card.types = types.strip()
            card.set_power(power)
            card.set_toughness(toughness)
            card.set_loyalty(loyalty)
            card.set_mana(mana)
            card.cmc = cmc

            p_rules = soup.find('p', {'class':'ctext'})
            card.rules = '\n\n'.join(p_rules.b.stripped_strings)

            p_flavour = p_rules.find_next_sibling('p')
            card.flavour = '\n'.join(p_flavour.stripped_strings)

            p_artist = soup.find('p', text=re.compile(r'\AIllus\.'))
            artist = engine._parse_artist(p_artist)

            ul_rulings = p_flavour.find_next_sibling('ul')
            if ul_rulings.li.attrs.get('class', '') != '':
                rulings = []
                ul_legal = ul_rulings
            else:
                rulings = engine._parse_rulings(ul_rulings)
                ul_legal = ul_rulings.find_next_sibling('ul')

            legal_card = engine._parse_legals(ul_legal)
            card.legal_vintage = legal_card.legal_vintage
            card.legal_legacy = legal_card.legal_legacy
            card.legal_extended = legal_card.legal_extended
            card.legal_standard = legal_card.legal_standard
            card.legal_classic = legal_card.legal_classic
            card.legal_commander = legal_card.legal_commander
            card.legal_modern = legal_card.legal_modern

            b_dual = soup.find('b', text='The other part is:')
            # Only the 'a' part of a dual card should return it's
            # other part.  Otherwise they would try to find their
            # other part infinitely.
            if b_dual:
                card.dual_type = engine._parse_dual_type(card.name)
                if number[-1] == 'a':
                    dual_card, _, _, _ = engine.parse_card(
                        setcode, number.replace('a', 'b'), lang=lang)
                else:
                    dual_card = None
            else:
                dual_card = None

            return card, dual_card, artist, rulings

        @staticmethod
        def _parse_rarity(rarity_str):
            # We don't need to check for RARITY_NONE here.
            for (rarity_code, rarity_full) in MTGCard.RARITIES[1:]:
                if rarity_str == rarity_full:
                    return rarity_code
            return MTGCard.RARITY_NONE

        @staticmethod
        def parse_set(setcode, lang='en'):
            """Parse all cards in a set.

            Each card will be yielded along with it's edition,
            dual_card (if any), artist and all rulings (if any).

            """
            engine = MTGCardParser.MCIEngine
            url = '{0}/{1}/{2}.html'.format(engine.URL, setcode, lang)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            table = soup.find('table', {'cellpadding': '3'})
            # Skip the first entry since it only declares the headers.
            for tr in table.find_all('tr')[1:]:
                card = MTGCard()
                tds = tr.find_all('td')
                number_str = tds[0].text
                number, number_suffix = MTGCardEdition.parse_number(number_str)
                # Skip other parts of dual cards, since they have
                # already been parsed in the previous iteration,
                # together with it's 'a' part.
                if not number_suffix in ['', 'a']:
                    continue
                edition = MTGCardEdition(number=number,
                                         number_suffix=number_suffix)
                card.rarity = engine._parse_rarity(tds[4].text)
                card, dual_card, artist, rulings = engine.parse_card(
                    setcode, number_str, card=card, lang=lang)
                if dual_card is not None:
                    dual_edition = MTGCardEdition(number=number,
                                                  number_suffix='b')
                else:
                    dual_edition = None
                yield edition, card, dual_edition, dual_card, artist, rulings


class MTGTokenParser:
    def __init__(self, base_url='', lang='en'):
        pass

    def parse(self):
        pass
