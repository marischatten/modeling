import json
import numpy


def get_data(filename) -> object:
    with open(filename, "r", encoding='utf8') as f:
        return json.load(f)


# def write_data(filename):
#   with open(filename,"w",encoding='utf8') as f:

def euclidean_distance(x1: object, x2: object, y1: object, y2: object) -> object:
    a = numpy.array((x1, y1))
    b = numpy.array((x2, y2))
    return numpy.linalg.norm(a - b)
