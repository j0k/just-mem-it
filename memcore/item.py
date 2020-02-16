# {
#   "id" : 0,
#   "title" : "skill 1",
#   "description" : "it's simple",
#   "date" : 12345621,
#   "type" : {
#     "time" : "normal",
#     "obj" : "skill"
#   },
#   "iter" : [],
#   "active" : 1,
#   "paused" : 0
# }

import typing as t
import time

import inspect
import typing
from contextlib import suppress
from functools import wraps

from dataclasses import dataclass, asdict, field, InitVar
import dataclasses

from dataclasses_json import dataclass_json


# https://stackoverflow.com/questions/50563546/validating-detailed-types-in-python-dataclasses
# https://www.geeksforgeeks.org/data-classes-in-python-set-3-dataclass-fields/

def enforce_types(callable):
    spec = inspect.getfullargspec(callable)

    def check_types(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            with suppress(KeyError):  # Assume un-annotated parameters can be any type
                type_hint = spec.annotations[name]
                if isinstance(type_hint, typing._SpecialForm):
                    # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    # In case of non-typing types (such as <class 'int'>, for instance)
                    actual_type = type_hint
                # In Python 3.8 one would replace the try/except with
                # actual_type = typing.get_origin(type_hint) or type_hint
                if isinstance(actual_type, typing._SpecialForm):
                    # case of typing.Union[…] or typing.ClassVar[…]
                    actual_type = type_hint.__args__

                if not isinstance(value, actual_type):
                    raise TypeError('Unexpected type for \'{}\' (expected {} but found {})'.format(name, type_hint, type(value)))

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_types(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper

    if inspect.isclass(callable):
        callable.__init__ = decorate(callable.__init__)
        return callable

    return decorate(callable)

@enforce_types
@dataclass
class Type(object):
    time : str = "default"
    obj  : str = "skill"

@enforce_types
@dataclass
class Date(object):
    create : float = time.time()

@enforce_types
@dataclass
class NextTimeItem(object):
    create : t.List[int]

    @staticmethod
    def default():
        return [0,0]

@enforce_types
@dataclass_json
@dataclass
class Item(object):
    title         : str
    description   : str  = ""
    hint          : str  = ""
    scale         : str  = "Scale Rational Long 2x"
    type          : Type = field(default_factory=Type)
    paused        : bool = True
    date          : Date = field(default_factory=Date)
    reminders     : t.List[float] = field(default_factory=list)
    nextTimes     : t.List[t.List[float]] = field(default_factory = list)
    lastIntervals : t.List[float] = field(default_factory=list)
    idx           : int = 0

@enforce_types
@dataclass_json
@dataclass
class Items(object):
    create : t.List[Item]


o1 = Item(title="", description="12", type = Type(obj="", time="12"), paused=True)
print(asdict(o1))
