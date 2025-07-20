# config.py
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

LOG_LEVEL = logging.INFO
LLM_MODEL = "gpt-4.1-nano"
STT_MODEL = "nova-2"
TTS_MODEL = "aura-asteria-en"


def configure_logging():
    logging.basicConfig(level=LOG_LEVEL)
    return logging.getLogger("multiprompt-agent")
