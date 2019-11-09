import logging
import json
import sys

def load_data() -> dict:
    with open("secrets.json", "r") as f:
        data = json.load(f)
    if data is None:
        discord_logger.critical("Could not load data parameters! Aborting")
        sys.exit(1)
    if data.get("token") is None:
        discord_logger.critical("Could not load token! Aborting")
        sys.exit(1)
    if data.get("owner") is None:
        discord_logger.warning("No owner specified. Will assume owner from Discord application info.")
    if data.get("primaryServer") is None:
        discord_logger.error("No primary server specified. This bot will run without a primary server.")
    if not isinstance(data.get("portNum"), int):
        data["portNum"] = 8080
        discord_logger.warning("Invalid port number. This bot will use the default port, port 8080.")
    if data.get("prefix") is None:
        discord_logger.warning("No prefix. This bot will use the default prefix, 'p?'.")
        data["prefix"] = "p?"
    return data

class ColoredTerminalLogger(logging.Logger):
    FAIL = "\033[38;5;9m"
    INFO = "\033[38;5;244m"
    WARN = "\033[38;5;214m"
    RESET = "\033[0m"
    DEBUG = "\033[38;5;27m"
    BOLD = "\033[1m"
    UNBOLD = "\033[21m"
    ULINE = "\033[4m"
    UNLINE = "\033[24m"
    
    @staticmethod
    def test():
        print(ColoredTerminalLogger.FAIL + "FAILURE!!!" + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.WARN + "WARNING!" + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.INFO + "Things you might need to know." + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.RESET + "Everything is fine." + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.DEBUG + "Anything and everything, here." + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.BOLD + "REALLY IMPORTANT." + ColoredTerminalLogger.UNBOLD + " Or not." + ColoredTerminalLogger.RESET)
        print(ColoredTerminalLogger.ULINE + "Read this." + ColoredTerminalLogger.UNLINE + " Or don't." + ColoredTerminalLogger.RESET)

    def info(self, message: str, *args, **kwargs):
        if (self.getEffectiveLevel() <= logging.INFO):
            logging.Logger.info(self, ColoredTerminalLogger.INFO + message + ColoredTerminalLogger.RESET, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        if (self.getEffectiveLevel() <= logging.CRITICAL):
            logging.Logger.critical(self, ColoredTerminalLogger.FAIL + message + ColoredTerminalLogger.RESET, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        if (self.getEffectiveLevel() <= logging.DEBUG):
            logging.Logger.debug(self, ColoredTerminalLogger.DEBUG + message + ColoredTerminalLogger.RESET, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> str:
        if (self.getEffectiveLevel() <= logging.WARNING):
            logging.Logger.warning(self, ColoredTerminalLogger.WARN + message + ColoredTerminalLogger.RESET, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> str:
        if (self.getEffectiveLevel() <= logging.ERROR):
            logging.Logger.error(self, ColoredTerminalLogger.FAIL + message + ColoredTerminalLogger.RESET, *args, **kwargs)

logging.setLoggerClass(ColoredTerminalLogger)
discord_logger = logging.getLogger("discord")
data = load_data()

if __name__ == "__main__":
    ColoredTerminalLogger.test()