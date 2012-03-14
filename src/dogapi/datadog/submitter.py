

import logging


logger = logging.getLogger('dogapi.submitter')


class Submitter(object):

    def submit(self, metrics, callback):
        raise NotImplementedError()

class SynchronousSubmitter(Submitter):

    def submit(self, metrics, callback):
        logger.info("submitting metrics synchronously")
        return callback(metrics)

class ThreadedSubmitter(Submitter):

    pass

