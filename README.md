# scaleio_exporter

Exporter data for ScaleIO

### Read Data
The script will read data from ScaleIO cluster using the scli (ScaleIO CLI).
First of all login into a ScaleIO MDM and get data of the storages created.
The credentials to connect into ScaleIO are been read from the environment variables.

Remember to export the before execute this script, like:
> export MDM_IPS "192.168.0.100,192.168.0.101,192.168.100.12"

The Variables are:
  * MDM_IPS (Ips of the MDM cluster)
  * MDM_PORT (Port to connect on ScaleIO)
  * SCALEIO_USER (User to connect on ScaleIO)
  * SCALEIO_PASS (Password)

### Format Data to a defaultdict
After get data from ScaleIO format into a defaultdict object.
This object can be used to create a JSON file and send all data in an unique time.

### Send data
This script will use the zabbix_sender to send data to a server or proxy.
Will be necessary a zabbix_agentd.conf in the directory /etc/zabbix.
More detail of zabbix_agentd.conf [here](https://www.zabbix.com/documentation/4.0/manual/appendix/config/zabbix_agentd).
