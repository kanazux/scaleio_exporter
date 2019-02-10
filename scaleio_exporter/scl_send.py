#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import time
import socket
from subprocess import call, CalledProcessError
from scaleio_exporter.scl_parse import scaleio_data
from scaleio_exporter.scl_conn import connect_scaleio


class zbx_sender():
    """
    Class to send data to a Zabbix Server or Proxy.

    Get ScaleIO data, format to a defaultdict to generate a simple json.
    Send data by using zabbix_sender and an existing agentd conf file.
    """

    def __init__(self):
        self.scl_data = scaleio_data()
        self.zbx_sender = "/bin/zabbix_sender"
        self.zbx_conf = "/etc/zabbix/zabbix_agentd.conf"
        self.conf = connect_scaleio("scaleio_exporter.ini")

    def send_data(self):
        """Send data to a Zabbix server."""

        try:
            get_data = self.scl_data.read_data()
            hostname = socket.gethostname()
            for storage in get_data[hostname]:
                for key in storage:
                    print("Sending: Host {}, Key: {}, Value: {}".format(storage, key, storage[key]))
        except CalledProcessError:
            print("Not possible to send data, make tyy logging into ScaleIO cluster")
