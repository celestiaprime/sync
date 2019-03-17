from .infra.data_manager import DataManager

import websockets
import logging
import os

logger = logging.getLogger()


def init_logger(level, path):
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = None
    try:
        fh = logging.FileHandler(path)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    except:
        logger.debug("Failed to create log file")
    # create console handler with a provided log level
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # add the handlers to the logger
    logger.addHandler(ch)


path = os.path.join(os.getcwd(), "log.txt")
init_logger(logging.DEBUG, path)


async def run_client():
    ws = await websockets.connect("ws://localhost:8765")
    data_manager = DataManager(ws, mode="client")
    logger.debug("Client init complete")
    await data_manager.channel.run_loop()


async def run_server():
    ws = await websockets.serve("ws://localhost:8765")
    data_manager = DataManager(ws, mode="client")
    logger.debug("Client init complete")
    await data_manager.channel.run_loop()