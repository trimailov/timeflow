from setuptools import setup

setup(
    name='timeflow',
    version='0.1',
    py_modules=['timeflow'],
    entry_points='''
        [console_scripts]
        timeflow=timeflow.main:main
    ''',
)
