import os

from tempfile import TemporaryDirectory, mkstemp


class TempDir:
    def __init__(self):
        self._dir = TemporaryDirectory()

    def file(self, content: str = None):
        fh, path = mkstemp(dir=self._dir.name)
        if content is not None:
            os.write(fh, str.encode(content))
        os.close(fh)
        return path
