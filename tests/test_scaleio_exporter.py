#!/usr/bin/python3
"""Tests for transpopy files"""


from unittest import TestCase, main, mock
from collections import defaultdict
from configparser import SafeConfigParser, SectionProxy
from scaleio_exporter.scl_conn import connect_scaleio
from scaleio_exporter.scl_logger import scl_logger


class testSclConn(TestCase):
    """Test Class connect_scaleio."""

    def test_scl_config_ini(self):
        self.assertIsInstance(connect_scaleio('samples/scaleio_exporter.ini').config_ini(),
                              SectionProxy)

    def test_scl_get_login(self):
        self.assertIsInstance(connect_scaleio('samples/scaleio_exporter.ini').get_login(),
                              str)


class testSclLogger(TestCase):
    """Test Class connect_scaleio."""

    def test_scl_log_data(self):
        mock_log_data = mock.create_autospec(scl_logger("Test").log_data,
                                             return_value="Mock Test")
        self.assertEqual(mock_log_data(), "Mock Test")


if __name__ == "__main__":
    main()
