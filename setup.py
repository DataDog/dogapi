from setuptools import setup, find_packages
setup(
    name = "dogapi",
    version = "0.1.0",
    packages = find_packages("src"),
    package_dir = {'':'src'},
    author = "Datadog, Inc.",
    author_email = "packages@datadoghq.com",
    description = "Python bindings to Datadog's API",
    license = "BSD",
    keywords = "datadog data",
    url = "http://datadoghq.com",
)

