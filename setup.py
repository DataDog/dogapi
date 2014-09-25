from setuptools import setup, find_packages
import sys

install_reqs = [
    "decorator>=3.3.2"
]
test_reqs = [
     "Pillow>=2.5.0"
]

if sys.version_info[0] == 2:
    # simplejson is not python3 compatible
    install_reqs.append("simplejson>=2.0.9")

if [sys.version_info[0], sys.version_info[1]] < [2, 7]:
    install_reqs.append("argparse>=1.2")

setup(
    name = "dogapi",
    version = "1.8.5",
    packages = find_packages("src"),
    package_dir = {'':'src'},
    author = "Datadog, Inc.",
    author_email = "packages@datadoghq.com",
    description = "Python bindings to Datadog's API and a user-facing command line tool.",
    license = "BSD",
    keywords = "datadog data",
    url = "http://www.datadoghq.com",
    install_requires = install_reqs,
    tests_require = test_reqs,
    entry_points = {
        'console_scripts': [
            'dog = dogshell:main',
            'dogwrap = dogshell.wrap:main',
        ],
    },
)
