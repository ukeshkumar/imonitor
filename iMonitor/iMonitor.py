import logging

from clientInterface import clientInterface
from controller import controller


class iMonitor:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/imonitor.log',
                    filemode='a')
        self.logger = logging.getLogger('iMonitor')
        self.logger.info("Starting iMonitor Application...")
        self.logger.info("Creating controller object")
        self.controller = controller()
        self.logger.info("Creating client interface object")
        self.ci = clientInterface(self.controller)

    def run(self):
        self.ci.runApp()


if __name__ == '__main__':
    server = iMonitor()
    server.run()
