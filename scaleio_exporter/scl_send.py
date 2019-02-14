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
        self.zbx_sender = '/bin/zabbix_sender -c {} -s "{}" -i {} -vv'
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
                os.unlink(zbx_tmp_file.name)

    def send_data(self):
        """
        Send data to a Zabbix server.
        
        Format data to save into a file on the /tmp directory.
        The data will be saved like example above:
        <hostname> <variable[storage]> <value>
        zabbix_sender will be used to send data to a zabbix proxy.
        """

        try:
            get_data = self.scl_data.read_data()
            self.check_discover(
                set([get_data[self.hostname][pool]['NAME'] for pool in get_data[self.hostname]]))
            
            var_list = []
            var_line = "{} {} {}"
            for storage in get_data[self.hostname]:
                for key, value in get_data[self.hostname][storage].items():
                    var_list.append(var_line.format(self.hostname, 
                                                    "{}[{}]".format(key, get_data[self.hostname][storage]['NAME']),
                                                    value))
            
            with open('/tmp/scale_items', 'w') as scale_items:
                scale_items.write("\n".join(var_list))
            call([self.zbx_sender.format(self.zbx_conf, self.hostname, "/tmp/scale_items")], shell=True)
            os.unlink('/tmp/scale_items')
        except CalledProcessError:
            return "CalledProcessError"
        except Exception as error:
            scl_logger(error).log_data()

        return "ok"