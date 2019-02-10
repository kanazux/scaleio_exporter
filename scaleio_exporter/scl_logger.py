#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import os
import time
from datetime import datetime


class scl_logger():
    """Create file, directories and log errors."""

    def __init__(self, msg_error):
        self.msg = msg_error
        self.time = datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
        self.directory = "/var/logs/scaleio"
        self.log_file = "scl_zbx.log"

    def check_dir(self):
        """Check if log directory exists and create if not."""
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory, 755)

    def log_data(self):
        with open(os.path.join(self.directory, self.log_data), "a") as logger_file:
            logger_file.write("{}, {}".format(self.time, self.msg))