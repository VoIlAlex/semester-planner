import todoist
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
        self.begin = None
        self.end = None
        self.lectures: List[ClassData] = []
        self.practical: List[ClassData] = []
        self.labs: List[ClassData] = []

    def parse_dict(self, semester_dict: dict):
        self.number = semester_dict['semester']['number']
        self.begin = semester_dict['semester']['begin']
        self.end = semester_dict['semester']['end']

        def parse_study_type(name: str, semester_dict: dict) -> List:
            parsed_study_type = []
            for subject_info in semester_dict['classes']['labs']:
                subject = subject_info['subject']
                for day in subject_info['schedule']:
                    for class_data in subject_info['schedule'][day]:
                        class_data = ClassData.parse(
                            class_data,
                            begin=self.begin,
                            end=self.end,
                            subject=subject
                        )
                        parsed_study_type.append(class_data)
            return parsed_study_type

        self.lectures = parse_study_type('lectures', semester_dict)
        self.parctical = parse_study_type('parctical', semester_dict)
        self.labs = parse_study_type('labs', semester_dict)


class SemesterPlanner:
    # I don't know whether it works
    # for Windows. I mean /tmp/... It
    # does not exist on Windows, right?
    # So... We'll see what gonna happen;)
    logger = BeautifulLogger.get_instance(
        os.path.join(
            LOGS_LOCATION,
            'semester_planner.log'
        )
    )

    def __init__(self, semester: Semester):
        self.semester = semester

    def setup_todoist(self,
                      api_token: str,
                      root_project: str = None,
                      labs_project: str = "Labs",
                      lectures_project: str = "Lectures",
                      practical_project: str = "Practical"):
        api = TodoistAPI(api_token)
        api.sync()

        # Get root project from TodoistAPI
        projects: List[todoist.models.Project] = api.state['projects']

        def create_project_if_not_exists(project_name: str,
                                         parent_project: todoist.models.Project,
                                         color: todoist.api.Col) -> todoist.models.Project:
            for project in projects:
                if project['name'] == project_name and project['parent_id'] == parent_project['id']:
                    return project
            else:
                project = api.projects.add(
                    name=project_name,
                    parent_id=parent_project['id']
                )
                api.commit()
                return project

        for project in projects:
            if project['name'] == root_project:
                answer = None
                while answer != 'y' and answer != 'n':
                    answer = input(
                        'Do you want to clear the project "{}"? [y/n] '.format(root_project))
                if answer == 'y':
                    project.delete()
                    root_project = api.projects.add(name=root_project)
                    break
                else:
                    root_project = project
                    break
        else:
            root_project = api.projects.add(name=root_project)
        api.commit()

        labs_project = create_project_if_not_exists(
            project_name=labs_project,
            parent_project=root_project
        )
        self.__todoist_upload_labs(api, labs_project)

        api.commit()

    def __todoist_upload_labs(self, api: todoist.TodoistAPI, labs_project: todoist.models.Project):
        semester_task_content = 'Labs. Semester #{}'.format(
            self.semester.number,
            date_string=str(self.semester.end),
            project_id=labs_project['id']
        )
        semester_task = api.items.add(
            semester_task_content,
            project_id=labs_project['id']
        )
        subject = None
        subject_task = None
        subject_lab_count = 0
        for class_data in self.semester.labs:
            if class_data.subject != subject:
                subject = class_data.subject
                subject_task = api.items.add(
                    '{}:'.format(class_data.subject),
                    project_id=labs_project['id'],
                    parent_id=semester_task['id']
                )
                subject_lab_count = 0
            for class_instance in class_data:
                subject_lab_count += 1
                class_instance_content = '{}. Lab #{}'.format(
                    subject,
                    subject_lab_count)

                # Create Todoist-compatible
                # due date string
                class_instance_due_date = class_instance.date + class_data.interval
                if class_instance_due_date < datetime.date.today():
                    class_instance_due_date = datetime.date.today()
                class_instance_due_date = str(class_instance_due_date)

                api.items.add(
                    class_instance_content,
                    project_id=labs_project['id'],
                    parent_id=subject_task['id'],
                    date_string=class_instance_due_date
                )
            api.commit()

