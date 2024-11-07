import numpy as np

class Circuit:
    def __init__(self, components_values, components_nodes, nodes):
        self.components_values = components_values
        self.components_nodes = [sorted(node) for node in components_nodes]
        self.nodes = nodes

    def _finder(self, row, component_name):
        for i, node in enumerate(self.nodes):
            if (i != row) and (component_name in node):
                return i
        return -1

    def _matrix_reduction(self, circuit_matrix, node):
        y, x = circuit_matrix.shape
        pivote_value = circuit_matrix[node, x - node]
        new_matrix = np.zeros((x - 1), dtype=complex)

        for j in range(y):
            if j == node:
                continue
            new_node = np.array([], dtype=complex)
            for i in range(x):
                if i == x - node:
                    continue
                new_node = np.append(new_node, circuit_matrix[j, i] - circuit_matrix[node, i] * circuit_matrix[j, x - node] / pivote_value)
            new_matrix = np.vstack((new_matrix, new_node))

        return new_matrix[1:]

    def _paralel_branch_finder(self):
        components_frequency = {}

        for i, component_nodes in enumerate(self.components_nodes):
            component_tuple = tuple(component_nodes)
            if component_tuple in components_frequency:
                components_frequency[component_tuple].append(i)
            else:
                components_frequency[component_tuple] = [i]

        return [indices for indices in components_frequency.values() if len(indices) > 1]

    def _serial_branch_finder(self):
        nodes_frequency = {}
        for component_nodes in self.components_nodes:
            for node in component_nodes:
                nodes_frequency[node] = nodes_frequency.get(node, 0) + 1

        serial_nodes = [num for num, count in nodes_frequency.items() if count == 2]
        serial_components_set = []

        for serial_node in serial_nodes:
            serial_components = []
            for component, component_nodes in enumerate(self.components_nodes):
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

    def _serial_sum(self, serial_components_set):
        components_to_delete = []
        for components in serial_components_set:
            sum_value = sum(self.components_values[component] for component in components)
            nodes_join = [node for component in components for node in self.components_nodes[component]]
            new_component_nodes = [x for x in nodes_join if nodes_join.count(x) == 1]

            self.components_nodes[components[-1]] = new_component_nodes
            self.components_values[components[-1]] = sum_value
            components_to_delete.extend(components[:-1])

        self.components_values = [v for i, v in enumerate(self.components_values) if i not in components_to_delete]
        self.components_nodes = [n for i, n in enumerate(self.components_nodes) if i not in components_to_delete]

    def _parallel_sum(self, parallel_components_set):
        components_to_delete = []
        for components in parallel_components_set:
            sum_value = sum(1 / self.components_values[component] for component in components)
            self.components_values[components[-1]] = 1 / sum_value
            components_to_delete.extend(components[:-1])

        self.components_values = [v for i, v in enumerate(self.components_values) if i not in components_to_delete]
        self.components_nodes = [n for i, n in enumerate(self.components_nodes) if i not in components_to_delete]

    def get_circuit_matrix(self):
        circuit_matrix_len = self.nodes.shape[0]
        circuit_matrix = np.zeros((circuit_matrix_len, circuit_matrix_len), dtype=complex)
        in_nodes = []
        
        for j in range(circuit_matrix_len):
            for i in range(circuit_matrix_len):
                if i == j:
                    acc = complex(0, 0)
                    for component_name in self.nodes[j]:
                        if not isinstance(component_name, str):
                            acc += 1 / self.components_values[component_name]
                    circuit_matrix[j, i] = acc

        for j, node in enumerate(self.nodes):
            for component_name in node:
                if isinstance(component_name, str):
                    in_nodes.append(j)
                    continue
                node_num = self._finder(j, component_name)
                if node_num > -1:
                    circuit_matrix[j, node_num] = -1 / self.components_values[component_name]

        return circuit_matrix, in_nodes

    def get_z_matrix(self):
        z_matrix, in_nodes = self.get_circuit_matrix()
        total_nodes = set(range(len(z_matrix)))
        no_in_nodes = list(total_nodes - set(in_nodes))

        while len(no_in_nodes) > 0:
            z_matrix = self._matrix_reduction(z_matrix, no_in_nodes[0])
            total_nodes = set(range(len(z_matrix)))
            no_in_nodes = [n - 1 for n in no_in_nodes[1:]]

        return z_matrix

    def equivalent_circuit(self):
        parallel_components_set = self._paralel_branch_finder()
        serial_components_set = self._serial_branch_finder()

        while parallel_components_set or serial_components_set:
            if parallel_components_set:
                self._parallel_sum(parallel_components_set)
                parallel_components_set = self._paralel_branch_finder()
                serial_components_set = self._serial_branch_finder()
            if serial_components_set:
                self._serial_sum(serial_components_set)
                parallel_components_set = self._paralel_branch_finder()
                serial_components_set = self._serial_branch_finder()

        return self.components_nodes, self.components_values

# Ejemplo de uso
if __name__ == "__main__":
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    
    input_nodes = [1,4]
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
    nodes = np.array([[0,1,"In_1"],[1,2,3],[3,0,4],[2,4,5,"In_3"]])

    circuit = Circuit(components_values, components_nodes, nodes)
    print("Component Nodes (Original):", circuit.components_nodes)
    print("Component Values (Original):", circuit.components_values)
    
    components_nodes, components_values = circuit.equivalent_circuit()
    print("Component Nodes (Equivalent):", circuit.components_nodes)
    print("Component Values (Equivalent):", circuit.components_values)
        
    z_matrix = circuit.get_z_matrix()
    print("Matriz Z:", z_matrix)

