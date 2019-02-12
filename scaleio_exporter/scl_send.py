#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import os
import sys
import time
import socket
from subprocess import CalledProcessError, call
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
        self.hostname = socket.gethostname()
        self.discover_file = "/etc/scaleio_exporter/scaleio_storages"
        self.zbx_sender = '/bin/sh /bin/zabbix_sender -c {} -s "{}" -i {} -vv'
        self.zbx_sh_sender = "/bin/sh /etc/scaleio_exporter/zbx_sender.sh"
        self.zbx_conf = "/etc/zabbix/zabbix_agentd.conf"
        self.zbx_item = '"{}" "discovery.volume" {{"data":[{{"{{#VOLUME}}": "{}"}}]}}\n'
        self.conf = connect_scaleio("/etc/scaleio_exporter/scaleio_exporter.ini")

    def call_cmd(self, _storage, _key, _value):
        """Return a cmd line for zabbix_sender."""

        return self.zbx_sender.format(
            self.zbx_conf, _storage, _key, _value
        )

    def check_discover(self, _storages):
        """Check if storage was discovered, if not create items prototype into Zabbix."""

        if not os.path.exists(self.discover_file):
            from pathlib import Path
            Path(self.discover_file).touch()
        storage_items = _storages.difference(
            set([s for s in str(open(self.discover_file,'r').read()).split("\n")]))
        if len(storage_items) != 0:
            for _storage in storage_items:
                with open(self.discover_file, 'a') as discover_file:
                    discover_file.write(_storage + "\n")
                with open('/tmp/{}'.format(_storage), 'w') as zbx_tmp_file:
                    zbx_tmp_file.write(self.zbx_item.format(self.hostname, _storage))
                call([self.zbx_sender.format(self.zbx_conf, self.hostname, "/tmp/{}".format(_storage))], shell=True)
                #os.unlink(zbx_tmp_file.name)
        sys.exit(0)

    def send_data(self):
        """Send data to a Zabbix server."""

        try:
            get_data = self.scl_data.read_data()
            self.check_discover(
                set([get_data[self.hostname][pool]['NAME'] for pool in get_data[self.hostname]]))
            for storage in get_data[self.hostname]:
                for key, value in get_data[self.hostname][storage].items():
                    # call([self.call_cmd(storage, key, value)], shell=True)
                    print('ok')
        except CalledProcessError:
            return "CalledProcessError"
        finally:
            scl_logger(str(sys.exc_info())).log_data()

        return "ok"