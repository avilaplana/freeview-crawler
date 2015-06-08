FROM python:2.7-slim

ADD *.py /

ADD *.sh /

RUN apt-get update && apt-get install -y \
	python-pip \
	build-essential \ 
	python-dev \
	cron

RUN pip install \
	pymongo \
	beautifulsoup4 \
	pytz \
	numpy

RUN touch /etc/cron.d/hello-cron

RUN chmod 0644 /etc/cron.d/hello-cron
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD /crawler.sh  && /run_cron.sh && cron -f

