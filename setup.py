from setuptools import setup, find_packages
import sys

setup(
    name = "dogapi",
    version = "0.1.0",
    packages = find_packages("src", exclude=["dogshell"]),
    package_dir = {'':'src'},
    author = "Datadog, Inc.",
    author_email = "packages@datadoghq.com",
    description = "Python bindings to Datadog's API",
    license = "BSD",
    keywords = "datadog data",
    url = "http://datadoghq.com",
    install_requires= [
        "sphinx==1.0.7"
    ],
)

shell_reqs = ["dogapi==0.1.0"]
if sys.version_info < (2, 7):
    shell_reqs.append("argparse>=1.2")

setup(
    name = "dogshell",
    version = "0.1.0",
    packages = ["dogshell"],
    package_dir = {'':'src'},
    author = "Datadog, Inc.",
    author_email = "packages@datadoghq.com",
    description = "A user-facing command line tool, 'dog', for interacting with the Datadog API.",
    license = "BSD",
    keywords = "datadog data",
    url = "http://datadoghq.com",
    install_requires=shell_reqs,
    entry_points={
        'console_scripts': [
            'dog = dogshell:main',
        ],
    },
)
