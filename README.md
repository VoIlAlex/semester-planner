# Semester Planner

Utility to plan your semester in different apps.

## Installation

To install semester-planner type the following in the terminal:

```bash
pip install semester-planner
```

## Usage

Before planning your semester in different apps you should.

### Semester configuration

The configuration has the following structure:

```json
{
    "semester": {
        "number": 6,
        "start": "01/27/2020",
        "end": "05/17/2020"
    },
    "classes": {
        "labs": [...],
        "practical": [...],
        "lectures": [...]
    }
}
```

* `semester` - meta-information about the semester.
* `classes` - list of classes.

Where each class has the following structure:

```json
{
    "subject": "History",
    "schedule": {
        "0": [{
            "start": "01/27/2020",
            "end": "05/17/2020",
            "interval": 7
        }],
        "1": [],
        "2": [],
        "3": [{
            "start": "04/02/2020",
            "end": "05/17/2020",
            "interval": 7
        }],
        "4": [],
        "5": [],
        "6": []
    }
}
```

* `subject` - is the name of the subject.
* `"0".."6"` - the days of week.

### Todoist planner

To configure todoist token use the following command:

```bash
semester-planner config todoist --token <todoist-api-token>
```

You can find `<todoist-api-token>` [here](https://todoist.com/prefs/integrations).

To setup everything in Todoist type this in your terminal:

```bash
semester-planner todoist --all
```

It will create project ("University" by default) and subprojects for labs, lectures and
practical classes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE.md)
