import logging

def setup_logging():
    #Software information
    # log_dir = "logs"
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    
    #Configure the log format, including time, file name, line number, log level and message
    logging_format = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    
    #Configure basic logging settings
    logging.basicConfig(
        level=logging.DEBUG,
        format=logging_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('日志.log', mode='a', encoding='utf-8'),
            #Also output to the console
            logging.StreamHandler()  
        ]
    )
    
    #Get logger instance
    logger = logging.getLogger(__name__)
    return logger

def main():
    #Set log configuration
    logger = setup_logging()
    
    #Test different levels of logging
    logger.debug("这是一个调试信息")
    logger.info("程序正常启动")
    logger.warning("这是一个警告信息")
    logger.error("发生了一个错误")
    logger.critical("发生了一个严重错误")
    
    #Simulate a function call to generate logs
    def test_function():
        logger.info("这是在test_function中产生的日志")
    
    test_function()

if __name__ == "__main__":
    main()