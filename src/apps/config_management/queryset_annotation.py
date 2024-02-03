from django.db.models import QuerySet
from typing import Iterator, TypeVar, Optional

T = TypeVar("T")


class QuerySetType(QuerySet):

    def __iter__(self) -> Iterator[T]:
        pass

    def first(self) -> Optional[T]:
        pass