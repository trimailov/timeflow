from setuptools import setup

setup(
    name='timeflow',
    packages=['timeflow'],
    version='0.1',
    description='Small CLI time logger',
    author='Justas Trimailovas',
    author_email='j.trimailvoas@gmail.com',
    url='https://github.com/trimailov/timeflow',
    keywords=['timelogger', 'logging', 'timetracker', 'tracker'],
    py_modules=['timeflow'],
    entry_points='''
        [console_scripts]
        timeflow=timeflow.main:main
        tf=timeflow.main:main
    ''',
)
