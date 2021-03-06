#!/usr/bin/python
import os
import argparse
import sys
import logging
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseValidator(ABC):
    def __init__(self, param):
        self.param = param

    @abstractmethod
    def is_valid(self):
        pass

class DateRangeValidator(BaseValidator):
    def is_valid(self):
        date_range = self.param

        if not date_range:
            sys.stdout.write('Date range is not defined, all files will be cloned...\n')
            return True

        date_format = '%Y%m%d%H%M'
        splitted = date_range.rstrip().split('-')

        if len(splitted) != 2:
            sys.stdout.write('daterange is not correctly\n')
            logger.info('Date range is not specified correctly\n')
            return False

        date_start = datetime.strptime(splitted[0], date_format)
        date_end = datetime.strptime(splitted[1], date_format)

        if date_start > date_end:
            sys.stdout.write('Date end cannot be bigger than date start\n')
            return False

        return True

class PathValidator(BaseValidator):
    def is_valid(self):
        self.dir_path = self.param
        return self.path_exist()

    def path_exist(self):
        if not self.dir_path:
             sys.stdout.write(f'Path cannot be empty\n')
             return False

        if not os.path.exists(os.path.join(self.dir_path)):
             sys.stdout.write(f'Directory {self.dir_path} does not exists.\n')
             return False

        return True

class NameValidator(BaseValidator):
    def is_valid(self):
        self.name = self.param
        if not self.name:
            sys.stdout.write('Name is not defined, please try again...\n')
            return False

        return True

class FileValidator(BaseValidator):
    def is_valid(self):
        self.path = self.param

        if not PathValidator(self.path).is_valid():
            return False

        """ Check given file line by line """
        with open(self.path, 'r') as input_file:
            splitted_line = input_file.readline().split(' ')

            if len(splitted_line) < 4:
                return False

            path_in, path_out = splitted_line[:2]
            if not PathValidator(path_in).is_valid():
                return False

            if not PathValidator(path_out).is_valid():
                return False

            if not NameValidator(splitted_line[2]).is_valid():
                return False

            if not DateRangeValidator(splitted_line[3]).is_valid():
                return False

        return True

class CommandArgsValidator:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

        """ If file path is given then we omit every validators because
            all the data will be read from given file, so we only have to
            check this file but we need above validators to do that
        """
        if not self.kwargs['file']:
            self.validators = [
                    PathValidator(self.kwargs['in']),
                    PathValidator(self.kwargs['out']),
                    NameValidator(self.kwargs['name']),
                    DateRangeValidator(self.kwargs['date']),
            ]
        else:
            self.validators = [FileValidator(self.kwargs['file'])]

    def check(self):
        for validator in self.validators:
            if not validator.is_valid():
                return False

        return True

