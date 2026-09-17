from main import Bot 
import logging
import logging.handlers

BOT_LOG_PATH = "./logs/bot.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    BOT_LOG_PATH,
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)


if __name__ == '__main__':
	bot_response = Bot().main()
	logger.info(f"Bot's response: {bot_response}")