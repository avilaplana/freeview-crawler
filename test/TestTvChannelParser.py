#!/usr/local/bin/python

import unittest
import urllib2
from tvChannelParser import parseToTVChannels

class TestTvChannelParser(unittest.TestCase):

    def test_shuffle(self):
        tv_channels_url = 'http://tvlistings.theguardian.com/text-only'
        channels_html_loaded = urllib2.urlopen(tv_channels_url).read()
        list_channels = parseToTVChannels(channels_html_loaded)
        for channel in list_channels:
            print "Testing channel parsing" + str(channel.channel_document)
            self.assertTrue(channel.channel_document["name"] is not "", "name in channel does not exist")
            self.assertTrue(channel.channel_document["language"] is not "", "language in channel does not exist")
            self.assertTrue("/?c=" in channel.query_parameter, "query parameter does not exist")

if __name__ == '__main__':
    unittest.main()