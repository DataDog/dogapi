"""Example of integration between Fabric and Datadog.
"""

from fabric.api import *
from fabric.colors import *
from dogapi.fab import setup, notify

setup(api_key = "YOUR API KEY HERE", application_key = "YOUR APPLICATION KEY HERE")

@notify
@task(alias="success")
def my_task(some_arg):
    """Always succeeds"""
    print(green("My task always runs properly."))

@notify
@task(alias="failure")
def my_other_task(some_arg):
    """Always fails"""
    print(red("My other task is designed to fail."))
    raise Exception("failure!!!")
