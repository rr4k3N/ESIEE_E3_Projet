class Logger:
    ALL     = 0
    DEBUG   = 1
    INFO    = 2
    WARN    = 3
    ERROR   = 4
    NONE    = 5

    def __init__(self, log_level=0, prefix=""):
        self.prefix = prefix
        self.log_level = log_level

    def _make_prefix(level):
        if level == Logger.INFO:
            return "INFO"
        elif level == Logger.WARN:
            return "WARN"
        elif level == Logger.ERROR:
            return "ERROR"

        return ""


    def _log(self, level, message):
        if level < self.log_level: return
        entry = f'[{Logger._make_prefix(level)}]\t{self.prefix} {message}'

        print(entry)

    def debug(self, message): self._log(Logger.DEBUG, message)
    def info(self, message): self._log(Logger.INFO, message)
    def warn(self, message): self._log(Logger.WARN, message)
    def error(self, message): self._log(Logger.ERROR, message)
