import subprocess

from zdl.utils.io.log import logger


class Terminal:
    @classmethod
    def checkCall(cls, command):
        logger.debug(command)
        subprocess.check_call(command, shell=True)

    @classmethod
    def checkOutput(cls, command):
        logger.debug(command)
        output = subprocess.check_output(command, shell=True)
        logger.debug(output)
        return output
