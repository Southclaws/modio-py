class ModioError(Exception):
    pass


class InvalidModioFormat(ModioError):
    pass


class IncorrectModioVersion(ModioError):
    pass


class ModioTagOverflow(ModioError):
    pass


class UnknownDataType(ModioError):
    pass
