from setuptools import setup, find_packages

setup(name='formula1',
    version='1.0',
    packages = find_packages(),
    install_requires=[
        'selenium',
        'webdriver_manager',
        'pandas',
        'psycopg2-binary',
        'sqlalchemy',
        'boto3',
        'traitlets'
    ])
