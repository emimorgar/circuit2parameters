import cmath
import numpy as np

Z_matrix = [[1+2j, 2], [3+2j, 1j]]

### Get coeficient to calculate Inverse matrix
def get_cof(mat, cof, p, q, n):
    i = 0
    j = 0
    for row in range(n):
        for col in range(n):
            if row != p and col != q:
                cof[i][j] = mat[row][col]
                j += 1
                if j == n - 1:
                    j = 0
                    i += 1
                    
### Get adjoint matrix for Inverse matrix                     
def adjoint(mat, adj):
    n = len(mat)
    if n == 1:
        adj[0][0] = 1
        return
    sign = 1
    cof = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            get_cof(mat, cof, i, j, n)
            sign = 1 if (i + j) % 2 == 0 else -1
            adj[j][i] = sign * det(cof, n - 1)        


### Function to calculate inverse matrix
def inverse(mat):
    n = len(mat)
    det = det(mat, n)
    if det == 0:
        print("Matriz singular, no se puede calcular matriz inversa")
        return None
    adj = [[0] * n for _ in range(n)]
    adjoint(mat, adj)
    inv = [[adj[i][j] / det for j in range(n)] for i in range(n)]
    return inv            
                    

### Function to calculate determinat 
def det(mat):
    n = len(mat)
    if n == 2:
        return mat[0][0] * mat[1][1] - \
               mat[0][1] * mat[1][0]
    res = 0
    for col in range(n):
      sub = [[0] * (n - 1) for _ in range(n - 1)]
      for i in range(1, n):
          subcol = 0
          for j in range(n):  
              if j == col:
                  continue
              
              sub[i - 1][subcol] = mat[i][j]
              subcol += 1
              
      sign = 1 if col % 2 == 0 else -1
      res += sign * mat[0][col] * det(sub, n - 1)
    
    return res

### Z to ABCD ###
def z2abcd(mat):
    det_mat = det(mat)
    if len(mat) == 2:
        C = 1 / mat[0][0]
        D = mat[1][1] / mat[1][0]
        A = mat[0][0] / mat[1][0]
        B = det_mat / mat[1][0]    
        ABCD_matrix = [[A, B],[C, D]]
        return ABCD_matrix
    else:
        print("Tamaño de matriz inválido")
        return None
        
test_abcd = z2abcd(Z_matrix)
test_y = inverse(Z_matrix)

print(test_abcd)

### Z to S ###
def z2s(mat, z_car):
    if len(mat) == 2:
        s_11 = ((mat[0][0] - z_car)(mat[1][1] + z_car)-(mat[0][1]*mat[1][0]))/((mat[0][0] + z_car)(mat[1][1] + z_car)-(mat[0][1]*mat[1][0]))
        s_12 = (2 * mat[0][1] * z_car)/((mat[0][0] + z_car)(mat[1][1] + z_car)-(mat[0][1]*mat[1][0]))
        s_21 = (2 * mat[1][0] * z_car)/((mat[0][0] + z_car)(mat[1][1] + z_car)-(mat[0][1]*mat[1][0]))
        s_22 = ((mat[0][0] + z_car)(mat[1][1] - z_car)-(mat[0][1]*mat[1][0]))/((mat[0][0] + z_car)(mat[1][1] + z_car)-(mat[0][1]*mat[1][0]))
        S_matrix = [[s_11, s_12],[s_21, s_22]]
        return S_matrix
    else:
        return None
        