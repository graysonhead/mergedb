class MdbError(Exception):
    """
    Base class for MergeDB errors
    """

    def __init__(self, msg):
        self.msg = msg


class MdbLoadError(MdbError):

    def __str__(self):
        return self.msg


class MdbMergeError(MdbError):

    def __str__(self):
        return self.msg


class MdbDeclarationError(MdbError):

    def __str__(self):
        return self.msg