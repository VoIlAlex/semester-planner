from semester_planner import Semester, SemesterPlanner
import json

if __name__ == "__main__":
    semester_data = json.load(open('./data/semester_example_1.json'))
    semester = Semester()
    semester.parse_dict(semester_data)
    semester_planner = SemesterPlanner(semester)
    semester_planner.setup_todoist(
        api_token="ce691d7a35d04f8e5de2661572f3643116de58d3",
        root_project="sandbox"
    )
