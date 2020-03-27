from distutils.core import setup
from setuptools import find_packages
from setuptools.command.install import install
import semester_planner.config as cfg
import semester_planner.utils as utils
import os

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''


class PostInstallCommand(install):
    def run(self):
        if not os.path.exists(cfg.APPDATA_PATH):
            os.makedirs(cfg.APPDATA_PATH)
        if not os.path.exists(cfg.LOG_DIR_PATH):
            os.makedirs(cfg.LOG_DIR_PATH)
        if not os.path.exists(cfg.CONFIG_FILE_PATH):
            open(cfg.CONFIG_FILE_PATH, 'a+').close()

        config = utils.SemesterPlannerConfig()
        config.save_default_config()

        install.run(self)


setup(
    # Name of the package
    name='semester-planner',

    # Packages to include into the distribution
    packages=find_packages('.'),

    # Start with a small number and increase it with every change you make
    # https://semver.org
    version='1.0.0',

    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    # For example: MIT
    license='MIT',

    # Short description of your library
    description='utility to plan your semester in different apps.',

    # Long description of your library
    long_description=long_description,
    long_description_context_type='text/markdown',

    scripts=['./bin/semester-planner'],


    cmdclass={
        'install': PostInstallCommand
    },

    # Your name
    author='voilalex',

    # Your email
    author_email='ilya.vouk@gmail.com',

    # Either the link to your github or to your website
    url='https://github.com/VoIlAlex',

    # Link from which the project can be downloaded
    download_url='https://github.com/VoIlAlex/semester-planner/archive/v1.0.0.tar.gz',

    # List of keyword arguments
    keywords=['utility', 'todoist', 'cli', 'planner', 'study'],

    # List of packages to install with this one
    install_requires=[
        'todoist-python',
        'via-logger',
        'todoist-colors'
    ],

    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which python versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
