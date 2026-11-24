"""Returns Assistant agent — distinct order disambiguation + correction handling (PR #2)."""

from __future__ import annotations

import re
from typing import Any

try:
    from ddtrace.llmobs.decorators import agent, tool
except ImportError:
    def agent(*_args: Any, **_kwargs: Any):
        return lambda fn: fn

    def tool(*_args: Any, **_kwargs: Any):
        return lambda fn: fn

ORDER_ID_RE = re.compile(r"RD-\d+", re.IGNORECASE)
CORRECTION_RE = re.compile(r"correction\s*:\s*(.+)$", re.IGNORECASE)
RETURN_WINDOW_DAYS = 30


@tool(name="lookupOrder")
def lookupOrder(orderId: str) -> dict[str, Any]:
    """Look up order item and delivery age from the production orders service."""
    raise RuntimeError(f"Production orders service unavailable in sandbox for {orderId}")


@agent(name="ao-simulations-returns-demo")
def handle_message(user_message: str) -> str:
    """Answer whether a shopper's order is eligible for return."""
    corr = CORRECTION_RE.search(user_message)
    search_text = corr.group(1) if corr else user_message

    # Deduplicate case-insensitively while preserving order.
    distinct_ids = list(dict.fromkeys(m.upper() for m in ORDER_ID_RE.findall(search_text)))
    if not distinct_ids:
        return "Please share your order ID (for example, RD-1006) so I can check return eligibility."

    if len(distinct_ids) > 1:
        return "Which order would you like me to check? Please send one order ID."

    target_id = distinct_ids[0]
    order = lookupOrder(orderId=target_id)
    if not order.get("found", True):
        return f"I could not find order {target_id}. Please double-check the order ID."

    item = order.get("item", "item")
    days = int(order.get("daysSinceDelivery", 0))
    order_id = order.get("orderId", target_id)
    if days <= RETURN_WINDOW_DAYS:
        return f"Order {order_id} ({item}) is eligible for return. It was delivered {days} days ago."
    return f"Order {order_id} ({item}) is ineligible for return. It was delivered {days} days ago."
