import semester_planner
from semester_planner import Semester, SemesterPlanner
from semester_planner import utils
import functools
import json
import argparse
from .utils import parse_args
import os



def cli():
    args = parse_args()
    config = utils.SemesterPlannerConfig()
    semester_data = json.load(open(args.semester))
    semester = Semester()
    semester.parse_dict(semester_data)
    semester_planner = SemesterPlanner(semester)

    if args.command == 'todoist':
        api_token = args.token if args.token else config['TODOIST']['token']
        root_project = args.root_project if args.root_project else config[
            'TODOIST']['root_project']
        something_toggled = args.labs or args.lectures or args.practical

        setup_todoist = functools.partial(
            semester_planner.setup_todoist,
            api_token=api_token,
            root_project=root_project,
            override=args.override
        )

        if not something_toggled or args.all:
            setup_todoist()
        else:
            setup_todoist(
                labs_project="Labs" if args.labs else None,
                lectures_project="Lectures" if args.lectures else None,
                practical_project="Practical" if args.practical else None
            )
    elif args.command == 'config':
        if args.list:
            print(config.to_string(args.config_section.upper()))
        elif args.config_section == 'todoist':
            if args.token:
                config['TODOIST']['token'] = args.token
            if args.root:
                config['TODOIST']['root_project'] = args.root
        config.save()
