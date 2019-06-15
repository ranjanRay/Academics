import numpy as np
from collections import defaultdict


def createInitialAuthVector(graph) :

    '''

        ## INPUT :

            ## The graph.

        ## OUTPUT :

            ## A - adjacency matrix from the graph.
            ## ATranspose - transpose of A.
            ## v0 - Initial authority vector.
            ## mapping - virtual to real graph node numbers.
            ## reverseMapping - real to virtual graph node numbers.

    '''

    outEdgeWeights = defaultdict(lambda : 0.0)
    mapping = {}
    reverseMapping = {}
    for eachNode in graph.nodes() :
        for eachKey in graph[eachNode] :
            outEdgeWeights[eachNode] += graph[eachNode][eachKey][0]['weight']

    # for k, v in outEdgeWeights.items() :
    #     print(k, v)
    i = 1
    for eachItem in outEdgeWeights.items() :
        mapping[i] = eachItem
        reverseMapping[eachItem[0]] = i
        i += 1


    ## Let the initial adjacency matrix of the graph be A
    ## let the initial auth vector be v0
    ## Let the the transpose of the matrix be AT

    graphTranspose = graph.reverse()

    A = np.zeros((i+1, i+1))
    for eachNode in graphTranspose.nodes() :
        for eachKey in graphTranspose[eachNode] :
            try :
                A[reverseMapping[eachNode]][reverseMapping[eachKey]] = 1
            except :
                continue

    ATranspose = np.transpose(A)

    v0 = np.zeros((i+1, 1))


    for k, v in reverseMapping.items() :
        v0[v] = outEdgeWeights[k]

    # print(v0)
    return (A, ATranspose, v0, i, mapping, reverseMapping)


def normalise(matrix, j) :

    '''

    ## Normalisation makes sure that each entry in the matrix remains within the bound [0, 1]


    ## INPUT :
        ## The matrix.

    ## OUTPUT :
        ## The matrix with normalised values.

    '''

    total = 0.0
    for i in range(0, j+1) :
        try :
            total += matrix[i][0] ** 2
        except :
            break

    total = total ** 0.5
    for i in range(0, j+1) :

        matrix[i][0] *= 1.0
        matrix[i][0] /= total

    return matrix

def HITS(A, ATranspose, v0, epsilon, i) :

    '''
        ##  INPUT :

            ## A is the adjacency matrix of the graph.
            ## ATranspose is the transpose of the matrix A.
            ## v0 is the initial authority vector.
            ## epsilon is the permissible error.
            ## i is the number of rows and columns in the matrix A.

        ##  OUTPUT :

            ## u0 containing the hub scores for each node in the graph.
            ## v0 containing the authorty scores for each node in the graph.

    '''

    v0 = normalise(v0, i)
    u0 = np.matmul(A, v0)
    # print('The initial hub vector...')
    # print(u0)

    if (u0 >= 1).any() :
        u0 = normalise(u0, i)

    for _ in range(0, 201) :

        # v1 = normalise(ATranspose * u0, i)
        # u1 = normalise(A * v1, i)
        v1 = np.matmul(ATranspose, u0)
        u1 = np.matmul(A, v1)
        if (abs(v0 - v1) <= epsilon).all() and (abs(u0 - u1) <= epsilon).all() :
            break

        if (v1 >= 1).any() :
            v0 = normalise(v1, i)
        else :
            v0 = v1

        if (u1 >= 1).any() :
            u0 = normalise(u1, i)

        else :
            u0 = u1

    return (u0, v0) ## The return values are the hub and authority vectors respectively.


def generateHubAndAuth(hubMatrix, authMatrix, mapping, reverseMapping) :

    '''
    ##   INPUT :

        ## hubMatrix is a N x 1 matrix containing the hub scores of each of the nodes in the graph.
        ## authMatrix is a N x 1 matrix containing the authority scores of each of the nodes in the graph.
        ## mapping is a dictionary containing the mapping from virtual node number to real node number
            in the graph.

        ## reverseMapping is a dictionary containg the mapping from real node number to the virtual one
            in the graph.

    ##  OUTPUT :

        ## hubDict - contains the dictionary mapping between the real node number to its hub score.
        ## authDict - contains the dictionary mapping between the real node number to its authorty score.

    '''

    hubDict = {}
    authDict = {}

    for eachKey in mapping.items() :
        # print(eachKey[0], eachKey[1][0])
        hubDict[eachKey[1][0]] = hubMatrix[eachKey[0]][0]
        authDict[eachKey[1][0]] = authMatrix[eachKey[0]][0]

    return hubDict, authDict

def hits(graph, epsilon) :

    A, ATranspose, v0, i, mapping, reverseMapping = createInitialAuthVector(graph)
    hubMatrix, authMatrix = HITS(A, ATranspose, v0, epsilon, i)
    hub, auth = generateHubAndAuth(hubMatrix, authMatrix, mapping, reverseMapping)
    return (hub , auth)
