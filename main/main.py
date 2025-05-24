import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import asyncio
import sys
import os
from pathlib import Path
import configparser
from app.api import start_rest_api

levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL)
log_file_path = Path(__file__).parent.parent / "logs" / "app.log"
log_file_path.parent.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(log_file_path, mode='w')
file_handler.name = "file"  # Set a custom name attribute

with open(log_file_path, 'w'):
    pass

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        file_handler,  # Log to file
        logging.StreamHandler()             # Log to console
    ]
)

logger = logging.getLogger(__name__)

def get_param()->str:
    try:
        args = sys.argv[1]
        if args.endswith(".jinit"):
            return args
        else:
            return args + "_profile"
    except IndexError:
        raise IndexError("Give profile name")

def resolve_profile_path(main_app_dir:str) -> str:
    arg_profile = get_param()
    profile_path = os.path.join(main_app_dir,"profiles", arg_profile)
    if not os.path.exists(profile_path):
        raise  FileNotFoundError(f"No Profile found {profile_path}")
    return profile_path

def init_app(main_directory: str, logging_bootstrap: bool = True)->None:
    profile_name = resolve_profile_path(main_directory)

def main_app():
    print("Starting main app")
    start_rest_api("DEBUG")

def main():
    logger.info("Starting application...")
    try:
        main_app()
    except Exception as ex:
        logger.error(f" {ex} ")
        raise

if __name__ == "__main__":
    main()