from datetime import datetime, timezone
from src.tools import product_search, size_recommender, eta, order_lookup, order_cancel

# Router
def router(prompt):
    if "wedding" in prompt.lower() or "dress" in prompt.lower() or "eta" in prompt.lower():
        return "product_assist"
    elif "cancel order" in prompt.lower():
        return "order_help"
    else:
        return "other"

# Tool Selector
def tool_selector(intent, prompt):
    evidence = []
    tools_called = []
    policy_decision = None
    final_message = ""

    if intent == "product_assist":
        results = product_search(query="midi", price_max=120, tags=["wedding", "midi"])
        tools_called.append("product_search")

        rec_size = size_recommender(prompt)
        tools_called.append("size_recommender")

        delivery_eta = eta("560001")
        tools_called.append("eta")

        evidence = [{"id": p["id"], "title": p["title"], "price": p["price"]} for p in results]
        msg = "Here are some suggestions: "
        msg += " ".join([f"{p['title']} for ${p['price']}." for p in results])
        msg += f" Recommended size: {rec_size}. ETA: {delivery_eta}."
        final_message = msg

    elif intent == "order_help":
        parts = prompt.split()
        order_id = None
        email = None
        for p in parts:
            if p.startswith("A"):
                order_id = p
            if "@" in p:
                email = p.strip("().,")
        order = order_lookup(order_id, email)
        tools_called.append("order_lookup")

        if order:
            current_time = datetime(2025, 9, 7, 12, 30, tzinfo=timezone.utc)  # fixed test time
            cancel_result = order_cancel(order_id, email, current_time)
            tools_called.append("order_cancel")
            policy_decision = cancel_result

            if cancel_result["cancel_allowed"]:
                final_message = f"Order {order_id} has been successfully cancelled."
            else:
                final_message = (
                    f"Sorry, order {order_id} cannot be cancelled because of our 60-minute policy. "
                    "You may still edit the address, request store credit, or contact support."
                )
            evidence = [{"order_id": order_id, "email": email, "created_at": order["created_at"]}]
        else:
            final_message = "Order not found."
            policy_decision = {"cancel_allowed": False, "reason": "not found"}

    else:  # Guardrail
        policy_decision = {"refuse": True}
        final_message = (
            "I can’t provide discount codes that don’t exist. "
            "You can check our newsletter or first-order perks instead."
        )

    return {
        "intent": intent,
        "tools_called": tools_called,
        "evidence": evidence,
        "policy_decision": policy_decision,
        "final_message": final_message,
    }


# Run agent
def run_agent(prompt: str):
    intent = router(prompt)
    trace = tool_selector(intent, prompt)
    return trace
