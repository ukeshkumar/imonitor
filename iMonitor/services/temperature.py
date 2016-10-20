import pika
import threading
import json
import logging

import iMonitor.messages as messages

"""
    Class to handle Service Temperature
"""
class Temperature(threading.Thread):
    def __init__(self, dbObj, *args, **kwargs):
        super(Temperature, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger("iMonitor.services.Temperature")
        self._db = dbObj
        self.start()


    def callback_func(self, channel, method, properties, body):
#        print("{} received '{}'".format(self.name, body))
        self.logger.info("Temperature info received from Q")
        data = json.loads(body)
        data['status'] = self.checkThreshold(data)
        self._db.insertTemperature(data)
        channel.basic_ack(delivery_tag = method.delivery_tag)


    def run(self):
        self.logger.info("Starting listioning thread for temperature update")
        exchange_name = 'myexchange'
        queue_name = 'temperature_q'
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()

        # to purge messages in the queue
        channel.queue_delete(queue=queue_name)
        channel.exchange_declare(exchange=exchange_name, type='direct')
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name,
                           queue=queue_name,
                           routing_key='temperature')
        channel.basic_consume(self.callback_func,
                              queue=queue_name)
        print "started..."
        channel.start_consuming()
        

    def checkThreshold(self, data):
        retVal = 0
        res = self._db.getDeviceDetails(data['uuid'])
        if res[1] == 200:
            temp = float(data['temp'])
            minThreshold = float(res[0][0][7])
            maxThreshold = float(res[0][0][8])
            if minThreshold != 0 and maxThreshold != 0 and (temp > maxThreshold or temp < minThreshold):
                retVal = 1

                self.logger.error("Temperature threshold reached for %s in %s", res[0][0][0], res[0][0][3])
                print "reached threshold"
                # check whether to send email
                if res[0][0][10] == "Enable":
                    htmlmessage = """\
                       <table BORDER=3 BORDERCOLOR="#d6d6c2">
                         <tr>
                           <th> <B> Device-Name </B></th>
                           <th> <B> Location </B></th>
                           <th> <B> Temperature (&deg;C) </B> </th>
                           <th> <B> Humidity (%%) </B> </th>
                         </tr>
                         <tr>
                           <td> %s </td>
                           <td> %s </td>
                           <td> %.2f </td>
                           <td> %.2f </td>
                         </tr>
                         <tr>
                           <td colspan="4"> Note: temperature (min / max) threshold is (%.2f&deg;C, %.2f&deg;C) </td>
                         </tr>
                    """ % (res[0][0][0], res[0][0][3], temp, float(data['hum']), minThreshold, maxThreshold)

                    self.sendEmail(res[0][0][11], htmlmessage)

                # check whether to send sms
                if res[0][0][12] == "Enable":
                    self.sendSms(res[0][0][13], "%s in %s reached threshold. Current temp: %.2fC" % (res[0][0][0], res[0][0][3], temp))
        return retVal


    def sendSms(self, numbers, message):
        # to get username, password for way2sms provider
        res = self._db.getSmsSettings()
        if res[1] == 200:
            messages.sms(res[0][0][0], res[0][0][1]).sendMany(numbers, message)


    def sendEmail(self, emailIds, message):
        # to get info to send email
        res = self._db.getEmailSettings()
        if res[1] == 200:
            messages.email(res[0][0][0], res[0][0][1], res[0][0][2], res[0][0][3]).sendMany(emailIds, message)


class deviceMonitor(threading.Thread):

    def __init__(self, dbObj, *args, **kwargs):
        super(Temperature, self).__init__(*args, **kwargs)
        self._db = dbObj
        self.start()

        
    def run(self):
        pass 



if __name__ == "__main__":
    obj1=Temperature(None)

    data = """{
  "uuid":"device1",
  "date": "2016-10-12",
  "time": "18:37:46",
  "temp": "15.3",
  "hum": "20"
}"""
    import time
    time.sleep(1)

    print "data : " + data
    exchange_name = 'myexchange'
    queue_name = 'temperature_q'
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    channel.basic_publish(exchange='myexchange',
                  routing_key='temperature',
                  body=data)
    connection.close()
    print "added to q"

