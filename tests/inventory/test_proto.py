from lilacs.inventory.proto import InventoryResolver
from unittest import TestCase


class TestProto(TestCase):
    def test_pagination(self):
        self.assertEqual(
            InventoryResolver.pagination(2, 30, 150), (30, 60, 2, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            InventoryResolver.pagination(4, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            InventoryResolver.pagination(5, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            InventoryResolver.pagination(5, 100, 150), (100, 150, 2, 50),
            " Pagination should give corrected page and correct count"
        )
        self.assertEqual(
            InventoryResolver.pagination(5, 110, 150), (40, 50, 5, 10),
            " Pagination should use default limit (10) when getting too much "
        )