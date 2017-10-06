import numpy.linalg as linalg
import numpy as np
import src.phase1util
#input      doc_id_dict     {index : doc_id}
#           feature_id_dict {index : feature_id}
#           value_matrix    {doc_id :{feature_id : value}}
# return 2 d nparray. with rows doc_id, cols feature_id
def build_matrix(doc_id_dict, feature_id_dict, value_matrix):
    matrix = []
    row = len(doc_id_dict)
    col = len(feature_id_dict)
    for i in (row):
        for j in range(col):
            doc_id = doc_id_dict[i]
            feature_id = feature_id_dict[j]
            matrix[i][i] = value_matrix[doc_id][feature_id]
    return matrix




a = [[9, 4, 5, 2],[7, 4, 2, 3],[7, 2, 1, 6],[8, 2, 5, 3],[8, 9, 8,6]]

U, s, V = linalg.svd(a, full_matrices=True)


print(a)

print("U is {}".format(U))
print("s is {}".format(s))
print("V is {}".format(V))