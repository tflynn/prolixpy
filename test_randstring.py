#!/usr/bin/env python

from prolix import rand
import standard_logger
logger = standard_logger.get_logger('random_limits', console=True, level_str="DEBUG")
rs = rand.RandomString(logger=logger)
for i in range(1,100):
	print(rs.random_utf8_string(10))

