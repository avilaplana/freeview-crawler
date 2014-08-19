#!/usr/local/bin/python


import unittest
import urllib2
from tvContentParser import parseToTVContent
from datetime import datetime

class TestTvChannelParser(unittest.TestCase):

    def test_shuffle(self):

        tv_content_channel_url = 'http://tvlistings.theguardian.com/text-only/?c=bbc-3'
        tv_content_channel_html_loaded = urllib2.urlopen(tv_content_channel_url).read()
        tv_content_channel_documents = parseToTVContent("Channel 4", tv_content_channel_html_loaded)
        for document in tv_content_channel_documents:
            print "Testing content parsing" + str(document)
            self.assertTrue(document["channel"] is not "", "channel name does not exist")

            if "flags" in document:
                self.assertTrue(document["flags"] is not "", "flags is empty")
            self.assertTrue(document["category"] is not "", "category does not exist")
            self.assertTrue(type(document["startTime"]) is datetime)
            self.assertTrue(type(document["endTime"]) is datetime)
            if "program" in document:
                self.assertTrue(document['program']['title'] is not "", "title is empty")
                self.assertTrue(document['program']["description"] is not "", "description does not exist")
            if "serie" in document:
                self.assertTrue(document['serie']['serieTitle'] is not "", "serieTitle is empty")
                self.assertTrue(document['serie']["description"] is not "", "description does not exist")
                if "seasonNumber" in document['serie']:
                    self.assertTrue(document['serie']['seasonNumber'] is not "", "seasonNumber is empty")
                if "episodeNumber" in document['serie']:
                    self.assertTrue(document['serie']['episodeNumber'] is not "", "episoeNumber is empty")
                if "totalNumber" in document['serie']:
                    self.assertTrue(document['serie']['totalNumber'] is not "", "totalNumber is empty")

                self.assertTrue(document['serie']['episodeTitle'] is not "", "episodeTitle is empty")


if __name__ == '__main__':
    unittest.main()