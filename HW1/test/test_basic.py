import unittest
import datetime
import os

import log_analyzer

class MyFirstTest(unittest.TestCase):

    def testExpectTsEqual(self):
		"""
		Checks that ts in .ts file approximately equals to mtime of ts file (the difference is less than 2 minutes)
		"""
		#real_config = log_analyzer.get_config('./logreader.ini')
		real_config = log_analyzer.config
		ts_file = open(real_config["TS_PATH"][2:])
		ts_from_file = ts_file.read()
		ts_datetime = datetime.datetime.fromtimestamp(float(ts_from_file))
		ts_file_mtime = os.path.getmtime(real_config["TS_PATH"])
		ts_mtime_datetime = datetime.datetime.fromtimestamp(ts_file_mtime)
		td = abs(ts_mtime_datetime - ts_datetime).seconds
		self.assertTrue(td < 120)
