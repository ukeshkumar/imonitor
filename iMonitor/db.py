import json
import logging
import mysql.connector
from datetime import datetime

"""
    Class to handle Service Temperature
"""
class Connector():
#    user = 'root'
#    password='root123'
#    host='127.0.0.1'
#    database='imonitor'


#    def __init__ (self, user='root', password='root123', host='127.0.0.1', database='imonitor'):
    def __init__ (self, user=None, password=None, host=None, database=None):
        self.logger = logging.getLogger("iMonitor.db.Connector")
        if not(user and password and host and database):
            self.logger.error("username/password/host/database not provided")
            exit(1)
        self.user = user
        self.password = password
        self.host = host
        self.database = database


    def isDeviceExist(self, uuid):
        retVal = ("Not Found", 404)
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
            cursor = cnx.cursor()
            select_query = "select * from devices where uuid = '%s'" % (uuid)
            cursor.execute(select_query)
            res = cursor.fetchall()
            if res:
                retVal = ("Device found", 302)

            cursor.close()
            cnx.close()
            return retVal
        except mysql.connector.Error as err:
            self.logger.error("DB Error: %s", str(err))
            return (err, 500)


    def executeSelectQuery(self, selectQuery):
        retVal = ("Not Found", 404)
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
            cursor = cnx.cursor()
            cursor.execute(selectQuery)
            res = cursor.fetchall()
            if res:
                retVal = (res, 200)

            cursor.close()
            cnx.close()
            return retVal
        except mysql.connector.Error as err:
            self.logger.error("DB Error: %s", str(err))
            return (err, 500)


    def insertRowToDb(self, insertQuery):
        retVal = ("Error", 500)
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
            cursor = cnx.cursor()
            res = cursor.execute(insertQuery)
            if cursor.rowcount == 1:
                retVal = ("Successfully Inserted", 200)
            cnx.commit()
            cursor.close()
            cnx.close()
            return retVal
        except mysql.connector.Error as err:
            self.logger.error("DB Error: %s", str(err))
            return (err, 500)


    def updateDevice(self, updateData, uuid = None, mac = None):
        retVal = ("Not Found", 404)
        try:
            cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
            cursor = cnx.cursor()
            if uuid:
                updateQuery = "update devices set %s where uuid = '%s'" % (updateData, uuid)
            elif mac:
                updateQuery = "update devices set %s where mac = '%s'" % (updateData, mac)
            else:
                return retVal

            cursor.execute(updateQuery)
            cnx.commit()
            if cursor.rowcount:
                retVal = ("Successfully updated", 200)

            cursor.close()
            cnx.close()
            return retVal
        except mysql.connector.Error as err:
            self.logger.error("DB Error: %s", str(err))
            return (err, 500)


    def registerDevice(self, data):
        retVal = ("Unauthorized", 401)
        selectQuery = "select uuid, mac, type, location, pollinterval, apiusername, apipassword from devices where mac = '%s'" % (data['mac'])
        res = self.executeSelectQuery(selectQuery)
        if res[1] == 200:
            info = { 'uuid' : res[0][0][0], 'mac' : res[0][0][1], 'type' : res[0][0][2], 
                     'location' : res[0][0][3], 'pollinterval' : res[0][0][4], 
                     'apiusername' : res[0][0][5], 'apipassword' : res[0][0][6]
                   }
            retVal = (json.dumps(info), 200)

            # change the device status to 'Active'
            self.updateDevice("status = 'Active'", mac = data['mac'])
            self.logger.info("Registered new device (%s) and changed status to Active", res[0][0][0])
            return retVal

        selectQuery = "select mac, type, location from unauthdevices where mac = '%s'" % (data['mac'])
        res = self.executeSelectQuery(selectQuery)
        if res[1] == 200:
            self.logger.info("Device (mac: %s) already in unauthdevices", data['mac'])
            return retVal

        # add mac, location to unauthdevices return data with 401 code
        insertQuery = "insert into unauthdevices (mac, type, location, timestamp) values ('%s', '%s', '%s', '%s')" % (data['mac'], data['type'], data['location'], str(datetime.utcnow())) 
        res = self.insertRowToDb(insertQuery)
        self.logger.info("Device (mac: %s) added to unauthdevices", data['mac'])
        return retVal


    def checkChangeFlagForDevice(self, uuid):
        retVal = ("Unauthorized", 401)
        selectQuery = "select uuid, mac, type, location, pollinterval, apiusername, apipassword, changeflag from devices where uuid = '%s'" % (uuid)
        res = self.executeSelectQuery(selectQuery)
        if res[1] == 200 and res[0][0][7] == 1:
            self.logger.info("Changeflag is enabled and so, sending necessary info to the device")
            info = { 'uuid' : res[0][0][0], 'mac' : res[0][0][1], 'type' : res[0][0][2], 
                     'location' : res[0][0][3], 'pollinterval' : res[0][0][4], 
                     'apiusername' : res[0][0][5], 'apipassword' : res[0][0][6],
                     'status' : 'update'
                   }
            retVal = (json.dumps(info), 200)
            # change the device changeflag to '0'
            self.updateDevice("changeflag = 0", uuid = uuid)
        return retVal


    def getSmsSettings(self):
        selectQuery = "select username, password from smssettings where status = 'Active'"
        return self.executeSelectQuery(selectQuery)


    def getEmailSettings(self):
        selectQuery = "select mailserver, fromaddress, username, password from emailsettings where status = 'Active'"
        return self.executeSelectQuery(selectQuery)


    def getDeviceDetails(self, uuid):
        selectQuery = "select uuid, mac, type, location, pollinterval, apiusername, apipassword, minthreshold_temp, maxthreshold_temp, description, emailflag, toemail, smsflag, tonumber, changeflag, status from devices where uuid = '%s'" % (uuid)
        return self.executeSelectQuery(selectQuery)


    def insertTemperature(self, data):
        insertQuery = "insert into temperature (uuid, ctemperature, chumidity, cdate, ctime, status) values ('%s', '%s', '%s', '%s', '%s', %d)" % (data['uuid'], data['temp'], data['hum'], data['date'], data['time'], data['status']) 
        # when uuid is available, then insert the temperature data
        if self.isDeviceExist(data['uuid'])[1] == 302:
            res = self.insertRowToDb(insertQuery)


if __name__== "__main__":
    data = {'mac' : '1239', 'location' : 'lab-1', 'type' : 'temperature'}
    obj=Connector(user='root', password='root123', host='127.0.0.1', database='imonitor')
    print obj.registerDevice(data)

