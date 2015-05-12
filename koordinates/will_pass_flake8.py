def bar():
    '''
    This won't pass a flake test
    '''
    a = 1 + 2
    return a


if __name__ == "__main__":
    print bar()
