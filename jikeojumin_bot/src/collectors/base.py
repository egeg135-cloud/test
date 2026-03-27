from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from src.models import PostRecord


class BaseCollector(ABC):
    platform: str

    @abstractmethod
    def collect(self, keywords: list[str], limit: int = 20) -> Iterable[PostRecord]:
        raise NotImplementedError
