import ConfigParser
import json
import logging
import pika
import os

import db as db
from services.temperature import Temperature


class controller: 
    def __init__(self,):
        try:
            self.logger = logging.getLogger("iMonitor.controller")
            config = ConfigParser.RawConfigParser()
            config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.cfg')
            self.db_host = config.get('database', 'host')
            self.db_username = config.get('database', 'username')
            self.db_password = config.get('database', 'password')
            self.db_database = config.get('database', 'database')
        except Exception as err:
            self.logger.error("Error while creating controllr obj: %s", str(err))
            print "Error while creating controllr obj: %s" % str(err)
            exit(1)

        self.dbConnector = db.Connector(host=self.db_host, user=self.db_username, password=self.db_password, database=self.db_database)
        self.temperature = Temperature(self.dbConnector)


    def registerDevice(self, data):
#        print "\tdata : " + str(data)
        return self.dbConnector.registerDevice(data)


    def createTemperatureEntry(self, data):
#        print "\tdata : " + str(data)
        retVal = (json.dumps({'status':'ok'}), 202)
        exchange_name = 'myexchange'
        queue_name = 'temperature_q'
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()
        channel.basic_publish(exchange='myexchange',
                      routing_key='temperature',
                      body=json.dumps(data))
        connection.close()
        self.logger.info("Added temperature request to Q")

        # check for changeflag in devices, if enabled, reply updated data
        res = self.dbConnector.checkChangeFlagForDevice(data['uuid'])
        if(res[1] == 200):
            retVal = (res[0], 202)

        return retVal

