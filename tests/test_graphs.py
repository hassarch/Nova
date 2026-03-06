from nova.core.graph.models import ExecutionNode
from nova.core.graph.workflow_graphs import WorkflowGraph

graph = WorkflowGraph()

graph.add_node(ExecutionNode(id="install", command="pip install -r requirements.txt"))

graph.add_node(ExecutionNode(id="test", command="pytest", depends_on=["install"]))

graph.validate_dependencies()
graph.detect_cycles()

ready = graph.get_ready_nodes()

print([n.id for n in ready])
