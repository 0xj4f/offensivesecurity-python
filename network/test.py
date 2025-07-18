def primes(n: int):
    """Return a list of the first primes"""
    sieve = [True] * n

    res = []
    for i in range(2, n):
        if sieve[i]:
            res
