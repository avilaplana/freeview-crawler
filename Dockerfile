FROM python:2.7-slim

ADD *.py /root/
ADD crawler.sh /root/crawler.sh

RUN apt-get update
RUN apt-get install -y python-pip
RUN apt-get install -y build-essential python-dev
RUN pip install pymongo
RUN pip install beautifulsoup4
RUN pip install pytz

