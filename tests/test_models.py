import pytest

from cardbox.models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGCardEdition,
    MTGCollection,
    MTGCollectionEntry,
)


class TestMTGCard:
    @pytest.mark.parametrize("mana,mana_n,mana_w,mana_u,mana_b,mana_r,mana_g,mana_c,mana_special", [
        ('10RG', 10, None, None, None, 1, 1, None, ''),
        ('UWWGgg', None, 2, 1, None, None, 3, None, ''),
        ('3XCCBW', 3, 1, None, 1, None, None, 2, 'X'),
        ('{BP}{2/W}2U', 2, None, 1, None, None, None, None, '{BP}{2/W}'),
    ])
    def test_parse_mana(self, mana, mana_n, mana_w, mana_u, mana_b,
                        mana_r, mana_g, mana_c, mana_special):
        n, w, u, b, r, g, c, special = MTGCard.parse_mana(mana)
        print(n, w, u, b, r, g, c, special)
        assert (mana_n == n) if mana_n else (n is None)
        assert (mana_w == w) if mana_w else (w is None)
        assert (mana_u == u) if mana_u else (u is None)
        assert (mana_b == b) if mana_b else (b is None)
        assert (mana_r == r) if mana_r else (r is None)
        assert (mana_g == g) if mana_g else (g is None)
        assert (mana_c == c) if mana_c else (c is None)
        assert mana_special == special
