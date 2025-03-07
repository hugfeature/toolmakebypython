def outer(x):
    def inner(y):
        return x + y

    return inner


print(outer(5)(6))


def debug(func):
    def wrapper():
        print("[DEBUG]: enter {}()".format(func.__name__))
        return func()

    return wrapper


@debug
def hello():
    print("hello")


hello()
