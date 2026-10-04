from collections.abc import Iterator

import pytest


class LogCapture:
    """Reads back what init_logging() wrote to stdout.

    init_logging() installs its handler on sys.stdout at call time, so tests
    use pytest's capsys to substitute that stream rather than adding a handler
    of their own -- a private handler would bypass the level filtering and
    handler wiring under test. Records are written synchronously (no enqueue
    thread), so they are on the stream by the time the test body returns.
    """

    def __init__(self, capsys: pytest.CaptureFixture[str]) -> None:
        self._capsys = capsys

    def records(self) -> list[dict]:
        import json

        out = self._capsys.readouterr().out
        return [json.loads(line) for line in out.splitlines() if line.startswith("{")]

    def messages(self) -> list[str]:
        return [record["message"] for record in self.records()]


@pytest.fixture
def log_capture(capsys: pytest.CaptureFixture[str]) -> Iterator[LogCapture]:
    yield LogCapture(capsys)
