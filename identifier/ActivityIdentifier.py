from typing import Callable
from tincan import Statement


class ActivityIdentifier:
    def __init__(self) -> None:
        pass

    def process_statement(self, st_getter: Callable[[int], Statement | None], i: int):
        pass
