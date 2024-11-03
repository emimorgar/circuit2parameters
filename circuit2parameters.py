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

    return serial_nodes

  
if __name__ == "__main__":   
    
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

    components_nodes = [[0,1],[1,2],[0],[0,3],[2,3],[2,4],[3,4],[3,4],[4]]
    input_nodes = [1,4]
    
    for compenent_nodes in components_nodes:
        compenent_nodes.sort()
        
    
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
