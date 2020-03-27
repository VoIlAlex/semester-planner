"""Collection of dataholders."""
import datetime
from typing import Union, List


class Class:
    def __init__(self, subject: str, date: datetime.date, number: int):
        self.subject = subject
        self.date = date
        self.number = number


class ClassIterator:
    def __init__(self, class_data):
        self.class_data = class_data
        self.current_date = class_data.start
        self.current_number = 0
        while (self.current_date.weekday() in self.class_data.dayoffs):
            self.current_date += self.class_data.interval

    def __next__(self):
        if self.current_date >= self.class_data.end:
            raise StopIteration
        obj = Class(
            subject=self.class_data.subject,
            date=self.current_date,
            number=self.current_number
        )
        self.current_date += self.class_data.interval
        while (self.current_date.weekday() in self.class_data.dayoffs):
            self.current_date += self.class_data.interval
        self.current_number += 1
        return obj


class ClassData:
    DATE_FORMAT = '%m/%d/%Y'

    def __init__(self,
                 subject: str,
                 start: Union[str, datetime.date],
                 end: Union[str, datetime.date],
                 interval: Union[int, datetime.timedelta],
                 dayoffs: List[Union[str, int]]):

        self.subject = subject
        if isinstance(start, datetime.date):
            self.start = start
        else:
            self.start = datetime.datetime.strptime(
                start, ClassData.DATE_FORMAT).date()

        if isinstance(end, datetime.date):
            self.end = end
        else:
            self.end = datetime.datetime.strptime(
                end, ClassData.DATE_FORMAT).date()

        if isinstance(interval, datetime.timedelta):
            self.interval = interval
        else:
            self.interval = datetime.timedelta(interval)

        self.dayoffs = []
        for dayoff in dayoffs:
            dayoff = dayoff.lower()
            if dayoff == 'mon' or dayoff == 'monday' or dayoff == 0:
                self.dayoffs.append(0)
            elif dayoff == 'tue' or dayoff == 'tues' or dayoff == 'tuesday' or dayoff == 1:
                self.dayoffs.append(1)
            elif dayoff == 'wed' or dayoff == 'wednesday' or dayoff == 2:
                self.dayoffs.append(2)
            elif dayoff == 'thu' or dayoff == 'thurs' or dayoff == 'thursday' or dayoff == 3:
                self.dayoffs.append(3)
            elif dayoff == 'fri' or dayoff == 'friday' or dayoff == 4:
                self.dayoffs.append(4)
            elif dayoff == 'sat' or dayoff == 'saturday' or dayoff == 5:
                self.dayoffs.append(5)
            elif dayoff == 'sun' or dayoff == 'sunday' or dayoff == 6:
                self.dayoffs.append(6)

    def __iter__(self):
        return ClassIterator(self)

    @staticmethod
    def parse(
        obj: dict,
        **defaults
    ):
        """Build ClassData object from dict with provided defaults

        Arguments:
            obj {dict} -- dict object with the data about the class
        """
        if 'start' in obj:
            start = obj['start']
        else:
            start = defaults['start']

        if 'interval' in obj:
            interval = obj['interval']
        else:
            interval = defaults.get('interval', 1)

        if 'end' in obj:
            end = obj['end']
        elif 'count' in obj:
            count = obj['count']
            end = datetime.datetime.strptime(
                start,
                ClassData.DATE_FORMAT
            ).date() + datetime.timedelta(interval * count)
        else:
            end = defaults['end']

        if 'dayoffs' in obj:
            dayoffs = obj['dayoffs']
        else:
            dayoffs = defaults.get('dayoffs', [])

        if 'subject' in obj:
            subject = obj['subject']
        else:
            subject = defaults['subject']

        return ClassData(
            subject=subject,
            start=start,
            end=end,
            interval=interval,
            dayoffs=dayoffs
        )


class Semester:
    def __init__(self):
        self.number = None
        self.start = None
        self.end = None
        self.lectures: List[ClassData] = []
        self.practical: List[ClassData] = []
        self.labs: List[ClassData] = []

    def parse_dict(self, semester_dict: dict):
        self.number = semester_dict['semester']['number']
        self.start = semester_dict['semester']['start']
        self.end = semester_dict['semester']['end']

        def parse_study_type(name: str, semester_dict: dict) -> List:
            parsed_study_type = []
            for subject_info in semester_dict['classes']['labs']:
                subject = subject_info['subject']
                for day in subject_info['schedule']:
                    for class_data in subject_info['schedule'][day]:
                        class_data = ClassData.parse(
                            class_data,
                            start=self.start,
                            end=self.end,
                            subject=subject
                        )
                        parsed_study_type.append(class_data)
            return parsed_study_type

        self.lectures = parse_study_type('lectures', semester_dict)
        self.parctical = parse_study_type('parctical', semester_dict)
        self.labs = parse_study_type('labs', semester_dict)
