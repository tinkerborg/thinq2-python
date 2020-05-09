def memoize(func):
    memo = {}

    def inner(*args, **kwargs):
        key = str(dict(args=args, kwargs=kwargs))
        if key not in memo:
            memo[key] = func(*args, **kwargs)
        return memo[key]

    return inner


def end_with(string, end):
    if string.endswith(end):
        return string
    return string + end
