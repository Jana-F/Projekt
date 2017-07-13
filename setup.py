from os.path import join, dirname
from setuptools import setup, find_packages

project_version = __import__("cztwitter")
version = project_version.__versionstr__

with open(join(dirname(__file__), 'requirements.txt')) as f:
    requirements = [x for x in f.readlines() if x[0] not in ('#', '-') and not x.startswith('https://')]

setup(
    name="cztwitter",
    version=version,
    classifiers=['Private :: Do Not Upload'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        cztwitter-manage=cztwitter.cli:manage
    ''',
)
