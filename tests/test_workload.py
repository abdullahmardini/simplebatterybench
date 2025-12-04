import pytest

from batben import workload


def test_is_prime_small():
    assert workload.is_prime(2) is True