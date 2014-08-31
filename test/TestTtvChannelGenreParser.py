#!/usr/local/bin/python

import unittest
import urllib2
from tvChannelGenreParser import parseToChannelGenre

class TestTvChannelParser(unittest.TestCase):

    def test_shuffle(self):
        list_categories = ['KIDS','SHOPPING','ENTERTAINMENT','DOCUMENTARIES','ALL CHANNELS','MOVIES','LIFESTYLE & CULTURE','MUSIC','RELIGION','NEWS','INTERNATIONAL','SPORTS']
        tv_listing_url = 'http://tvlistings.theguardian.com/'
        tv_listing_html_loaded = urllib2.urlopen(tv_listing_url).read()
        list_genres_channels = parseToChannelGenre(tv_listing_html_loaded)
        for genre in list_genres_channels:
            self.assertTrue(genre in list_categories, "genre " + genre + " no in the list")
            self.assertTrue(len(list_genres_channels[genre]) > 0, "genre " + genre + " with no channels")

if __name__ == '__main__':
    unittest.main()