#!/bin/python3.6
# -*- coding: utf-8 -*-


from collections import defaultdict
from subprocess import check_output
from scaleio_exporter.scl_conn import connect_scaleio


class scaleio_data(object):
    """
    Class to execute query by using ScaleIO CLI and get data.

    The data will be load on a defaultdict, making possible export in a json format.
    """

    def __init__(self):
        self.params = "--query_properties --object_type STORAGE_POOL --all_objects --properties"
        self.properties = (
            "NAME,MAX_CAPACITY_IN_KB,SPARE_CAPACITY_IN_KB,THIN_CAPACITY_ALLOCATED_IN_KB,"
            "THICK_CAPACITY_IN_USE_IN_KB,UNUSED_CAPACITY_IN_KB,SNAP_CAPACITY_IN_USE_OCCUPIED_IN_KB,"
            "CAPACITY_IN_USE_IN_KB,UNREACHABLE_UNUSED_CAPACITY_IN_KB,DEGRADED_HEALTHY_CAPACITY_IN_KB,"
            "FAILED_CAPACITY_IN_KB,USER_DATA_READ_BWC,USER_DATA_WRITE_BWC,REBALANCE_READ_BWC,"
            "FWD_REBUILD_READ_BWC,BCK_REBUILD_READ_BWC,AVAILABLE_FOR_THICK_ALLOCATION_IN_KB"
        )
        self.conn = connect_scaleio("scaleio_exporter.ini")
        self.mdm_ips = self.conn.config_ini().get("mdm_ips")
        self.mdm_port = self.conn.config_ini().get("mdm_port")
        self.user = self.conn.config_ini().get("username")
        self.passwd = self.conn.config_ini().get("password")
        self.query = "{} {} {} --mdm_ip {} --mdm_port {}".format(
            self.conn.scli, self.params, self.properties, self.mdm_ips, self.mdm_port
        )

    def read_data(self):
        raw_data = check_output([self.query], shell=True)
        print(raw_data)