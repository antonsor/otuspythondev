#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import configparser
import re
import logging
import datetime
import gzip
from collections import defaultdict
from string import Template


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "WORK_DIR": "./work",
    "TS_DIR": "./ts",
    "ERRORS_PERCENT": 30,
    "LOG_FILEPATH": None  #"log_analyzer.out"
}



# <Anton>
# idea 1 for unittest: check that report exists and it consists of ... entries
# idea 2 for unittest: mtime файлика должен быть равен этому таймстемпу

# create dictionary: url time_sum or value "statistics"?
# create 

# -actions: create github account
# +code: regexp for file from ga
LOG_NAMES_PATTERN = "^nginx-access-ui\.log\-(\d{8})(\.gz)?$"
REPORT_NAMES_PATTERN = "^report\-\d{4}\.\d{2}\.\d{2}\.html$"
YYYYMMDD_PATTERN = "(20\d{2})(1[0-2]|0[1-9])(3[01]|[0-2][1-9]|[12]0)"
LOGGING_FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'

# -code: insert into template
# +code: process lines from notebook
# -code: logging library (look at logging.exception)
# +code: work with configs
# +code: print "the square of {} equals {}".format(args.square, answer)

# </Anton>
        if folder_name not in os.listdir(FILE_SAVE_PATH):
            os.mkdir(FILE_SAVE_PATH+folder_name)
       #/good example

def get_config(path_to_config):
    """
    Forms the result config using default config and replacing its values from config file
    """
    config_custom = configparser.ConfigParser()
    try:
        config_custom.read(path_to_config)
        config_custom = config_custom['custom']
    except Exception as e:
        # write log: Exception: str(e)
        print(str(e))
        sys.exit()
    result_config = config
    for parameter in result_config:
        result_config[parameter] = config_custom.get(parameter, result_config[parameter])
    return result_config
    

def prepare_config_dirs(config_dict):
    """"
    Creates folders needed for successful work of script.
    Paths are taken from config_dict parameters with "_DIR" suffixes.
    Avoids the problems with dirs that are not exist
    """
    for parameter in config_dict:
        if parameter.endswith("_DIR"):
            parameter_dir = config_dict.get(parameter, None)
            if parameter_dir:
                if not os.path.isdir(parameter_dir):   # ! to correct with config
                    try:
                        os.makedirs(parameter_dir)
                    except OSError:
                        # write log: Unable to create dir parameter_dir
                        print("Unable to create dir", parameter_dir)
                        return False
    return True


def get_file_to_parse():
    """
    Checks if there are fresh files to parse and
    returns log file name to parse
    """
    # get the log file with max date
    file_list = []
    object_names = os.listdir() # ! to correct with path in config
    for object_name in object_names:
        if re.fullmatch(LOG_NAMES_PATTERN, object_name):
            file_list.append(object_name)
    file_list.sort(reverse=True)
    if len(file_list) > 0:
        log_file = file_list[0]
        print("Last log file found: ", log_file)
        # write log: Info: Last log file found: , log_file
    else:
        # write log: Info: No appropriate log files found
        return False
    
    # get the report with max date
    file_list = []
    report_dir = config.get("REPORT_DIR")  #! to correct with config
    object_names = os.listdir(report_dir)
    for object_name in object_names:
        if re.fullmatch(REPORT_NAMES_PATTERN, object_name):
            file_list.append(object_name)
    file_list.sort(reverse=True)
    if len(file_list) > 0:
        report_file = file_list[0]
        print("Last report file found: ", report_file)
        # write log: Info: Last report file found: , report_file
        
        # compare last log date and last report date
        last_log_date = datetime.datetime.strptime(log_file[20:28], "%Y%m%d")
        last_report_date = datetime.datetime.strptime(report_file[7:17], "%Y.%m.%d")
        if last_log_date > last_report_date:
            return log_file
        else:
            print("No fresh log files found. Everything is up to date")
            # write log: Info: No fresh log files found. Everything is up to date
    else:
        return log_file

def parse_line(line):
    """
    Implements parsing of a line
    Returns overall result and parced fields:
        is_parced       - 0 if parsing didn't cause any exceptions, 1 - otherwise
        url             - parsed field
        request_time    - parsed field
    """
    is_parsed = 0
    url = ""
    request_time = 0.0
    try:
        line = line.split("GET ")[1]
        url = line.split(" HTTP/1.1")[0]
        request_time = float(line.split()[-1])
    except Exception:
        pass
    finally:
        is_parsed = 1
    return is_parsed, url, request_time

def write_ts():
    pass


def main():

    # get config path from arguments if it is present
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config', default='./logreader.ini', help='Path to config file')
    args = arg_parser.parse_args()
    config_final = get_config(args.config)

    # configure logger
    logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT, datefmt='%Y.%m.%d %H:%M:%S',
                        filename=config_final.get("LOG_FILEPATH", None))
    logger = logging.getLogger()
    try:
        if prepare_config_dirs(config_final):
            parsed_lines_counter = 0
            total_lines_couter = 0
            calc_dict = {}
            calc_init = {"count":0,
                      "count_perc":0,
                      "time_sum":0,
                      "time_perc":0,
                      "time_avg":0,
                      "time_max":0,
                      "time_med":0
                      }
            filter_dict = defaultdict(float)

            log_name = get_file_to_parse()
            if log_name:
                print('Info: Start parsing file ', log_name)
                if log_name.endswith(".gz"):
                    log_to_parse = gzip.open(log_name, 'rb')
                else:
                    log_to_parse = open(log_name, 'rb')

                # Step 1: Parsing the file and filling the non-percentage values
                for line in log_to_parse:
                    total_lines_couter += 1
                    is_parsed, url, request_time = parse_line(line)
                    parsed_lines_counter += is_parsed
                    if is_parsed:
                        # modify filter_dict (key: url, value: time_sum)
                        time_sum = filter_dict.get(url,0) + request_time
                        filter_dict[url] = time_sum
                        # modify values dict (key: url, value: dict of column:value)
                        calc_entry = calc_dict.get(url, calc_init)
                        calc_entry["count"] += 1
                        calc_entry["time_sum"] = time_sum
                        # calculate running avg by formula: average = old average + (next data - old average) / next count
                        # taken from https://stackoverflow.com/questions/12636613/how-to-calculate-moving-average-without-keeping-the-count-and-data-total
                        calc_entry["time_avg"] = calc_entry["time_avg"] + (request_time - calc_entry["time_avg"])/calc_entry["count"]
                        calc_entry["time_max"] = request_time if request_time > calc_entry["time_max"] else calc_entry["time_max"]
                        # temporarily runing median = running avg (looking for a formula
                        calc_entry["time_med"] = calc_entry["time_avg"]
                        calc_dict[url] = calc_entry
                    else:
                        if total_lines_couter > 100 and (total_lines_couter - parsed_lines_counter)*100 / total_lines_couter > int(config_final["ERRORS_PERCENT"]):
                            #logger.error('Too many parsing errors. Perhaps the log format has changed. Everything is stopped.')
                            logging.error('Too many parsing errors. Perhaps the log format has changed. Everything is stopped.')
                            sys.exit()

                # Step 2: Get total values
                time_sum_total = 0
                count_total = 0
                for key in calc_dict:
                    count_total += calc_dict[key]["count"]
                    time_sum_total += calc_dict[key]["time_sum"]

                # Step 3: Calculate percentage values
                for key in calc_dict:
                    calc_dict[key]["count_perc"] = calc_dict[key]["count"]/count_total
                    calc_dict[key]["time_perc"] = calc_dict[key]["time_sum"]/time_sum_total

                # Step 4: Form the list of REPORT_SIZE urls with max time_sum
                entries_counter = 0
                final_urls = []
                for entry in sorted(filter_dict, key=filter_dict.get, reverse=True):
                    entries_counter += 1
                    if entries_counter <= int(config_final[REPORT_SIZE]):
                        final_urls.insert(len(final_urls), entry)

                # Step 5: Form table_json
                table_json = []
                for entry in final_urls:
                    table_json_entry = calc_dict[entry]
                    table_json_entry["url"] = entry
                    table_json.insert(len(table_json), table_json_entry)

                # Step 6: Form the report
                with open('report.html', 'r') as rep_template_file:
                    rep_template = Template(rep_template_file.read())  #.replace('\n', '')
                    report_file = open("ReportNN.txt", "w") # !! to add path and date
                    report_file.write(rep_template.substitute(table_json = str(table_json)))
                    report_file.close()



        else:
            sys.exit()

    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    main()

 
