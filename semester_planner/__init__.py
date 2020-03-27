import todoist
import todoist_colors
from todoist.api import TodoistAPI
import argparse
import json
import os
import sys
import datetime
from via_logger import BeautifulLogger
from via_logger.utils import generate_log_filename
from typing import Union, List
from .data import Class, ClassData, ClassIterator, Semester
from .utils import SemesterPlannerConfig

LOGS_LOCATION = '.'
if not os.path.exists(LOGS_LOCATION):
    os.makedirs(LOGS_LOCATION)


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
                      root_project: str = "University",
                      labs_project: str = "Labs",
                      lectures_project: str = "Lectures",
                      practical_project: str = "Practical",
                      override: bool = None):
        api = TodoistAPI(api_token)
        api.sync()

        # Get root project from TodoistAPI
        projects: List[todoist.models.Project] = api.state['projects']

        override = False if override is None else override
        for project in projects:
            if project['name'] == root_project:
                if override is not None:
                    root_project = project
                    break
                answer = None
                while answer != 'y' and answer != 'n':
                    answer = input(
                        'Do you want to override existing projects? [y/n] '.format(root_project))
                if answer == 'y':
                    override = True
                root_project = project
                break
        else:
            root_project = api.projects.add(
                name=root_project,
                color=todoist_colors.PURPLE
            )
        api.commit()

        if labs_project is not None:
            labs_project = self.__todoist_create_project(
                api=api,
                project_name=labs_project,
                override=override,
                parent_project=root_project,
                existed_projects=projects,
                color=todoist_colors.BLUE)
            self.__todoist_upload_labs(api, labs_project)

        if lectures_project is not None:
            lectures_project = self.__todoist_create_project(
                api=api,
                project_name=lectures_project,
                override=override,
                parent_project=root_project,
                existed_projects=projects,
                color=todoist_colors.GREEN
            )
            self.__todoist_upload_lectures(api, lectures_project)

        if practical_project is not None:
            practical_project = self.__todoist_create_project(
                api=api,
                project_name=practical_project,
                override=override,
                parent_project=root_project,
                existed_projects=projects,
                color=todoist_colors.ORANGE
            )
            self.__todoist_upload_practical(api, practical_project)

        api.commit()

    def __todoist_create_project(self,
                                 api: todoist.TodoistAPI,
                                 project_name: str,
                                 override: bool,
                                 color: int,
                                 parent_project: todoist.models.Project = None,
                                 existed_projects: List[todoist.models.Project] = None):
        existed_projects = existed_projects if existed_projects is not None else []
        for project in existed_projects:
            if project['name'] == project_name:
                if parent_project and project['parent_id'] != parent_project['id']:
                    continue
                if override:
                    project.delete()
                    break
                return project
        project = api.projects.add(
            name=project_name,
            parent_id=parent_project['id'],
            color=color
        )
        api.commit()
        return project

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

    def __todoist_upload_lectures(self, api: todoist.TodoistAPI, lectures_project: todoist.models.Project):
        semester_task_content = 'Lecture. Semester #{}'.format(
            self.semester.number,
            date_string=str(self.semester.end),
            project_id=lectures_project['id']
        )
        semester_task = api.items.add(
            semester_task_content,
            project_id=lectures_project['id']
        )
        subject = None
        subject_task = None
        subject_lectures_count = 0
        for class_data in self.semester.labs:
            if class_data.subject != subject:
                subject = class_data.subject
                subject_task = api.items.add(
                    '{}:'.format(class_data.subject),
                    project_id=lectures_project['id'],
                    parent_id=semester_task['id']
                )
                subject_lectures_count = 0
            for class_instance in class_data:
                subject_lectures_count += 1
                class_instance_content = '{}. Lecture #{}'.format(
                    subject,
                    subject_lectures_count)

                # Create Todoist-compatible
                # due date string
                class_instance_due_date = class_instance.date + class_data.interval
                if class_instance_due_date < datetime.date.today():
                    class_instance_due_date = datetime.date.today()
                class_instance_due_date = str(class_instance_due_date)

                api.items.add(
                    class_instance_content,
                    project_id=lectures_project['id'],
                    parent_id=subject_task['id'],
                    date_string=class_instance_due_date
                )
            api.commit()

    def __todoist_upload_practical(self, api: todoist.TodoistAPI, practical_project: todoist.models.Project):
        semester_task_content = 'Practical. Semester #{}'.format(
            self.semester.number,
            date_string=str(self.semester.end),
            project_id=practical_project['id']
        )
        semester_task = api.items.add(
            semester_task_content,
            project_id=practical_project['id']
        )
        subject = None
        subject_task = None
        subject_practicals_count = 0
        for class_data in self.semester.labs:
            if class_data.subject != subject:
                subject = class_data.subject
                subject_task = api.items.add(
                    '{}:'.format(class_data.subject),
                    project_id=practical_project['id'],
                    parent_id=semester_task['id']
                )
                subject_practicals_count = 0
            for class_instance in class_data:
                subject_practicals_count += 1
                class_instance_content = '{}. Practical #{}'.format(
                    subject,
                    subject_practicals_count)

                # Create Todoist-compatible
                # due date string
                class_instance_due_date = class_instance.date + class_data.interval
                if class_instance_due_date < datetime.date.today():
                    class_instance_due_date = datetime.date.today()
                class_instance_due_date = str(class_instance_due_date)

                api.items.add(
                    class_instance_content,
                    project_id=practical_project['id'],
                    parent_id=subject_task['id'],
                    date_string=class_instance_due_date
                )
            api.commit()
