import numpy as np

class Circuit:
    
    def __init__(self, components_values, components_nodes, input_nodes):
        self.components_values = components_values
        self.components_nodes = [sorted(node) for node in components_nodes]
        self.input_nodes = input_nodes

    def __finder(self, row, component_name, nodes) -> int:
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

    def __matrix_reduction(self) -> np.ndarray:
        """Reduce a circuit matrix by eliminating the row and column corresponding to the given node.

        Args:
            circuit_matrix (np.ndarray): The original circuit matrix.
            node (int): The node to be used as a pivot.

        Returns:
            np.ndarray: The reduced matrix.
        """
        circuit_matrix = self.circuit_matrix
        node = self.no_in_nodes
        
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

        self.circuit_matrix = new_matrix[1:]
        self.no_in_nodes = node

    def __paralel_branch_finder(self):
        components_frequency = {}

        for i, component_nodes in enumerate(self.components_nodes):
            component_tuple = tuple(component_nodes)
            if component_tuple in components_frequency:
                components_frequency[component_tuple].append(i)
            else:
                components_frequency[component_tuple] = [i]

        return [indices for indices in components_frequency.values() if len(indices) > 1]

    def __serial_branch_finder(self):
        nodes_frequency = {}
        for component_nodes in self.components_nodes:
            for node in component_nodes:
                nodes_frequency[node] = nodes_frequency.get(node, 0) + 1
        #todos los nodos en serie
        serial_nodes = [num for num, count in nodes_frequency.items() if count == 2]
        #elimina los nodos de entrada
        serial_nodes = [i for i in serial_nodes if i not in self.input_nodes]
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

    def __serial_sum(self, serial_components_set):
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

    def __parallel_sum(self, parallel_components_set):
        components_to_delete = []
        for components in parallel_components_set:
            sum_value = sum(1 / self.components_values[component] for component in components)
            self.components_values[components[-1]] = 1 / sum_value
            components_to_delete.extend(components[:-1])

        self.components_values = [v for i, v in enumerate(self.components_values) if i not in components_to_delete]
        self.components_nodes = [n for i, n in enumerate(self.components_nodes) if i not in components_to_delete]

    def get_circuit_matrix(self):
        #print(nodes)
        circuit_matrix_len = len(self.nodes_matrix)
        self.circuit_matrix = np.zeros((circuit_matrix_len, circuit_matrix_len), dtype=complex)
        
        
        for j in range(circuit_matrix_len):
            for i in range(circuit_matrix_len):
                if i == j:
                    acc = complex(0, 0)
                    for component_name in self.nodes_matrix[j]:
                        if not isinstance(component_name, str):
                            acc += 1 / self.components_values[component_name]
                    self.circuit_matrix[j, i] = acc

        self.in_nodes = []
        for j, node in enumerate(self.nodes_matrix):
            for component_name in node:
                if isinstance(component_name, str):
                    self.in_nodes.append(j)
                    continue
                node_num = self.__finder(j, component_name, self.nodes_matrix)
                if node_num > -1:
                    self.circuit_matrix[j, node_num] = -1 / self.components_values[component_name]

    def get_z_matrix(self) -> np.ndarray:
        """
        Calculate the Z matrix for a circuit.

        Args:
            component_values (dict): Dictionary of component values (e.g., resistors, capacitors).
            nodes (np.ndarray): Matrix of nodes.

        Returns:
            np.ndarray: The Z matrix.
        """
        
        total_nodes = set(range(len(self.circuit_matrix)))
        self.no_in_nodes = list(total_nodes - set(self.in_nodes))

        while len(no_in_nodes) > 0:
            self.__matrix_reduction()
            total_nodes = set(range(len(self.circuit_matrix)))
            no_in_nodes = [n - 1 for n in self.no_in_nodes[1:]]

    def equivalent_circuit(self):
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
    
    def components_to_node(self):

        nodes = []
        for node_num in range(len(self.components_nodes)+1):
            node  = [component_num for component_num, component in enumerate(self.components_nodes) if node_num in component]
            if node_num in self.input_nodes:
                node.append(f"In_{node_num}")
            nodes.append(node)
        self.nodes_matrix = [node for node in nodes if node]
    
    def run(self):
        self.equivalent_circuit()
        self.components_to_node()
        self.get_circuit_matrix()
        self.get_z_matrix()
        
    
        
        
# Ejemplo de uso
if __name__ == "__main__":
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    
    input_nodes = [5,0]
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
    print("Component Nodes (Original):", circuit.components_nodes)
    print("Component Values (Original):", circuit.components_values)
    
    #components_nodes_, components_values_ = circuit.equivalent_circuit()
    #print("Component Nodes (Equivalent):", components_nodes_)
    #print("Component Values (Equivalent):", components_values_)
    
    
    z_matrix = circuit.get_z_matrix()
    print("Matriz Z:", z_matrix)

