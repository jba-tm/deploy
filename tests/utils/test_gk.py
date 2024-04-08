# from app.contrib.graph_knowledge.utils import get_knowledge_graph
# from drugs import drugs_to_sql
from trials import trials_to_sql


def test_get_knowledge_graph():
    # result = get_knowledge_graph("Lepirudin")
    # print(result)
    # drugs_to_sql()
    trials_to_sql()