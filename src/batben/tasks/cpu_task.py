import math

def is_prime(n: int) -> bool:
    """
    quick and dirty prime check. this doesn't need to be bullet proof
    I also don't care about negative numbers
    """
    if n <= 3:
        return True
    sqrt = int(math.sqrt(n))
    for i in range(2, sqrt + 1):
        if n % i == 0:
            return False
    return True