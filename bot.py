from main import Bot, Reader, Sender, Config, ProximityRelay
import logging
import logging.handlers
from datetime import datetime

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

import time

TARGET_STOP_TIME = 1 * 60 * 60           # scan within seconds specified

def in_target_time(iso_time: str) -> bool:
    dt = datetime.fromisoformat(iso_time)
    unix_past_time = dt.timestamp()
    now = time.time()

    
    time_elapsed = now - unix_past_time

    if time_elapsed > TARGET_STOP_TIME:
        return False
    else: 
        return True


def stop_bot() -> bool: # need time, wd geohash, content # convert the time into unix-based time then subtract to current unix
    fetched_data_from_api = Reader().main()
    if not fetched_data_from_api:
        return False
    
    fetched_data_from_api.reverse()

    for fetched_datum in fetched_data_from_api:

        if fetched_datum["geohash"] == "wd" and fetched_datum["content"] == ".override" and in_target_time(fetched_datum["timestamp"]):
            return False
        if fetched_datum["geohash"] == "wd" and fetched_datum["content"] == ".stop" and in_target_time(fetched_datum["timestamp"]):
            return True

# in_target_time(fetched_datum["timestamp"])




    

	
if __name__ == '__main__':
    stop_message = "Ang bot ay pansamantalang hindi makakapag-send ng mga mensahe sa loob ng isang oras... I-extend? .stop"

    if stop_bot():
        send_stopped_response = Sender().send(
                                20000,
                                Bot().tags,
                                stop_message,
                                ProximityRelay().find_closest_relay(Bot().MAIN_GEOHASH)
                            )
        logger.info("Bot was stopped")
    else:
        bot_response = Bot().main()
        logger.info(f"Bot's response: {bot_response}")