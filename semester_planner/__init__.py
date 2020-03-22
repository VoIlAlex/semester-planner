from todoist.api import TodoistAPI
import argparse
import json
import os
import sys
import datetime
from via_logger import BeautifulLogger
from via_logger.utils import generate_log_filename
from typing import Union, List

# LOGS_LOCATION = '/var/log/semester_planner' if sys.platform == 'linux' else '.'
LOGS_LOCATION = '.'
if not os.path.exists(LOGS_LOCATION):
    os.makedirs(LOGS_LOCATION)


class Class:
    def __init__(self, subject: str, date: datetime.date, number: int):
        self.subject = subject
        self.date = date
        self.number = number

