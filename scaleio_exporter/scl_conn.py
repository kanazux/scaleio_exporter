#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
from subprocess import call, check_output
from configparser import SafeConfigParser


class connect_scaleio():
    """
    Class to connect on the ScaleIO master node.

    Read an ini file to get environment variables.
    Must be set on terminal console the variables above:
    MDM_IPS: Ips of all nodes on the ScaleIO cluster.
    MDM_PORT: Port of MDM management
    MDM_USER: Username for ScaleIO
    MDM_PASS: Password to login into ScaleIO
    """

    def __init__(self, conf):
        """Init the class variables."""

        self.conf = conf
        self.scli = "/bin/scli"
        self.login = ("{} --mdm_ip {} --mdm_port {} --login "
                      "--username {} --password {} --approve_certificate")

    def config_ini(self):
        """Read ini file to get env variables to connect on scaleio."""

        if not os.path.exists(self.conf):
            error_msg = """
            Config file not founded.
            Check if the file {} exists in the directory.
            Exiting...
            """.format(self.conf)
            print(error_msg)
            sys.exit(0)
        config = SafeConfigParser(os.environ)
        config.read(self.conf)
        return config["CONN"]

    def get_login(self):
        """Check login parameters from config parser."""

        get_config = self.config_ini()
        for param in ["mdm_ips", "mdm_port", "username", "password"]:
            if not get_config.get(param) or get_config.get(param) == "":
                print("Local variable {} not set in terminal.\nExiting...\n".format(param))
        
        return self.login.format(self.scli,
                                 get_config.get("mdm_ips"),
                                 get_config.get("mdm_port"),
                                 get_config.get("username"),
                                 get_config.get("password"))

    def conn(self):
        """Connect on the ScaleIO."""

        _conn = check_output([self.get_login()], shell=True)
        os.system(self.get_login())
        print(_conn)