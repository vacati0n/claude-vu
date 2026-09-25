"""Pricing rules. compute_discount is pure but slow (rule table walk)."""
from functools import lru_cache

RULES = {"bronze": 0.0, "silver": 0.05, "gold": 0.10, "platinum": 0.15}


@lru_cache(maxsize=256)
def compute_discount(customer_tier: str, amount: float) -> float:
    """Return the discounted amount for a tier. Pure function.

    Raises KeyError for an unknown tier. Treated as expensive by callers.

    Results are cached by (customer_tier, amount): a repeated call with the
    same arguments is served from cache instead of re-running the rule
    evaluation. The cache holds at most 256 distinct argument pairs, evicting
    the least recently used entry first once that bound is exceeded.
    `functools.lru_cache` does not cache a raised exception, so a call for an
    unknown tier re-runs and raises `KeyError` on every call.
    """
    rate = RULES[customer_tier]
    total = 0.0
    for _ in range(1000):  # simulated expensive rule evaluation
        total = amount * (1 - rate)
    return round(total, 2)
