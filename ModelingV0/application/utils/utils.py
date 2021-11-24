import json
import numpy

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def get_data(filename) -> object:
    with open(filename, "r", encoding='utf8') as f:
        return json.load(f)


def write_data(filename, obj):
    with open(filename, "w", encoding='utf8') as f:
        json.dump(obj, f)


def euclidean_distance(x1: object, x2: object, y1: object, y2: object) -> object:
    a = numpy.array((x1, y1))
    b = numpy.array((x2, y2))
    return numpy.linalg.norm(a - b)