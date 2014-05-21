"""Example of integration between Fabric and Datadog.
"""

from fabric.api import *
from fabric.colors import *
from dogapi.fab import setup, notify

setup(api_key = "YOUR API KEY HERE")

# Make sure @notify is just below @task
@notify
@task(default=True, alias="success")
def sweet_task(some_arg, other_arg):
    """Always succeeds"""
    print(green("My sweet task always runs properly."))

@notify
@task(alias="failure")
def boring_task(some_arg):
    """Always fails"""
    print(red("My boring task is designed to fail."))
    raise Exception("failure!!!")

env.roledefs.update({
    'webserver': ['localhost']
})

@notify
@task(alias="has_roles")
@roles('webserver')
@hosts('localhost')
def roles_task(arg_1, arg_2):
    run('touch /tmp/fab_test')
