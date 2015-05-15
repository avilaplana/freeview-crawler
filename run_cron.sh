echo 'PATH=/usr/local/bin:'$PATH >> /etc/cron.d/hello-cron
echo 'MONGO_PORT_27017_TCP_ADDR'=$MONGO_PORT_27017_TCP_ADDR >> /etc/cron.d/hello-cron
echo 'MONGO_PORT_27017_TCP_PORT'=$MONGO_PORT_27017_TCP_PORT >> /etc/cron.d/hello-cron
echo '0 1 * * * root /crawler.sh >> /var/log/cron.log  2>&1' >> /etc/cron.d/hello-cron
