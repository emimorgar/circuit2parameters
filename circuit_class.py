import numpy as np

class Circuit:
    
    def __init__(self, components_values: list, components_nodes: list, input_nodes: list):
        self._components_values = components_values
        self._components_nodes = [sorted(node) for node in components_nodes]
        self._input_nodes = input_nodes
        self._nodes_matrix = []
        self._circuit_matrix = None
        self._no_in_nodes = None
        self._in_nodes = []

    def equivalent_circuit(self):
        """Find the equivalent circuit for a circuit."""
        parallel_components_set = self.__paralel_branch_finder()
        serial_components_set = self.__serial_branch_finder()

        while parallel_components_set or serial_components_set:
            if parallel_components_set:
                self.__parallel_sum(parallel_components_set)
                parallel_components_set = self.__paralel_branch_finder()
                serial_components_set = self.__serial_branch_finder()
            if serial_components_set:
                self.__serial_sum(serial_components_set)
                parallel_components_set = self.__paralel_branch_finder()
                serial_components_set = self.__serial_branch_finder()

    def __paralel_branch_finder(self) -> list:
        """Find parallel branches in a circuit."""

        components_frequency = {}

        for i, component_nodes in enumerate(self._components_nodes):
            component_tuple = tuple(component_nodes)
            if component_tuple in components_frequency:
                components_frequency[component_tuple].append(i)
            else:
                components_frequency[component_tuple] = [i]

        return [indices for indices in components_frequency.values() if len(indices) > 1]

    def __serial_branch_finder(self) -> list:
        """Find serial branches in a circuit."""

        nodes_frequency = {}
        for component_nodes in self._components_nodes:
            for node in component_nodes:
                nodes_frequency[node] = nodes_frequency.get(node, 0) + 1
        #todos los nodos en serie
        serial_nodes = [num for num, count in nodes_frequency.items() if count == 2]
        #elimina los nodos de entrada
        serial_nodes = [i for i in serial_nodes if i not in self._input_nodes]
        serial_components_set = []
        for serial_node in serial_nodes:
            serial_components = []
            for component, component_nodes in enumerate(self._components_nodes):
                if serial_node in component_nodes:
                    serial_components.append(component)
            serial_components_set.append(serial_components)

        unified = []
        for pair in serial_components_set:
            found = None
            for group in unified:
                if any(item in group for item in pair):
                    found = group
                    break
            if found:
                found.update(pair)
            else:
                unified.append(set(pair))

        return [list(group) for group in unified]

    def __serial_sum(self, serial_components_set: list):
        """Sum the serial components in a circuit."""

        components_to_delete = []
        for components in serial_components_set:
            sum_value = sum(self._components_values[component] for component in components)
            nodes_join = [node for component in components for node in self._components_nodes[component]]
            new_component_nodes = [x for x in nodes_join if nodes_join.count(x) == 1]

            self._components_nodes[components[-1]] = new_component_nodes
            self._components_values[components[-1]] = sum_value
            components_to_delete.extend(components[:-1])

        self._components_values = [v for i, v in enumerate(self._components_values) if i not in components_to_delete]
        self._components_nodes = [n for i, n in enumerate(self._components_nodes) if i not in components_to_delete]

    def __parallel_sum(self, parallel_components_set: list):
        """Sum the parallel components in a circuit."""

        components_to_delete = []
        for components in parallel_components_set:
            sum_value = sum(1 / self._components_values[component] for component in components)
            self._components_values[components[-1]] = 1 / sum_value
            components_to_delete.extend(components[:-1])

        self._components_values = [v for i, v in enumerate(self._components_values) if i not in components_to_delete]
        self._components_nodes = [n for i, n in enumerate(self._components_nodes) if i not in components_to_delete]

    def components_to_node(self):
        """Convert the components to nodes."""

        nodes = []
        for node_num in range(len(self._components_nodes)+1):
            node  = [component_num for component_num, component in enumerate(self._components_nodes) if node_num in component]
            if node_num in self._input_nodes:
                node.append(f"In_{node_num}")
            nodes.append(node)
        self._nodes_matrix = [node for node in nodes if node]

    def get_circuit_matrix(self):
        """Calculate the circuit matrix for a circuit."""

        circuit_matrix_len = len(self._nodes_matrix)
        self._circuit_matrix = np.zeros((circuit_matrix_len, circuit_matrix_len), dtype=complex)
        
        
        for j in range(circuit_matrix_len):
            for i in range(circuit_matrix_len):
                if i == j:
                    acc = complex(0, 0)
                    for component_name in self._nodes_matrix[j]:
                        if not isinstance(component_name, str):
                            acc += 1 / self._components_values[component_name]
                    self._circuit_matrix[j, i] = acc

        self._in_nodes = []
        for j, node in enumerate(self._nodes_matrix):
            for component_name in node:
                if isinstance(component_name, str):
                    self._in_nodes.append(j)
                    continue
                node_num = self.__finder(j, component_name, self._nodes_matrix)
                if node_num > -1:
                    self._circuit_matrix[j, node_num] = -1 / self._components_values[component_name]
    
    def __finder(self, row: int, component_name: str, nodes: np.ndarray) -> int:
        """This function find the component pair and returns the node number where it was allocated.

        Args:
            row (int): Current row of circuit matrix .
            nodes (np.ndarray): nodes matrix.
            component_name (str): component name want to find it.

        Returns:
            int: Node number where component pair was found, -1 if didn't find it.
        """
        for i, node in enumerate(nodes):
            if (i != row) and (component_name in node):
                return i
        return -1

    def get_z_matrix(self):
        """Calculate the Z matrix."""
        
        total_nodes = set(range(len(self._circuit_matrix)))
        self._no_in_nodes = list(total_nodes - set(self._in_nodes))

        while len(self._no_in_nodes) > 0:
            self.__matrix_reduction()
            self._no_in_nodes = [n - 1 for n in self._no_in_nodes[1:]]

    def __matrix_reduction(self):
        """Reduce a circuit matrix by eliminating the row and column corresponding to the given node."""
        circuit_matrix = self._circuit_matrix
        node = self._no_in_nodes[0]

        y, x = circuit_matrix.shape
        pivote_value = circuit_matrix[node, node]
        new_matrix = np.zeros((y - 1, x - 1), dtype=complex)
        new_row = 0
        for j in range(y):
            if j == node:
                continue
            new_col = 0
            for i in range(x):
                if i == node:
                    continue
                new_matrix[new_row, new_col] = circuit_matrix[j, i] - circuit_matrix[node, i] * circuit_matrix[j, node] / pivote_value
                new_col += 1
            new_row += 1

        self._circuit_matrix = new_matrix

    def run(self):
        """Run the circuit analysis."""

        self.equivalent_circuit()
        self.components_to_node()
        self.get_circuit_matrix()
        self.get_z_matrix()
        
    
        
        
# Ejemplo de uso
if __name__ == "__main__":
    
    input_nodes = [0,4,5]
    components_values = [
        5000j,
        10000,
        -.01j,
        1000,
        0.1,
        -0.1j,
        9800,
        10j,
        1500,
        150,
        100j,
        1123,
        -600j,
        100j,
        10000,
        15
    ]
    #components_values = [10,10,10,10,10,10,10,10,10]
    #components_nodes = [[0,6],[6,2],[1,5],[4,2],[2,0],[3,5],[6,3],[1,4],[4,3]]
    components_nodes = [[0,1],[1,2],[0],[0,3],[2,3],[2,4],[3,4],[3,4],[4],[4],[4],[4,5],[5,6],[6,7],[7,4],[7]]
    

    circuit = Circuit(components_values, components_nodes, input_nodes)
    print("Component Nodes (Original):", circuit._components_nodes)
    print("Component Values (Original):", circuit._components_values)
    
    #components_nodes_, components_values_ = circuit.equivalent_circuit()
    #print("Component Nodes (Equivalent):", components_nodes_)
    #print("Component Values (Equivalent):", components_values_)
    
    circuit.run()

    print("Component Nodes (Simplified): ", circuit._components_nodes)
    print("Component Values (Simplified): ", circuit._components_values)

    print("Circuit Matrix:\n", circuit._circuit_matrix)