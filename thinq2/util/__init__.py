from tempfile import NamedTemporaryFile


def memoize(func):
    memo = {}

    def inner(*args, **kwargs):
        key = str(dict(args=args, kwargs=kwargs))
        if key not in memo:
            memo[key] = func(*args, **kwargs)
        return memo[key]

    return inner


def create_tempfile(content):
    file = NamedTemporaryFile()
    file.write(content.encode("utf8"))
    file.seek(0)
    return file

def end_with(string, end):
    if string.endswith(end):
        return string
    return string + end
