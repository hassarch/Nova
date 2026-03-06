from typing import Dict, List

from .models import ExecutionNode


class WorkflowGraph:
    """
    Manages execution nodes and their dependencies.
    """

    def __init__(self):
        self.nodes: Dict[str, ExecutionNode] = {}

    def add_node(self, node: ExecutionNode):
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists")

        self.nodes[node.id] = node

    def validate_dependencies(self):
        """
        Ensure all dependencies reference valid nodes.
        """

        for node in self.nodes.values():
            for dep in node.depends_on:
                if dep not in self.nodes:
                    raise ValueError(f"Node '{node.id}' depends on missing node '{dep}'")

    def detect_cycles(self):
        visited = set()
        stack = set()

        def visit(node_id):
            if node_id in stack:
                raise ValueError("Cycle detected in workflow graph")

            if node_id in visited:
                return

            stack.add(node_id)

            for dep in self.nodes[node_id].depends_on:
                visit(dep)

            stack.remove(node_id)
            visited.add(node_id)

        for node_id in self.nodes:
            visit(node_id)

    def get_ready_nodes(self) -> List[ExecutionNode]:
        ready = []

        for node in self.nodes.values():
            if node.status != "pending":
                continue

            dependencies_completed = all(self.nodes[dep].status == "completed" for dep in node.depends_on)

            if dependencies_completed:
                ready.append(node)

        return ready

    def mark_completed(self, node_id: str):
        self.nodes[node_id].status = "completed"

    def mark_failed(self, node_id: str):
        self.nodes[node_id].status = "failed"
