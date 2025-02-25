from datetime import datetime, time

import pytest
from freezegun import freeze_time

from quickping.services import Clock


@pytest.mark.parametrize(
    "frozen_time, is_active",
    [
        ("2024-02-24 05:00:00", False),
        ("2024-02-24 07:00:00", True),
        ("2024-02-24 10:00:00", True),
        ("2024-02-24 14:00:00", True),
        ("2024-02-24 15:00:00", True),
        ("2024-02-24 18:00:00", False),
    ],
)
def test_clock(frozen_time, is_active):
    Time = Clock("clock.test")

    with freeze_time(frozen_time):
        assert bool(time(7) <= Time < time(15)) == is_active
