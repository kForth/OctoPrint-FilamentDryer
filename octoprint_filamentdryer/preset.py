import os
import re

FILE_EXTENSION = "filamentdryer"
DEFAULT_FILENAME_TEMPLATE = f"%(name)s.{FILE_EXTENSION}"


class Preset:
    @staticmethod
    def from_dict(config: dict):
        return Preset(
            config.get("name", None),
            config.get("time", None),
            config.get("temp", None),
        )

    def __init__(self, name: str, time: float, temp: int):
        self.name = str(name)
        self.time = float(time)
        self.temp = int(temp)

    @property
    def display(self):
        return "%s (%0.1fh @ %d°C)" % (self.name, self.time, self.temp)

    def get_filename(self, template=DEFAULT_FILENAME_TEMPLATE):
        return to_snake_case(
            template % {"name": self.name, "time": self.time, "temp": self.temp}
        )

    def get_filepath(self, path, template=DEFAULT_FILENAME_TEMPLATE):
        return os.path.join(path, self.get_filename(template))

    def to_dict(self):
        return {"name": self.name, "time": self.time, "temp": self.temp}

    def __str__(self):
        return '{ "name": %s, "time": %f, "temp": %d }' % (
            self.name,
            self.time,
            self.temp,
        )


# Convert a given string to snake case
# https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-97.php
def to_snake_case(s: str):
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()
