"""Returns Assistant agent (baseline implementation).

Instrumented with Datadog LLM Observability decorators. During Datadog Simulations,
the runtime shim intercepts `lookupOrder` before real database code runs.
"""

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
RETURN_WINDOW_DAYS = 30


@tool(name="lookupOrder")
def lookupOrder(orderId: str) -> dict[str, Any]:
    """Look up order item and delivery age from the production orders service."""
    raise RuntimeError(f"Production orders service unavailable in sandbox for {orderId}")


@agent(name="ao-simulations-returns-demo")
def handle_message(user_message: str) -> str:
    """Answer whether a shopper's order is eligible for return."""
    ids = [m.upper() for m in ORDER_ID_RE.findall(user_message)]
    if not ids:
        return "Please share your order ID (for example, RD-1006) so I can check return eligibility."

    # Baseline bug: blindly picks the first order ID mentioned.
    order = lookupOrder(orderId=ids[0])
    if not order.get("found", True):
        return f"I could not find order {ids[0]}. Please double-check the order ID."

    item = order.get("item", "item")
    days = int(order.get("daysSinceDelivery", 0))
    order_id = order.get("orderId", ids[0])
    if days <= RETURN_WINDOW_DAYS:
        return f"Order {order_id} ({item}) is eligible for return. It was delivered {days} days ago."
    return f"Order {order_id} ({item}) is ineligible for return. It was delivered {days} days ago."
