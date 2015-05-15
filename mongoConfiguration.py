#!/usr/bin/env python
import os


def load_mongo_configuration():
	mongo_address='localhost'
	mongo_port=27017

	if "MONGO_PORT_27017_TCP_ADDR" in os.environ:
		mongo_address=os.environ["MONGO_PORT_27017_TCP_ADDR"]

	if "MONGO_PORT_27017_TCP_PORT" in os.environ:
		mongo_port=int(os.environ["MONGO_PORT_27017_TCP_PORT"])

	return (mongo_address, mongo_port)


