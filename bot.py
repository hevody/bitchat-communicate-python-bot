from main import Bot, Reader, Sender, Config, ProximityRelay, CryptographySpecific
import logging
import logging.handlers
from datetime import datetime, timedelta
import os

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

BOT_PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")
BOT_PUBKEY = CryptographySpecific().retrieve_signer_and_pubkey(BOT_PRIVATE_KEY)[1]

def in_target_time(iso_time: str) -> bool:
    dt = datetime.fromisoformat(iso_time)
    unix_past_time = dt.timestamp()
    now = time.time()

    
    time_elapsed = now - unix_past_time

    if time_elapsed > TARGET_STOP_TIME:
        return False
    else: 
        return True

def get_stop_time(iso_time: str) -> str:
    utc_time = datetime.strptime(iso_time.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
    manila_time_with_hour_increment = utc_time + timedelta(hours=8) + timedelta(hours=1)
    with_meridian_time = manila_time_with_hour_increment.strftime("%I:%M %p").lstrip('0')
    return with_meridian_time

def stop_bot() -> tuple[bool, str]: # need time, wd geohash, content # convert the time into unix-based time then subtract to current unix
    fetched_data_from_api = Reader().main()
    if not fetched_data_from_api:
        return (False,)
    
    fetched_data_from_api.reverse()

    for fetched_datum in fetched_data_from_api:
        if fetched_datum["nostrPubkey"] == BOT_PUBKEY:
            continue

        if fetched_datum["geohash"] == "wd" and fetched_datum["content"].endswith(".override") and in_target_time(fetched_datum["timestamp"]):
            return (False,)
        if fetched_datum["geohash"] == "wd" and fetched_datum["content"].endswith(".stop") and in_target_time(fetched_datum["timestamp"]):
            return (True, get_stop_time(fetched_datum["timestamp"]))
	
if __name__ == '__main__':
    if stop_bot()[0]:
        stop_message = f"Ang bot ay pansamantalang hindi makakapagpadala ng mga mensahe hanggang {stop_bot()[1]} ... I-extend? send .stop"
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