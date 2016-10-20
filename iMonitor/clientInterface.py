#!/usr/bin/python

import logging

from flask import Flask, request, jsonify, url_for

class clientInterface:
    def __init__(self, ctrObj):
        self.logger = logging.getLogger('iMonitor.clientInterface')
        self.app = Flask(__name__)
        self.controller = ctrObj
        self.app.add_url_rule('/auth', None, self.auth, methods=['POST'])
        self.app.add_url_rule('/services/temperature', None, self.temperature, methods=['POST'])
        self.app.add_url_rule('/', None, self.siteMap, methods=['GET'])


    def siteMap(self):
        """Print available apis."""
        self.logger.info("Received %s request", __name__)
        func_list = {}
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func_list[rule.rule] = self.app.view_functions[rule.endpoint].__doc__
        return jsonify(func_list)


    def auth(self):
        """To generate device-id and get config details"""
        self.logger.info("Received %s request", __name__)
        if request.method == 'POST' and request.is_json:
            return self.controller.registerDevice(request.json)
        else: 
            return "Error: Operation Not Supported", 405


    def temperature(self):
        """To get / post temperature details"""
        self.logger.info("Received %s request", __name__)
        if request.method == 'POST' and request.is_json:
            return self.controller.createTemperatureEntry(request.json)
        else: 
            return "Error: Operation Not Supported", 405


    def runApp(self):
        self.logger.info("Start listioning to client requests")
        self.app.run(port=3001, host="0.0.0.0")
    

if __name__ == "__main__":
    ci = clientInterface()
    ci.runApp()

