import numpy as np

class Circuit:
    
    def __init__(self, components: list, input_nodes: list, lower_freq_limit: float, upper_freq_limit: float, freq_step: float, z_charac: float):
        self._components = components
        self._input_nodes = input_nodes
        self._frecuency = lower_freq_limit
        self._upper_freq_limit = upper_freq_limit
        self._freq_step = freq_step
        self._z_charac = z_charac
        self._components_values = []
        self._components_nodes = []
        self._nodes_matrix = []
        self._circuit_matrix = None
        self._no_in_nodes = None
        self._in_nodes = []
        self.z_matrix = None
        self.y_matrix = None
        self.abcd_matrix = None
        self.s_matrix = None

    def impedance_calculator(self):
        """Convert input components to components_values and components_nodes."""

        for component in self._components:
            type_, value, *nodes = component
            if type_ == "R":
                self._components_values.append(value)
            elif type_ == "C":
                self._components_values.append(-1j / (2 * np.pi * self._frecuency * value))
            elif type_ == "L":
                self._components_values.append(1j * 2 * np.pi * self._frecuency * value)
            elif type_ == "S":
                relative_permitivity = 4.6 # Relative permitivity of the substrate FR4
                Beta = 2 * np.pi * self._frecuency * np.sqrt(relative_permitivity)/ 3e8
                self._components_values.append(1j * self._z_charac * np.tan(Beta * value))
            elif type_ == "O":
                relative_permitivity = 4.6 # Relative permitivity of the substrate FR4
                Beta = 2 * np.pi * self._frecuency * np.sqrt(relative_permitivity)/ 3e8
                self._components_values.append(-1j * self._z_charac / np.tan(Beta * value))
                
            self._components_nodes.append(sorted(nodes))

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

    def get_y_matrix(self):
        """Calculate the Z matrix for a circuit."""
        
        total_nodes = set(range(len(self._circuit_matrix)))
        self._no_in_nodes = list(total_nodes - set(self._in_nodes)) 

        while len(self._no_in_nodes) > 0:
            self.__matrix_reduction()
            self._no_in_nodes = [n - 1 for n in self._no_in_nodes[1:]]
        
        self.y_matrix = self._circuit_matrix

    def __matrix_reduction(self):
        """Reduce a circuit matrix by eliminating the row and column corresponding to the given node."""

        node = self._no_in_nodes[0]

        y, x = self._circuit_matrix.shape
        pivote_value = self._circuit_matrix[node, node]
        new_matrix = np.zeros((y - 1, x - 1), dtype=complex)
        new_row = 0
        for j in range(y):
            if j == node:
                continue
            new_col = 0
            for i in range(x):
                if i == node:
                    continue
                new_matrix[new_row, new_col] = (self._circuit_matrix[j, i] 
                                                - self._circuit_matrix[node, i] 
                                                * self._circuit_matrix[j, node] 
                                                / pivote_value)
                new_col += 1
            new_row += 1

        self._circuit_matrix = new_matrix
    
    def y2z(self):
        """Convert Z matrix to Y matrix."""
        det = np.linalg.det(self.y_matrix)
        if det:
            self.z_matrix = np.linalg.inv(self.y_matrix)
        else:
            self.z_matrix = None

    def z2abcd(self):
        """Convert Z matrix to ABCD matrix."""
        if len(self.z_matrix) == 2:
            det_mat = np.linalg.det(self.z_matrix)
            C = 1 / self.z_matrix[0][0]
            D = self.z_matrix[1][1] / self.z_matrix[1][0]
            A = self.z_matrix[0][0] / self.z_matrix[1][0]
            B = det_mat / self.z_matrix[1][0]    
            self.abcd_matrix = np.array([[A, B], [C, D]], dtype=complex)

    def z2s(self):
        """Convert Z matrix to S matrix."""
        if len(self.z_matrix) == 2:
            s_11 = ((self.z_matrix[0][0] - self._z_charac) * (self.z_matrix[1][1] + self._z_charac) - 
                    (self.z_matrix[0][1] * self.z_matrix[1][0])) / ((self.z_matrix[0][0] + self._z_charac) * 
                    (self.z_matrix[1][1] + self._z_charac) - (self.z_matrix[0][1] * self.z_matrix[1][0]))
            s_12 = (2 * self.z_matrix[0][1] * self._z_charac) / ((self.z_matrix[0][0] + self._z_charac) * 
                    (self.z_matrix[1][1] + self._z_charac) - (self.z_matrix[0][1] * self.z_matrix[1][0]))
            s_21 = (2 * self.z_matrix[1][0] * self._z_charac) / ((self.z_matrix[0][0] + self._z_charac) * 
                    (self.z_matrix[1][1] + self._z_charac) - (self.z_matrix[0][1] * self.z_matrix[1][0]))
            s_22 = ((self.z_matrix[0][0] + self._z_charac) * (self.z_matrix[1][1] - self._z_charac) - 
                    (self.z_matrix[0][1] * self.z_matrix[1][0])) / ((self.z_matrix[0][0] + self._z_charac) * 
                    (self.z_matrix[1][1] + self._z_charac) - (self.z_matrix[0][1] * self.z_matrix[1][0]))
            self.s_matrix = np.array([[s_11, s_12], [s_21, s_22]], dtype=complex)

    def run_simulation(self):
        """Run the circuit simulation."""
        circuit = {}
        while self._frecuency <= self._upper_freq_limit:

            matrix = {}
            self.impedance_calculator()
            self.equivalent_circuit()
            self.components_to_node()
            self.get_circuit_matrix()
            self.get_y_matrix()
            matrix["Y"] = self.y_matrix
            self.y2z()
            matrix["Z"] = self.z_matrix
            self.z2abcd()
            matrix["ABCD"] = self.abcd_matrix
            self.z2s()
            matrix["S"] = self.s_matrix
            circuit[self._frecuency] = matrix
            self._frecuency += self._freq_step

        return circuit
    
if __name__ == "__main__":
    
    input_nodes = [0,7]

    components = [
        ["L", 0.00045, 0, 1],
        ["R", 10000, 1, 2],
        ["C", 0.01, 0],
        ["R", 1000, 0, 3],
        ["L", 0.001, 2, 3],
        ["C", 0.0001, 2, 4],
        ["R", 9800, 3, 4],
        ["C", 0.01, 3, 4],
        ["L", 0.01, 4],
        ["R", 1500, 4],
        ["R", 150, 4],
        ["L", 1, 4, 5],
        ["R", 1123, 5, 6],
        ["C", 0.00007, 6, 7],
        ["L", 0.1, 7, 4],
        ["R", 10000, 7]
    ]

    lower_freq_limit = 1e3 
    upper_freq_limit = 1e6  
    freq_step = 1e3  

    circuit = Circuit(components, input_nodes, lower_freq_limit, upper_freq_limit, freq_step, 50)
    
    circuit.run_simulation()