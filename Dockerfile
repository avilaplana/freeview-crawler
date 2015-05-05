FROM python:2.7-slim

ADD *.py /root/
ADD crawler.sh /root/crawler.sh

RUN apt-get update
RUN apt-get install -y python-pip
RUN apt-get install -y build-essential python-dev
RUN pip install pymongo
RUN pip install beautifulsoup4
RUN pip install pytz
RUN pip install numpy


RUN apt-get install -y cron

# Add crontab file in the cron directory
ADD crontab /etc/cron.d/hello-cron
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/hello-cron
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD /root/crawler.sh && cron && tail -f /var/log/cron.log 

