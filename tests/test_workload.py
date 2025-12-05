from batben import workload


def test_is_prime():
    assert workload.is_prime(2) is True
    assert workload.is_prime(4) is False
    # seems dumb but like... I've seen LLMs propose that 6 is a prime number
    # especially when you tell it that it shouldn't shortcut via %2 and %3
    # it would remove the shortcut, but not change the behavior ¯\_(ツ)_/¯
    assert workload.is_prime(6) is False
    assert workload.is_prime(41) is True
    assert workload.is_prime(42) is False
