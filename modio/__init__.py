from .session import ModioSession


def open(filename, filemode):
    m = ModioSession(filename, filemode)
    return m
