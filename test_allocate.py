from datetime import date, timedelta
import pytest
from model import Batch, OrderLine, OutOfStock, Quantity, Reference, Sku, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(Reference("in-stock-batch"), Sku("RETRO-CLOCK"), Quantity(100), eta=None)
    shipment_batch = Batch(Reference("shipment-batch"), Sku("RETRO-CLOCK"), Quantity(100), eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(Reference("speedy-batch"), Sku("MINIMALIST-SPOON"), Quantity(100), eta=today)
    medium = Batch(Reference("normal-batch"), Sku("MINIMALIST-SPOON"), Quantity(100), eta=tomorrow)
    latest = Batch(Reference("slow-batch"), Sku("MINIMALIST-SPOON"), Quantity(10), eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 100
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(Reference("in-stock-batch-ref"), Sku("HIGHBROW-POSTER"), Quantity(100), eta=None)
    shipment_batch = Batch(Reference("shipment-batch-ref"), Sku("HIGHBROW-POSTER"), Quantity(100), eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.ref


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(Reference("batch1"), Sku("SMALL-FORK"), Quantity(10), eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])
