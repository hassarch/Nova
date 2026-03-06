from nova.core.graph.models import ExecutionNode
from nova.core.graph.scheduler import GraphScheduler
from nova.core.graph.workflow_graphs import WorkflowGraph


class FakeDispatcher:
    def execute(self, command):
        class Result:
            success = True
            stdout = "ok"
            stderr = ""

        print("Running:", command)

        return Result()


graph = WorkflowGraph()

graph.add_node(ExecutionNode(id="install", command="pip install -r requirements.txt"))

graph.add_node(ExecutionNode(id="tests", command="pytest", depends_on=["install"]))

graph.validate_dependencies()
graph.detect_cycles()

scheduler = GraphScheduler(graph, FakeDispatcher())

scheduler.run()
