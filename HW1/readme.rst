Launching the script:

Python3 needs to be installed

python log_analyzer.py [--config <config_file>]

Config parameters description:
[custom] section
REPORT_SIZE  	- The size of final report in lines
REPORT_DIR 		- Directory where reports are placed
LOG_DIR			- Directory where source log files are placed
TS_PATH			- Path and name of timestamp file
ERRORS_PERCENT	- Percentage of number of lines
LOG_PATH		- Path where result script log is placed

Files required:
report.html - report template
logreader.ini - config file example
