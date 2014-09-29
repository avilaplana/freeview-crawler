#!/usr/local/bin/python

import unittest
import urllib2
from tvContentGenreParser import parseToContentGenre

class TestTtvChannelGenreParser(unittest.TestCase):

    def test_shuffle(self):
        all_tv_content = [{"category": ["FILM", "HORROR"]}, {"category": ["DOCUMENTARY"]}, {"category": ["NEWS"]}, {"category": ["SPORT"]}]
        list_genres_channels = parseToContentGenre(all_tv_content)
        result_expected = set(["FILM", "HORROR", "DOCUMENTARY", "NEWS", "SPORT"])
        self.assertSetEqual(list_genres_channels, result_expected, "The sets of categories are not equals")

if __name__ == '__main__':
    unittest.main()