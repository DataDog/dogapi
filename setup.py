from setuptools import setup, find_packages
import sys

reqs = []
if sys.version_info[0] == 2:
    # simplejson is not python3 compatible
    reqs.append("simplejson>=2.0.9")
reqs.append("decorator>=3.3.2")
if [sys.version_info[0], sys.version_info[1]] < [2, 7]:
    reqs.append("argparse>=1.2")

setup(
    name = "dogapi",
    version = "1.6.1",
    packages = find_packages("src"),
    package_dir = {'':'src'},
    author = "Datadog, Inc.",
    author_email = "packages@datadoghq.com",
    description = "Python bindings to Datadog's API and a user-facing command line tool.",
    license = "BSD",
    keywords = "datadog data",
    url = "http://www.datadoghq.com",
    install_requires = reqs,
    entry_points={
        'console_scripts': [
            'dog = dogshell:main',
            'dogwrap = dogshell.wrap:main',
        ],
    },
)
