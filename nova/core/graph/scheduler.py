from .models import NodeStatus
from .workflow_graphs import WorkflowGraph


class GraphScheduler:
    """
    Responsible for executing nodes from the workflow graph
    in dependency-safe order.
    """

    def __init__(self, graph: WorkflowGraph, dispatcher):
        self.graph = graph
        self.dispatcher = dispatcher

    def is_finished(self):
        """
        Check if workflow execution is complete.
        """

        for node in self.graph.nodes.values():
            if node.status not in (NodeStatus.COMPLETED, NodeStatus.FAILED):
                return False

        return True

    def execute_node(self, node):
        """
        Execute a single node via dispatcher with retry logic.
        """

        attempts = 0

        while attempts <= node.retry_limit:
            node.status = NodeStatus.RUNNING

            result = self.dispatcher.execute(node.command)

            node.stdout = result.stdout
            node.stderr = result.stderr

            print(f"Executing node: {node.id}")
            print(f"Command: {node.command}")

            if result.success:
                node.status = NodeStatus.COMPLETED
                return

            attempts += 1

        node.status = NodeStatus.FAILED

    def run(self):
        """
        Execute the entire workflow graph.
        """

        while not self.is_finished():
            ready_nodes = self.graph.get_ready_nodes()

            if not ready_nodes:
                raise RuntimeError("No executable nodes found. Possible deadlock.")

            for node in ready_nodes:
                self.execute_node(node)
