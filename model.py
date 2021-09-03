from datetime import date
from dataclasses import dataclass
from typing import NewType, Optional, Set, List

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


@dataclass
class Batch:
    ref: Reference
    sku: Sku
    qty: Quantity
    eta: Optional[date]
    _allocations: Set[OrderLine] = set()

    def __post_init__(self) -> None:
        self._purchased_quantity = self.qty

    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.ref == self.ref

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True

        return self.eta > other.eta

    def __hash__(self) -> int:
        return hash(self.ref)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    batch = next(
        b for b in sorted(batches) if b.can_allocate(line)
    )
    batch.allocate(line)

    return batch.ref
