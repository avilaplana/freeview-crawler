#!/usr/local/bin/python

import urllib2
from tvContentParser import parseToTVContent
from tvChannelParser import parseToTVChannels
from tvChannelGenreParser import parseToChannelGenre
from tvContentGenreParser import parseToContentGenre
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['freeview']
channelCollection = db['tvChannel']
channelCollection.drop()

genreChannelCollection = db['tvChannelGenre']
genreChannelCollection.drop()

contentCollection = db['tvContent']
contentCollection.drop()

genreContentCollection = db['tvContentGenre']
genreContentCollection.drop()



def findContent(year, month, day, time_to_search = '12am', tabName = 'All'):
    date_to_search = str(year) + '-' + str(month) + '-' + str(day)
    telegraph_url = 'http://tvguideuk.telegraph.co.uk/grid.php?&day=' + date_to_search + '&oclock='+ time_to_search + '&tabname=' + tabName
    all = urllib2.urlopen(telegraph_url).read()


    soup = BeautifulSoup(all)
    slots = soup.findAll("div", { "class" : "channel" })

    for slot in slots:
        print "Channel: " +  slot.find("div", { "class" : "channel_name" }).text
        programs = slot.findAll("div", { "class" : "programme " })

        for program in programs:
            import re

            from datetime import datetime
            m = re.search('<div class=\'prog_pre_header\'>(.+?)</div>', program['onmouseover'].replace('\\', ''))
            start = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + m.group(1).split('-')[0]
            end = str(month) + ' ' + str(day) + ' ' + str(year) + ' ' + m.group(1).split('-')[1]
            # print start
            # print end
            print str(datetime.strptime( start, '%m %d %Y %I.%M%p'))
            print str(datetime.strptime( end, '%m %d %Y %I.%M%p'))
            # print m.group(1).split('-')[0] + " " + m.group(1).split('-')[1]

            m = re.search('<div class=\'prog_header\'>(.+?)</div>', program['onmouseover'].replace('\\', ''))
            match = m.group(1)
            if 'FILM: ' in (match):
                print 'FILM: ----> ' + match
            else:
                if 'Ana Matronic' in (match):
                    print match
                else: print match

            m = re.search('<div class=\'prog_pre_content\'>(.+?)</div>', program['onmouseover'].replace('\\', ''))
            match = m.group(1)
            if ('Episode' in match and 'Series' in match):
                if '<br>' in match:
                    # u'American Killer Catfish<br>Series 4 - Episode 2 of 10<br /><br /> Jeremy Wade visits tourist hot'
                    name = match.split('<br /><br /> ')[0].split('<br>')[0]
                    serie = match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[0].split('Series ')[1]
                    print 'SERIES: ----> serie:' + name
                    print 'SERIES: ----> serie:' + serie
                    if 'of' in match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[1]:
                        episode = match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[1].split(' of ')[0]
                        total = match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[1].split(' of ')[1]
                        print 'SERIES: ----> total:' + total
                    else:
                        episode = match.split('<br /><br /> ')[0].split('<br>')[1].split('- Episode ')[1].split(' of ')[0]

                    print 'SERIES: ----> episode:' + episode


                else: print 'SERIES: ----> ' + match.split('<br /><br /> ')[0]

                print 'SERIES: ----> ' + match.split('<br /><br /> ')[1]

            else:
                print  "aaa " + match
                a  = re.findall('\. Starring.*',match)
                if len(a) > 0:
                    print re.sub('\. Starring.*', '', match)
                    print a[0].split('\. Starring ')[0]
                b = re.findall('\..*, starring.*',match)
                if len(b) > 0:
                    print re.sub('\..*, starring.*', '', match)
                    print b[0].split(' starring ')[0]
                    print b[0].split(' starring ')[1]





from datetime import datetime

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year

hours = ['12am','2am','4am','6am','8am','10am','12pm','2pm','4pm','6pm','8pm','10pm']
# findContent(year, month, day,'8pm')
for hour in hours:
    print "------------------------" + hour
    findContent(year, month, day,hour)




#
# tv_listing_url = 'http://tvlistings.theguardian.com/'
# tv_listing_html_loaded = urllib2.urlopen(tv_listing_url).read()
#
# tv_channels_url = 'http://tvlistings.theguardian.com/text-only'
# channels_html_loaded = urllib2.urlopen(tv_channels_url).read()
# genre_channel_list = parseToChannelGenre(tv_listing_html_loaded)
# list_channels = parseToTVChannels(channels_html_loaded, genre_channel_list)
# all_tv_content_genres = set()
# for channel in list_channels:
#     channel_document = channel.channel_document
#     # print channel_document
#     channelCollection.insert(channel_document)
#     tv_channel_content_url = tv_channels_url + channel.query_parameter
#     channel_information = urllib2.urlopen(tv_channel_content_url).read()
#     tv_content_documents = parseToTVContent(channel_document['name'], channel_information)
#     for tv_content_document in tv_content_documents:
#         # print tv_content_document
#         contentCollection.insert(tv_content_document)
#     tv_content_genres_channel = parseToContentGenre(tv_content_documents)
#     all_tv_content_genres = all_tv_content_genres.union(tv_content_genres_channel)
#
# for genre_channel in genre_channel_list.keys():
#      genre_channel_dict = {}
#      genre_channel_dict['genre'] = genre_channel
#      genreChannelCollection.insert(genre_channel_dict)
#
# for genre_content in all_tv_content_genres:
#      genre_content_dict = {}
#      genre_content_dict['genre'] = genre_content
#      genreContentCollection.insert(genre_content_dict)
#
#
#











