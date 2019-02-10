#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import sys
import time
import socket
from subprocess import call, CalledProcessError
from scaleio_exporter.scl_logger import scl_logger
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
        self.zbx_sender = "/bin/zabbix_sender -c {} -s {} -k {} -o {}"
        self.zbx_conf = "/etc/zabbix/zabbix_agentd.conf"
        self.conf = connect_scaleio("scaleio_exporter.ini")

    def call_cmd(self, _storage, _key, _value):
        """Return a cmd line for zabbix_sender."""

        return self.zbx_sender.format(
            self.zbx_conf, _storage, _key, _value
        )

    def send_data(self):
        """Send data to a Zabbix server."""

        try:
            get_data = self.scl_data.read_data()
            hostname = socket.gethostname()
            for storage in get_data[hostname]:
                for key, value in get_data[hostname][storage].items():
                    call([self.call_cmd(storage, key, value)], shell=True)
        except CalledProcessError:
            return "CalledProcessError"
        finally:
            scl_logger(str(sys.exc_info())).log_data()

        return "ok"