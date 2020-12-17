def test_file_logger():
    import time
    from zdl.utils.io.log import logger, addFileLogger

    log_file = 'test/this_is_a_pytest_file.log'
    log_content = f'{time.time()} succeed'

    addFileLogger(log_file)
    logger.info(log_content)

    with open(log_file) as f:
        assert f.read().endswith(log_content + '\n')
