import asyncio
import importlib
import os
from datetime import datetime, time as py_time, timedelta
from time import time as timer

from . import app, decorators, models
from .app import QuickpingApp as QuickpingApp
from .decorators.disable import disable as disable
from .decorators.on_event import on_event as on_event
from .decorators.on_idle import on_idle as on_idle
from .decorators.route import route as route
from .decorators.scene import scene as scene
from .decorators.when import when as when
from .models import (
    TV as TV,
    Attribute as Attribute,
    Attributes as Attributes,
    BinarySensor as BinarySensor,
    Blind as Blind,
    Change as Change,
    Clock as Clock,
    Collection as Collection,
    Device as Device,
    Event as Event,
    FancyLight as FancyLight,
    FauxThing as FauxThing,
    Light as Light,
    MotionSensor as MotionSensor,
    Sensor as Sensor,
    Sun as Sun,
    Switch as Switch,
    Thing as Thing,
    Weather as Weather,
)
from .utils import importer
from .utils.comparer import Comparer as Comparer

Time = Clock("clock.default")
Day = Time.day


def load():
    for module in [app, decorators, models, importer]:
        importlib.reload(module)


def reload():
    path = os.path.dirname(os.path.abspath(__file__))
    importer.unload_directory(path, ignore=["app"])


load()


async def wait(seconds: float, *comparables: Comparer) -> bool:
    if not comparables:
        await asyncio.sleep(seconds)
        return True

    comparer = comparables[0]
    for comp in comparables[1:]:
        comparer |= comp

    seconds += timer()
    await asyncio.sleep(0.001)  # let the event loop clear out before we start polling
    result: bool = bool(comparer)
    while not result and timer() < seconds:
        result = bool(comparer)
        await asyncio.sleep(0.1)  # sleep for a bit to let the event loop do its thing

    return result


def any(*comparables: Comparer) -> Comparer:
    if not comparables:
        raise ValueError("Must provide at least one comparables")

    if len(comparables) == 1:
        return comparables[0]

    comparer = comparables[0]
    for comp in comparables[1:]:
        comparer |= comp
    return comparer


def all(*comparables: Comparer) -> Comparer:
    if not comparables:
        raise ValueError("Must provide at least one comparables")

    if len(comparables) == 1:
        return comparables[0]

    comparer = comparables[0]
    for comp in comparables[1:]:
        comparer &= comp
    return comparer


class time(py_time):  # noqa: N801
    def __add__(self, delta: timedelta) -> "time":
        dt = datetime.combine(datetime.today(), self)

        ts = (dt + delta).time()
        return time(ts.hour, ts.minute, ts.second)

    def __sub__(self, delta: timedelta) -> "time":
        dt = datetime.combine(datetime.today(), self)

        ts = (dt - delta).time()
        return time(ts.hour, ts.minute, ts.second)


midnight = time(hour=0)
one_am = time(hour=1)
two_am = time(hour=2)
three_am = time(hour=3)
four_am = time(hour=4)
five_am = time(hour=5)
six_am = time(hour=6)
seven_am = time(hour=7)
eight_am = time(hour=8)
nine_am = time(hour=9)
ten_am = time(hour=10)
eleven_am = time(hour=11)
noon = time(hour=12)
one_pm = time(hour=13)
two_pm = time(hour=14)
three_pm = time(hour=15)
four_pm = time(hour=16)
five_pm = time(hour=17)
six_pm = time(hour=18)
seven_pm = time(hour=19)
eight_pm = time(hour=20)
nine_pm = time(hour=21)
ten_pm = time(hour=22)
eleven_pm = time(hour=23)
one_second = timedelta(seconds=1)
two_seconds = timedelta(seconds=2)
three_seconds = timedelta(seconds=3)
four_seconds = timedelta(seconds=4)
five_seconds = timedelta(seconds=5)
six_seconds = timedelta(seconds=6)
seven_seconds = timedelta(seconds=7)
eight_seconds = timedelta(seconds=8)
nine_seconds = timedelta(seconds=9)
ten_seconds = timedelta(seconds=10)
fifteen_seconds = timedelta(seconds=15)
sixteen_seconds = timedelta(seconds=16)
seventeen_seconds = timedelta(seconds=17)
eighteen_seconds = timedelta(seconds=18)
nineteen_seconds = timedelta(seconds=19)
twenty_seconds = timedelta(seconds=20)
twenty_one_seconds = timedelta(seconds=21)
twenty_two_seconds = timedelta(seconds=22)
twenty_three_seconds = timedelta(seconds=23)
twenty_four_seconds = timedelta(seconds=24)
twenty_five_seconds = timedelta(seconds=25)
twenty_six_seconds = timedelta(seconds=26)
twenty_seven_seconds = timedelta(seconds=27)
twenty_eight_seconds = timedelta(seconds=28)
twenty_nine_seconds = timedelta(seconds=29)
thirty_seconds = timedelta(seconds=30)
thirty_one_seconds = timedelta(seconds=31)
thirty_two_seconds = timedelta(seconds=32)
thirty_three_seconds = timedelta(seconds=33)
thirty_four_seconds = timedelta(seconds=34)
thirty_five_seconds = timedelta(seconds=35)
thirty_six_seconds = timedelta(seconds=36)
thirty_seven_seconds = timedelta(seconds=37)
thirty_eight_seconds = timedelta(seconds=38)
thirty_nine_seconds = timedelta(seconds=39)
forty_seconds = timedelta(seconds=40)
forty_one_seconds = timedelta(seconds=41)
forty_two_seconds = timedelta(seconds=42)
forty_three_seconds = timedelta(seconds=43)
forty_four_seconds = timedelta(seconds=44)
forty_five_seconds = timedelta(seconds=45)
forty_six_seconds = timedelta(seconds=46)
forty_seven_seconds = timedelta(seconds=47)
forty_eight_seconds = timedelta(seconds=48)
forty_nine_seconds = timedelta(seconds=49)
fifty_seconds = timedelta(seconds=50)
fifty_one_seconds = timedelta(seconds=51)
fifty_two_seconds = timedelta(seconds=52)
fifty_three_seconds = timedelta(seconds=53)
fifty_four_seconds = timedelta(seconds=54)
fifty_five_seconds = timedelta(seconds=55)
fifty_six_seconds = timedelta(seconds=56)
fifty_seven_seconds = timedelta(seconds=57)
fifty_eight_seconds = timedelta(seconds=58)
fifty_nine_seconds = timedelta(seconds=59)
one_minute = timedelta(minutes=1)
two_minutes = timedelta(minutes=2)
three_minutes = timedelta(minutes=3)
four_minutes = timedelta(minutes=4)
five_minutes = timedelta(minutes=5)
six_minutes = timedelta(minutes=6)
seven_minutes = timedelta(minutes=7)
eight_minutes = timedelta(minutes=8)
nine_minutes = timedelta(minutes=9)
ten_minutes = timedelta(minutes=10)
fifteen_minutes = timedelta(minutes=15)
sixteen_minutes = timedelta(minutes=16)
seventeen_minutes = timedelta(minutes=17)
eighteen_minutes = timedelta(minutes=18)
nineteen_minutes = timedelta(minutes=19)
twenty_minutes = timedelta(minutes=20)
twenty_one_minutes = timedelta(minutes=21)
twenty_two_minutes = timedelta(minutes=22)
twenty_three_minutes = timedelta(minutes=23)
twenty_four_minutes = timedelta(minutes=24)
twenty_five_minutes = timedelta(minutes=25)
twenty_six_minutes = timedelta(minutes=26)
twenty_seven_minutes = timedelta(minutes=27)
twenty_eight_minutes = timedelta(minutes=28)
twenty_nine_minutes = timedelta(minutes=29)
thirty_minutes = timedelta(minutes=30)
thirty_one_minutes = timedelta(minutes=31)
thirty_two_minutes = timedelta(minutes=32)
thirty_three_minutes = timedelta(minutes=33)
thirty_four_minutes = timedelta(minutes=34)
thirty_five_minutes = timedelta(minutes=35)
thirty_six_minutes = timedelta(minutes=36)
thirty_seven_minutes = timedelta(minutes=37)
thirty_eight_minutes = timedelta(minutes=38)
thirty_nine_minutes = timedelta(minutes=39)
forty_minutes = timedelta(minutes=40)
forty_one_minutes = timedelta(minutes=41)
forty_two_minutes = timedelta(minutes=42)
forty_three_minutes = timedelta(minutes=43)
forty_four_minutes = timedelta(minutes=44)
forty_five_minutes = timedelta(minutes=45)
forty_six_minutes = timedelta(minutes=46)
forty_seven_minutes = timedelta(minutes=47)
forty_eight_minutes = timedelta(minutes=48)
forty_nine_minutes = timedelta(minutes=49)
fifty_minutes = timedelta(minutes=50)
fifty_one_minutes = timedelta(minutes=51)
fifty_two_minutes = timedelta(minutes=52)
fifty_three_minutes = timedelta(minutes=53)
fifty_four_minutes = timedelta(minutes=54)
fifty_five_minutes = timedelta(minutes=55)
fifty_six_minutes = timedelta(minutes=56)
fifty_seven_minutes = timedelta(minutes=57)
fifty_eight_minutes = timedelta(minutes=58)
fifty_nine_minutes = timedelta(minutes=59)
one_hour = timedelta(hours=1)
two_hours = timedelta(hours=2)
three_hours = timedelta(hours=3)
four_hours = timedelta(hours=4)
five_hours = timedelta(hours=5)
six_hours = timedelta(hours=6)
seven_hours = timedelta(hours=7)
eight_hours = timedelta(hours=8)
nine_hours = timedelta(hours=9)
ten_hours = timedelta(hours=10)
eleven_hours = timedelta(hours=11)
twelve_hours = timedelta(hours=12)
