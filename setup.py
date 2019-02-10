from setuptools import setup


setup(name="scaleio_exporter",
      packages=["scaleio_exporter"],
      license="BSD2CLAUSE",
      install_requires=[''],
      scripts=['scripts/scaleio_data'],
      version='0.1',
      description='A simple collector for ScaleIO to send data to Zabbix server.',
      long_description=("Connect into a ScaleIO cluster and collect data to send "
                        "to a Zabbix server or Proxy by using zabbix_sender."),
      author='Silvio Ap Silva a.k.a Kanazuchi',
      author_email='contato@kanazuchi.com',
      url='http://github.com/kanazux/scaleio_exporter',
      zip_safe=False)
