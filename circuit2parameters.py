import numpy as np

def get_circuit_matrix(components_values : list, nodes : np.ndarray) -> np.ndarray:
    """This function calculate the circuit matriz based of nodes
    
    Args:
        component_value (dict): It's a dict with the component values
        nodes (np.ndarray): It's a matrix where "y" elements are the nodes and 
                          each node contain the components into there.

    Returns:
        np.ndarray: Returns the characteristic matrix of the circuit
    """

    circuit_matrix_len = nodes.shape[0]
    circuit_matrix = np.zeros((circuit_matrix_len, circuit_matrix_len), dtype=complex)
    
    #This section fills the diagonal of circuit matrix 
    for j in range(circuit_matrix_len):
        for i in range(circuit_matrix_len):
            if i == j:
                acc = complex(0,0)
                for component_name in nodes[j]:
                    
                    if not isinstance(component_name, str):
                        acc += 1/components_values[component_name]

                circuit_matrix[j,i] = acc
    
    #This section search the component pair in other nodes 
    #and if it find it in n node, n will be the position where will be filled in circuit matrix.
    In_nodes = []
    for j, node in enumerate(nodes):
        for component_name in node:

            if isinstance(component_name, str):
                In_nodes.append(j)
                continue

            node_num = finder(j, nodes, component_name)

            if node_num > -1:
                circuit_matrix[j, node_num] = -1/components_values[component_name]
    
    return circuit_matrix, In_nodes

def finder(row : int, nodes : np.ndarray,  component_name : str) -> int:
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

def matrix_reduction(circuit_matrix : np.ndarray, node : int) -> np.ndarray:
    """Reduce a circuit matrix by eliminating the row and column corresponding to the given node.

    Args:
        circuit_matrix (np.ndarray): The original circuit matrix.
        node (int): The node to be used as a pivot.

    Returns:
        np.ndarray: The reduced matrix.
    """
    (Y,X) = circuit_matrix.shape

    pivote = (node,X-node)
    pivote_value = circuit_matrix[node][X-node]
    
    new_matrix = np.zeros((X-1), dtype=complex)
    for j in range(Y):
        if j == pivote[0]:
            continue
        else:
            new_node = np.array([], dtype=complex)
            for i in range(X):
                if i == pivote[1]:
                    continue 
                else:
                    new_node = np.append(new_node, circuit_matrix[j][i] - circuit_matrix[pivote[0]][i]*circuit_matrix[j][pivote[1]]/pivote_value)
        new_matrix = np.vstack((new_matrix, new_node))
    
    return new_matrix[1:]

def get_z_matrix(components_values : list, nodes : np.ndarray) -> np.ndarray:
    """
    Calculate the Z matrix for a circuit.

    Args:
        component_values (dict): Dictionary of component values (e.g., resistors, capacitors).
        nodes (np.ndarray): Matrix of nodes.

    Returns:
        np.ndarray: The Z matrix.
    """
    z_matrix, In_nodes = get_circuit_matrix(components_values, nodes)
    Total_nodes =  set([x for x in range(len(z_matrix))])
    No_In_nodes = list(Total_nodes - set(In_nodes))
  
    while len(No_In_nodes) > 0:
        z_matrix = matrix_reduction(z_matrix, No_In_nodes[0])
        Total_nodes =  set([x for x in range(len(z_matrix))])
        No_In_nodes = [n-1 for n in No_In_nodes[1:]]
    
    return z_matrix


def paralel_branch_finder(components_nodes):
    components_frecuency = {}
    
    for i, component_nodes in enumerate(components_nodes):
        component_tuple = tuple(component_nodes)
        if component_tuple in components_frecuency:
            components_frecuency[component_tuple].append(i)
        else:
            components_frecuency[component_tuple] = [i]

    paralel_components = [indices for indices in components_frecuency.values() if len(indices) > 1]
    
    return paralel_components
        
def serial_branch_finder(components_nodes):
    
    nodes_frecuency = {}
    for component_nodes in components_nodes:
        for node in component_nodes:
            if node in nodes_frecuency:
                nodes_frecuency[node] += 1
            else:
                nodes_frecuency[node] = 1
    
    serial_nodes = [num for num, count in nodes_frecuency.items() if count == 2]

    serial_components_set = []
    for serial_node in serial_nodes:
        serial_components = []
        for component, component_nodes in enumerate(components_nodes):
            for node in component_nodes:
                if node == serial_node:
                    serial_components.append(component)
        serial_components_set.append(serial_components)
    
    return serial_components_set

def serial_sum(components_nodes, components_values, serial_components_set):
    
    components_to_delate = []
    for [component_a, component_b] in serial_components_set:
        
        components_nodes_join = components_nodes[component_a] + components_nodes[component_b]
        new_component_nodes = [x for x in components_nodes_join if components_nodes_join.count(x) == 1]
        
        components_nodes[component_a] = new_component_nodes
        components_values[component_a] = components_values[component_a] + components_values[component_b]
        
        components_to_delate.append(component_b)
    
    components_values = [component for i, component in enumerate(components_values) if i not in components_to_delate]
    components_nodes = [component for i, component in enumerate(components_nodes) if i not in components_to_delate]
        
    return components_nodes, components_values

def paralel_sum(components_nodes, components_values, paralel_components_set):
    
    components_to_delate = []
    for components in paralel_components_set:
        
        #Suma paralela o serial
        sum_value = 0
        for component in components:
            sum_value += 1/components_values[component]
            
        #Asignacion de la nueva rama
        components_values[component] = 1/sum_value
        
        #Eliminacion de los componentes 
        components_to_delate.extend(components[:-1])
        
    components_values = [component for i, component in enumerate(components_values) if i not in components_to_delate]
    components_nodes = [component for i, component in enumerate(components_nodes) if i not in components_to_delate]
        
    return components_nodes, components_values

def equivalent_circuit(components_nodes, components_values):
    
    paralel_components_set = paralel_branch_finder(components_nodes)
    serial_nodes_set = serial_branch_finder(components_nodes) 
    
    while paralel_components_set or serial_nodes_set:
        print(paralel_components_set, serial_nodes_set)
        if paralel_components_set:
            components_nodes, components_values = paralel_sum(components_nodes, components_values, paralel_components_set)
            paralel_components_set = paralel_branch_finder(components_nodes)
        if serial_nodes_set:
            components_nodes, components_values = serial_sum(components_nodes, components_values, serial_nodes_set)
            serial_nodes_set = serial_branch_finder(components_nodes)
    
    return components_nodes, components_values
    
    
  
if __name__ == "__main__":   
    
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

    input_nodes = [1,4]

    components_values = [
        0.001j,
        10000,
        -.01j,
        1000,
        0.1,
        -0.1j,
        9800,
        10j,
        1500,
        150
    ]
    
    components_nodes = [[0,1],[1,2],[0],[0,3],[2,3],[2,4],[3,4],[3,4],[4],[4]]
    
    for component_nodes in components_nodes:
        component_nodes.sort()
    
    components_nodes, components_values = equivalent_circuit(components_nodes, components_values)
    
    print(components_nodes)
    print(components_values)
    
    components_values = [
        0.001j,
        10000,
        -.01j,
        1000,
        0.1,
        -0.1j
    ]

    #Examples of circuits
    nodes = np.array([[0,1,"In_1"],[1,2,3],[3,0,4],[2,4,5,"In_3"]])
    #nodes = np.array([["Z1","Z2","In_1"],["Z2","Z3","Z4"],["Z4","Z1","Z5","In_2"],["Z3","Z5","Z6"]])
    #nodes = np.array([["Z1","Z2","In_1"],["Z2","Z3","Z4"],["Z4","Z1","Z5","In_2"]])
    #nodes = np.array([["Z2","In_1"],["Z2","Z3","Z4"],["Z4","Z5","In_2"]])       

    
    z_matrix = get_z_matrix(components_values, nodes)
    print(z_matrix)
