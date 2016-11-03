import inspect
import json
import sys


# NOTE: format strings
# +------------+-------------------------+-----------+-----------+
# | Character  |       Byte order        |   Size    | Alignment |
# +------------+-------------------------+-----------+-----------+
# | @          | native                  | native    | native    |
# | =          | native                  | standard  | none      |
# | <          | little-endian           | standard  | none      |
# | >          | big-endian              | standard  | none      |
# | !          | network (= big-endian)  | standard  | none      |
# +------------+-------------------------+-----------+-----------+
#
# +---------+---------------------+---------------------+-------+----------+
# | Format  |       C Type        |    Python type      | Size  |  Notes   |
# +---------+---------------------+---------------------+-------+----------+
# | x       | pad byte            | no value            |       |          |
# | c       | char                | string of length 1  |    1  |          |
# | b       | signed char         | integer             |    1  | (3)      |
# | B       | unsigned char       | integer             |    1  | (3)      |
# | ?       | _Bool               | bool                |    1  | (1)      |
# | h       | short               | integer             |    2  | (3)      |
# | H       | unsigned short      | integer             |    2  | (3)      |
# | i       | int                 | integer             |    4  | (3)      |
# | I       | unsigned int        | integer             |    4  | (3)      |
# | l       | long                | integer             |    4  | (3)      |
# | L       | unsigned long       | integer             |    4  | (3)      |
# | q       | long long           | integer             |    8  | (2), (3) |
# | Q       | unsigned long long  | integer             |    8  | (2), (3) |
# | f       | float               | float               |    4  | (4)      |
# | d       | double              | float               |    8  | (4)      |
# | s       | char[]              | string              |       |          |
# | p       | char[]              | string              |       |          |
# | P       | void *              | integer             |       | (5), (3) |
# +---------+---------------------+---------------------+-------+----------+




class Message(object):
    """Base class for messages."""

    _MSG_ATTRS = []

    def latch(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val) 

    def ToDict(self):
        result = vars(self)
        for key, val in result.items():
            if isinstance(val, Message):
                result[key] = val.ToDict()

        result['_type'] = self.__class__.__name__
        return result
    
    def ToJson(self):
        return json.dumps(self.ToDict(), indent=2, separators=(',', ': '))


class Execute(Message):
    """Signals the server to start execution."""

    def __init__(self, src_tree=''):
        self.src_tree = src_tree


class Shutdown(Message):
    """Signals the server to shut down."""


class Baz(Message):
    def __init__(self, a, b=2, **kwargs):
        self.a = a
        self.b = b
        self.latch(**kwargs)

class Bar(Message):
    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = Baz(1)
        self.latch(**kwargs)

class Foo(Message):
    def __init__(self, w=2, **kwargs):
        self.w = w
        self.u = Bar(3, 4)
        self.latch(**kwargs)

class Decoder(object):
    def __init__(self):
        self.registry = dict()
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if (inspect.isclass(obj) and obj is not Message 
                    and issubclass(obj, Message)):
                self.registry[obj.__name__] = obj

    def FromDict(self, value_dict):
        for key, value in value_dict.items():
            if isinstance(value, dict):
                value_dict[key] = self.FromDict(value)
        type_fn = self.registry[value_dict.pop('_type')]
        return type_fn(**value_dict)

    def FromJson(self, json_str):
        return self.FromDict(json.loads(json_str))
