import logging
logging.basicConfig()

import common
import facade
import metric
import event
from facade import init
from simpleclient import SimpleClient

dog = SimpleClient()
