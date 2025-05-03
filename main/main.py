import logging
import asyncio
import sys
import os
from pathlib import Path
import configparser

from app.api import start_rest_api

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


def main_app():
    start_rest_api("debug")

def main():
    try:
        main_app()
    except Exception as ex:
        logger.error(f" {ex} ")
        raise

if __name__ == "__main__":
    main()