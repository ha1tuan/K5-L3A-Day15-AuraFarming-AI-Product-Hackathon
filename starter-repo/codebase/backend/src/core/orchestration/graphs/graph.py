"""Graph cách C (Task 7): parse -> geocode -> research -> select -> price -> schedule -> validate
-> (repair: quay lại select | explain) -> render. Không checkpointer; không import cấu hình web ở đầu module
(answer() chạy không cần server)."""
from langgraph.graph import END, START, StateGraph

from src.core.orchestration.nodes import trip_nodes as tn
from src.core.orchestration.state.state import TripState


def _after_parse(state: dict) -> str:
    return "render" if state.get("status") in ("ask_back", "refused") else "geocode"


def build_trip_graph():
    g = StateGraph(TripState)
    for name, fn in (("parse", tn.parse_request), ("geocode", tn.geocode_node), ("research", tn.research),
                     ("select", tn.select), ("price", tn.price), ("schedule", tn.schedule_node),
                     ("validate", tn.validate_node), ("explain", tn.explain_node), ("render", tn.render_node)):
        g.add_node(name, fn)
    g.add_edge(START, "parse")
    g.add_conditional_edges("parse", _after_parse, {"render": "render", "geocode": "geocode"})
    for a, b in (("geocode", "research"), ("research", "select"), ("select", "price"), ("price", "schedule"),
                 ("schedule", "validate"), ("explain", "render"), ("render", END)):
        g.add_edge(a, b)
    g.add_conditional_edges("validate", tn.route_after_validate, {"repair": "select", "explain": "explain"})
    return g.compile()
