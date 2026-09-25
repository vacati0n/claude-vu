import unittest
from app.pricing import compute_discount


class DiscountTests(unittest.TestCase):
    def setUp(self):
        compute_discount.cache_clear()

    def test_gold(self):
        self.assertEqual(compute_discount("gold", 100.0), 90.0)

    def test_unknown_tier(self):
        with self.assertRaises(KeyError):
            compute_discount("wood", 10.0)


class DiscountCacheTests(unittest.TestCase):
    """D-001, D-002, D-003: memoization, its 256-entry LRU bound, and the
    unchanged raise-every-call behaviour for an unknown tier."""

    def setUp(self):
        compute_discount.cache_clear()

    def test_repeated_call_is_served_from_cache(self):
        first = compute_discount("silver", 200.0)
        info_after_first = compute_discount.cache_info()

        second = compute_discount("silver", 200.0)
        info_after_second = compute_discount.cache_info()

        self.assertEqual(first, second)
        self.assertEqual(info_after_first.misses, 1)
        self.assertEqual(info_after_first.hits, 0)
        self.assertEqual(info_after_second.misses, 1)
        self.assertEqual(info_after_second.hits, 1)

    def test_cache_bound_is_256_with_lru_eviction(self):
        self.assertEqual(compute_discount.cache_info().maxsize, 256)

        for amount in range(300):
            compute_discount("gold", float(amount))

        info = compute_discount.cache_info()
        self.assertEqual(info.currsize, 256)

        # amount=0.0 was the first (least recently used) entry inserted and
        # must have been evicted once the 256-entry bound was exceeded.
        misses_before = compute_discount.cache_info().misses
        compute_discount("gold", 0.0)
        misses_after = compute_discount.cache_info().misses
        self.assertEqual(misses_after, misses_before + 1)

    def test_unknown_tier_raises_on_every_call_and_is_never_cached(self):
        with self.assertRaises(KeyError):
            compute_discount("wood", 10.0)
        misses_after_first = compute_discount.cache_info().misses

        with self.assertRaises(KeyError):
            compute_discount("wood", 10.0)
        misses_after_second = compute_discount.cache_info().misses

        self.assertEqual(misses_after_second, misses_after_first + 1)
