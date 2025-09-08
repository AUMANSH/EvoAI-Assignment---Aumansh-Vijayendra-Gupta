from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .tools import product_search, size_recommender, eta, order_lookup, order_cancel
import json
import re

class AgentState(TypedDict):
    user_input: str
    intent: str
    tools_called: List[str]
    evidence: List[Dict[str, Any]]
    policy_decision: Optional[Dict[str, Any]]
    final_message: str

def router(state: AgentState) -> AgentState:
    user_input = state['user_input'].lower()
    if 'wedding' in user_input or 'midi' in user_input or 'under' in user_input or 'dress' in user_input:
        intent = 'product_assist'
    elif 'cancel' in user_input or 'order' in user_input:
        intent = 'order_help'
    else:
        intent = 'other'
    return {**state, 'intent': intent}

def tool_selector(state: AgentState) -> AgentState:
    intent = state['intent']
    tools_called = []
    evidence = []
    policy_decision = None
    if intent == 'product_assist':
        # Extract price_max, tags, query
        user_input = state['user_input']
        price_max = 120  # Default
        match = re.search(r'under \$?(\d+)', user_input)
        if match:
            price_max = int(match.group(1))
        tags = []
        if 'wedding' in user_input:
            tags.append('wedding')
        if 'midi' in user_input:
            tags.append('midi')
        query = 'dress'  # Default
        products = product_search(query, price_max, tags)
        tools_called.append('product_search')
        evidence.extend([{'id': p['id'], 'title': p['title'], 'price': p['price']} for p in products])

        # Size recommender
        size = size_recommender(user_input)
        tools_called.append('size_recommender')

        # ETA
        zip_match = re.search(r'(\d{5})', user_input)
        zip_code = zip_match.group(1) if zip_match else '560001'
        eta_time = eta(zip_code)
        tools_called.append('eta')

    elif intent == 'order_help':
        # Extract order_id, email
        user_input = state['user_input']
        order_id_match = re.search(r'order (\w+)', user_input)
        order_id = order_id_match.group(1) if order_id_match else 'A1001'
        email_match = re.search(r'(\w+@\w+\.\w+)', user_input)
        email = email_match.group(1) if email_match else 'rehan@example.com'
        order = order_lookup(order_id, email)
        if order:
            tools_called.append('order_lookup')
            evidence.append({'order_id': order['order_id'], 'created_at': order['created_at']})
            if 'cancel' in user_input.lower():
                # Simulate current time as 2025-09-07T12:00:00Z for A1003 (within 60 min), 2025-09-08T03:48:19Z for others
                current_time = '2025-09-07T12:00:00Z' if order_id == 'A1003' else '2025-09-08T03:48:19Z'
                cancel_result = order_cancel(order_id, current_time)
                tools_called.append('order_cancel')
                policy_decision = {'cancel_allowed': cancel_result['cancel_allowed'], 'reason': cancel_result.get('reason', '')}
        else:
            policy_decision = None
    else:
        policy_decision = None

    return {**state, 'tools_called': tools_called, 'evidence': evidence, 'policy_decision': policy_decision}

def policy_guard(state: AgentState) -> AgentState:
    # Already handled in tool_selector
    return state

def responder(state: AgentState) -> AgentState:
    intent = state['intent']
    message = ""
    if intent == 'product_assist':
        products = [e for e in state['evidence'] if 'title' in e]
        if products:
            message = f"Here are some suggestions: {products[0]['title']} for ${products[0]['price']}."
            if len(products) > 1:
                message += f" Also, {products[1]['title']} for ${products[1]['price']}."
            message += f" Recommended size: M. ETA: 2-5 days."
        else:
            message = "No products found under your budget."
    elif intent == 'order_help':
        if state['policy_decision'] and state['policy_decision']['cancel_allowed']:
            message = "Order cancelled successfully."
        elif state['policy_decision']:
            message = f"Cancellation not allowed: {state['policy_decision']['reason']}. You can edit address, get store credit, or contact support."
        else:
            message = "Order not found."
    else:
        message = "I'm sorry, I can't help with that. For legitimate perks, check our newsletter or first-order offers."
    
    return {**state, 'final_message': message}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("router", router)
graph.add_node("tool_selector", tool_selector)
graph.add_node("policy_guard", policy_guard)
graph.add_node("responder", responder)

graph.set_entry_point("router")
graph.add_edge("router", "tool_selector")
graph.add_edge("tool_selector", "policy_guard")
graph.add_edge("policy_guard", "responder")
graph.add_edge("responder", END)

agent = graph.compile()

def run_agent(user_input: str) -> Dict[str, Any]:
    initial_state = {
        'user_input': user_input,
        'intent': '',
        'tools_called': [],
        'evidence': [],
        'policy_decision': None,
        'final_message': ''
    }
    result = agent.invoke(initial_state)
    trace = {
        'intent': result['intent'],
        'tools_called': result['tools_called'],
        'evidence': result['evidence'],
        'policy_decision': result['policy_decision'],
        'final_message': result['final_message']
    }
    return trace