"""Example of integration between Fabric and Datadog.
"""

from fabric.api import *
from fabric.colors import *
from dogapi.fab import setup, notify

setup(api_key = "YOUR API KEY HERE")

# Make sure @notify is just above @task
@parallel
@notify
@task(default=True, alias="success")
def sweet_task(some_arg):
    """Always succeeds"""
    print(green("My sweet task always runs properly."))

@serial
@notify
@task(alias="failure")
def boring_task(some_arg):
    """Always fails"""
    print(red("My boring task is designed to fail."))
    raise Exception("failure!!!")
