import subprocess

from zdl.utils.io.log import logger


class Terminal:
    @classmethod
    def checkCall(cls, command):
        """执行命令，打印结果和状态，执行错误则抛出异常
        """
        logger.debug(command)
        subprocess.check_call(command, shell=True)

    @classmethod
    def checkOutput(cls, command):
        """执行命令，返回运行结果，而不是打印
        """
        logger.debug(command)
        output = subprocess.check_output(command, shell=True)
        logger.debug(output)
        return output
