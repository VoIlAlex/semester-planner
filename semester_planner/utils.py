import os
import configparser
import semester_planner.config as cfg
from typing import Any


class SemesterPlannerConfig:
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(cfg.CONFIG_FILE_PATH)

    def save_default_config(self):
        for section in cfg.DEFAULT_LOCAL_CONFIG:
            if section not in self.config_parser:
                self.config_parser[section] = {}
            for key, value in cfg.DEFAULT_LOCAL_CONFIG[section].items():
                if key not in self.config_parser[section]:
                    self.config_parser[section][key] = str(value)

    def __getitem__(self, section: str):
        if section not in self.config_parser:
            self.config_parser[section] = {}
        return self.config_parser[section]

    def __setitem__(self, section: str, value: dict):
        self.config_parser[section] = value

    def save(self):
        self.config_parser.write(open(cfg.CONFIG_FILE_PATH, 'w+'))

    def to_string(self, section: str):
        if section not in self.config_parser:
            return "Empty section."
        result = "[{}]\n".format(section)
        for key, value in self.config_parser[section].items():
            result += '{} = {}\n'.format(key, value)
        return result

    def __str__(self):
        result = 'Semester planner configuration. ({})\n'.format(
            cfg.CONFIG_FILE_PATH)
        result += '\n'
        for section in self.config_parser:
            result += self.to_string(section)
