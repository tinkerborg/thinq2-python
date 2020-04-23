def memoize(f, *args):
    print("memozie %s" % f.__name__)

    def inner(caller, *args, **kwargs):
        print("caller %s" % caller)
        return f(caller, *args, **kwargs)

    return inner
