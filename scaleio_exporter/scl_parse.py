#!/bin/python3.6
# -*- coding: utf-8 -*-


import re
import time
import socket
from collections import defaultdict
from subprocess import check_output, STDOUT
from scaleio_exporter.scl_conn import connect_scaleio


class scaleio_data(object):
    """
    Class to execute query by using ScaleIO CLI and get data.

    The data will be load on a defaultdict, making possible export in a json format.
    """

    def __init__(self):
        self.sds_pattern = re.compile(r"^[\ ]+SDS:")
        self.device_pattern = re.compile(r"^[\ ]+Device:")
        self.params = "--query_properties --object_type STORAGE_POOL --all_objects --properties"
        self.latency = "--query_all_device_latency_meters --protection_domain_name"
        self.properties = (
            "NAME,MAX_CAPACITY_IN_KB,SPARE_CAPACITY_IN_KB,THIN_CAPACITY_ALLOCATED_IN_KB,"
            "THICK_CAPACITY_IN_USE_IN_KB,UNUSED_CAPACITY_IN_KB,SNAP_CAPACITY_IN_USE_OCCUPIED_IN_KB,"
            "CAPACITY_IN_USE_IN_KB,UNREACHABLE_UNUSED_CAPACITY_IN_KB,DEGRADED_HEALTHY_CAPACITY_IN_KB,"
            "FAILED_CAPACITY_IN_KB,USER_DATA_READ_BWC,USER_DATA_WRITE_BWC,REBALANCE_READ_BWC,"
            "FWD_REBUILD_READ_BWC,BCK_REBUILD_READ_BWC,AVAILABLE_FOR_THICK_ALLOCATION_IN_KB"
        )
        self.conf = connect_scaleio("/etc/scaleio_exporter/scaleio_exporter.ini")
        self.mdm_ips = self.conf.config_ini().get("mdm_ips")
        self.mdm_port = self.conf.config_ini().get("mdm_port")
        self.user = self.conf.config_ini().get("username")
        self.passwd = self.conf.config_ini().get("password")
        self.query = "{} {} {} --mdm_ip {} --mdm_port {}".format(
            self.conf.scli, self.params, self.properties, self.mdm_ips, self.mdm_port
        )
        self.data_dict = defaultdict(lambda: False)
        self.hostname = socket.gethostname()
        self.data_dict[self.hostname] = defaultdict(lambda: False)

    def format_bytes(self, _bytes, _format):
        if _format == "Bytes":
            _bytes = float(_bytes) / 1024 / 1024
        if _format == "KB":
            _bytes = float(_bytes) / 1024
        if _format == "GB":
            _bytes = float(_bytes) * 1024
        return _bytes

    def get_latency(self, _pd):
        """Get latency for PD."""

        latency_query = "{} {} {} --mdm_ip {} --mdm_port {}".format(
            self.conf.scli, self.latency, _pd.split("Pool".encode())[0].decode(), self.mdm_ips, self.mdm_port
        )
        latency_data = check_output([latency_query], shell=True, stderr=STDOUT)
        
        device_lines = [l.strip() for l in list(filter(None, latency_data.split("\n".encode())))
            if bool(self.device_pattern.match(l.decode()))]
        read_latency = "{:.2f}".format(float(sum([int(x.split()[5]) for x in device_lines])/len(device_lines)))
        write_latency = "{:.2f}".format(float(sum([int(x.split()[7]) for x in device_lines])/len(device_lines)))
        
        device_items = len(device_lines)
        
        sds_lines = [l.strip() for l in list(filter(None, latency_data.split("\n".encode())))
            if bool(self.sds_pattern.match(l.decode()))]
        max_read_lat = [" ".join([x.split()[1].decode(), x.split()[3].split("/".encode())[-1].decode(), x.split()[5].decode()]) for x in sds_lines][:3]
        max_write_lat = [" ".join([x.split()[1].decode(), x.split()[3].split("/".encode())[-1].decode(), x.split()[5].decode()]) for x in sds_lines][-3:]

        return (read_latency, write_latency, device_items, "<br/>".join(max_read_lat), "<br/>".join(max_write_lat))

    def read_data(self):
        """Get ScaleIO data and put into a default dict."""
        
        raw_data = check_output([self.query], shell=True, stderr=STDOUT)
        storages = list(filter(None, raw_data.split("STORAGE_POOL".encode())))
        for storage in storages:
            s_storage = list(filter(None, storage.split("\n".encode())))
            d_storage = defaultdict(lambda: False)
            for line in s_storage[1:]:
                s_line = line.strip().split()
                d_storage[s_line[0].decode()] = s_line[1].decode()
                if s_line[0].decode() == "USER_DATA_READ_BWC":
                    d_storage["USER_DATA_READ_BWC_IN_MB"] = self.format_bytes(s_line[5].decode().lstrip("("),
                                                                              s_line[6].decode().rstrip(")"))
                if s_line[0].decode() == "USER_DATA_WRITE_BWC":
                    d_storage["USER_DATA_WRITE_BWC_IN_MB"] = self.format_bytes(s_line[5].decode().lstrip("("),
                                                                                s_line[6].decode().rstrip(")"))

            get_latency_list = self.get_latency(s_storage[1].split()[-1].strip())
            d_storage["READ_LATENCY"] = get_latency_list[0]
            d_storage["WRITE_LATENCY"] = get_latency_list[1]
            d_storage["DEVICE_ITEMS"] = get_latency_list[2]
            d_storage["MAX_READ_LATENCY"] = get_latency_list[3]
            d_storage["MAX_WRITE_LATENCY"] = get_latency_list[4]

            self.data_dict[self.hostname][s_storage[0].decode().strip().rstrip(":")] = d_storage

        return self.data_dict