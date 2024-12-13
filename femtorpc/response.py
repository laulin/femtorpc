from collections import namedtuple


Response = namedtuple("Response", ["return_value", "exception"])

Generator = namedtuple("Generator", ["id"])
Function = namedtuple("Function", ["id"])