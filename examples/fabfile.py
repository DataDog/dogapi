"""Example of integration between Fabric and Datadog.
"""

from fabric.api import *
from fabric.colors import *
from dogapi.fab import setup, notify

setup(api_key = "YOUR API KEY HERE")

# Make sure @notify is just below @task
@task(default=True, alias="success")
@notify
def sweet_task(some_arg, other_arg):
    """Always succeeds"""
    print(green("My sweet task always runs properly."))

@task(alias="failure")
@notify
def boring_task(some_arg):
    """Always fails"""
    print(red("My boring task is designed to fail."))
    raise Exception("failure!!!")

env.roledefs.update({
    'webserver': ['localhost']
})

@task(alias="has_roles")
@notify
@roles('webserver')
@hosts('localhost')
def roles_task(arg_1, arg_2):
    run('touch /tmp/fab_test')
