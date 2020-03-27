import os

APPDATA_PATH = os.path.join(os.getenv('HOME'), '.semester-planner')
LOG_DIR_PATH = os.path.join(APPDATA_PATH, 'logs')
DEFAULT_LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, 'semester-planner.log')
CONFIG_FILE_PATH = os.path.join(APPDATA_PATH, '.config')

DEFAULT_LOCAL_CONFIG = {
    'TODOIST': {
        'token': 'null',
        'root_project': 'University'
    }
}
