import networkx as nx
from datetime import date, datetime
import math
from collections import defaultdict as dt, OrderedDict
import numpy as np
# np.seterr(divide='ignore', invalid='ignore')

def readInputFile (filename) :

    mapRowIdToOtherDetails = {}
    #mapAnswerIdToOtherDetails = {}
    answerDetails =[]

    for eachLine in open(filename) :
        postId = eachLine[eachLine.find("row Id=") + len("row Id=") + 1 : eachLine.find('"', eachLine.find("row Id=") +  len("row Id=") + 2, len(eachLine))]

        postTypeId = eachLine[eachLine.find("PostTypeId=") + len("PostTypeId=") + 1 : eachLine.find('"', eachLine.find("PostTypeId=") +  len("PostTypeId=") + 2, len(eachLine))]

        ownerUserId = eachLine[eachLine.find("OwnerUserId=") + len("OwnerUserId=") + 1 : eachLine.find('"', eachLine.find("OwnerUserId=") +  len("OwnerUserId=") + 2, len(eachLine))]
        parentId = eachLine[eachLine.find("ParentId=") + len("ParentId=") + 1 : eachLine.find('"', eachLine.find("ParentId=") +  len("ParentId=") + 2, len(eachLine))]
        creationdate= eachLine[eachLine.find("CreationDate=") + len("CreationDate=") + 1 : eachLine.find('"', eachLine.find("CreationDate=") +  len("CreationDate=") + 2, len(eachLine))]
        dateTime = creationdate
        index = dateTime.find("T")
        Date = dateTime[:index]
        #split = Date.split("-")
        #myDate = date(int(split[0]), int(split[1]), int(split[2]))
        #print "printing myDate"
        #print Date

        if postTypeId == '1' :

            myList = []
            myList += [ownerUserId, Date]
            mapRowIdToOtherDetails[postId] = myList

        elif postTypeId == '2' :
            #myList = []
            #myList += [ownerUserId, Date, parentId]
            # mapAnswerIdToOtherDetails[postId] = myList
            split = Date.split('-')
            myDate = date(int(split[0]), int(split[1]), int(split[2]))

            myTup = (ownerUserId, myDate, parentId, postId)
            answerDetails += (myTup,)

        else :
            continue

    # return mapRowIdToOtherDetails, mapAnswerIdToOtherDetails
    return mapRowIdToOtherDetails, answerDetails


def sortAccordingToDate(answerDetails) :

    #answerDetails = [(ownerUserId, Date, parentId, postId),(),....]
    # print answerDetails
    sortedByDate = sorted(answerDetails, key = lambda obj : obj[1])
    return sortedByDate

def printGraph(graph) :
    listOfNodes = graph.nodes();
    for eachNode in listOfNodes :
        print (graph[eachNode])

    # for u, v, w in graph.edges() :
    #     print (u, v, w)

def getMulFactor() :
    ## RETENTION VALUE = P*e^(-Qt)
    ## Here P and Q both are assumed to have the value 1 and one time unit is 6 months

    return 1.0/math.exp(1.0/6)

def adjustWeights(graph, userIdSet) :
    # printGraph(graph)

    mulFactor = getMulFactor()

    for eachNode in graph.nodes() :
        if eachNode not in userIdSet :
            for eachKey in graph[eachNode] :
                graph[eachNode][eachKey][0]['weight'] *= mulFactor


def createUserRelationshipGraph(answerersSortedByDate, mapRowIdToOtherDetails, window) :
    ## answerersSortedByDate = [(ownerUserId, Date, parentId, postId),(),....]
    ## mapRowIdToOtherDetails = {postId : [ownerUserId, Date]}


    # print('In the user RELATIONSHIP graph...')
    # print(mapRowIdToOtherDetails)


    graph = nx.MultiDiGraph()
    weight = 1.0
    begin = answerersSortedByDate[0][1]
    counter = 0
    for eachEntry in answerersSortedByDate :
        u = eachEntry[0]
        v = mapRowIdToOtherDetails[eachEntry[2]][0]
        counter += 1
        if (eachEntry[1] - begin).days > window :
            break
        graph.add_edge(u, v, weight = weight)
        # print(f'adding edge from {u} to {v} in the graph.')

    counter2 = 0
## answerersSortedByDate = [(ownerUserId, Date, parentId, postId),(),....]
## mapRowIdToOtherDetails = {postId : [ownerUserId, Date]}
    userIdSet = set()
    for eachEntry in answerersSortedByDate :
        if counter2 <= counter :
            counter2 += 1
            begin = eachEntry[1]
            continue

        u = eachEntry[0]
        v = mapRowIdToOtherDetails[eachEntry[2]][0]
        graph.add_edge(u, v, weight = weight)
        # print(f'adding edge from {u} to {v} in the graph.')
        userIdSet.add(eachEntry[0])
        if (eachEntry[1] - begin).days >= window :
            begin = eachEntry[1]
            adjustWeights(graph, userIdSet)
            userIdSet.clear()

    return graph


# def calcuateZScore(graph) :

def calculateNodeOutWeights(graph) :

    # print('printing the out edges with weights of 4512 : {}'.format(graph['4512']))

    nodeOutWeightDict = {}
    # for eachNode in graph.nodes() :
    #     nodeOutWeightDict[eachNode] = 0.0
    for eachNode in graph.nodes() :
        for eachKey in graph[eachNode] :
            try :
                nodeOutWeightDict[eachNode] += graph[eachNode][eachKey][0]['weight']
                # if nodeOutWeightDict[eachNode] == 0 :
                    # print(f' out weight of node {eachNode} is 0')
            except KeyError :
                # print(f"keyError for the node {eachNode}")
                nodeOutWeightDict[eachNode] = 0.0

    return nodeOutWeightDict


def top50Experts(sortedOutWeightScore) :
    top50ExpertsList = []
    counter = 0
    for eachTuple in sortedOutWeightScore :
        counter += 1
        top50ExpertsList.append(eachTuple[0])
        if counter >= 50 :
            break
    return top50ExpertsList

def calculateDegree(nodeOutWeightDict) :
    sortedOutWeightScore = sorted(nodeOutWeightDict.items(), key = lambda obj : obj[1], reverse = True)
    # print('printing expertise based on the out edge weights..')
    # print (sortedScore)
    top50ExpertsList = top50Experts(sortedOutWeightScore)
    return sortedOutWeightScore

def calculateZScore(nodeOutWeightDict, graph) :
    zScoreDict = {}
    for eachKey in nodeOutWeightDict :
        zScoreDict[eachKey] = nodeOutWeightDict[eachKey]*1.0 / graph.in_degree(eachKey)

    sortedZScoreList = sorted(zScoreDict.items(), key = lambda obj : obj[1], reverse = True)
    return sortedZScoreList


def calculateModifiedZScore(graph, nodeOutWeightDict) :


    '''
    Modified Z Score = A /  B ; where
    A = ∑ outweights  - ∑ (1 - inweights * 𝛃)
    B = √ (∑ outweights  + ∑ (1 - inweights * 𝛃)) ; 𝛃 is a parameter

    '''



    modifiedZScoreDict = dt(lambda : float('-inf'))

    # print('printing the user relationship graph..')
    # print(graph.edges())


    nodeInWeightDict = dt(lambda : 0.0)

    graph2 = graph.reverse()
    for eachNode in graph2.nodes() :
        for eachKey in graph2[eachNode] :
            # print(f"from {eachNode} to {eachKey}")
            try :
                nodeInWeightDict[eachNode] += 1 - graph[eachNode][eachKey][0]['weight']
            except KeyError :
                pass
                # print(f'keyError for {eachNode}')
                # nodeInWeightDict[eachNode] = 0.0

    for k, v in nodeOutWeightDict.items() :
        try :
            modifiedZScoreDict[k] = (nodeOutWeightDict[k] - nodeInWeightDict[k]) * 1.0 / math.sqrt(nodeOutWeightDict[k] + nodeInWeightDict[k])


        except :
            pass
            # print(f'keyError for {k} in modifiedZScoreDict')
            # modifiedZScoreDict[k] = 0.0

    #
    # lis = ['227', '4348', '10008', '7', '35762', '5', '46355', '3', '87381', '59472', '160951', '49943', '24373', '12135', '92', '69933', '43434', '6094', '1', '49115', '0', '68973', '52138', '39382', '2', '15998', '6297', '61', '72520', '31183', '76024', '29454']
    # print("checking in the new graph now...")
    # for _ in lis :
    #     if int(_) in graph.nodes() :
    #         print(f'{_} is present in the graph.')

    '''
    sorting the dictionary now..
    '''

    sortedModifiedZScoreDict = sorted(modifiedZScoreDict.items(), key = lambda obj : obj[1], reverse = True)

    # print('sorted dictionary based on z score is below: \n*10')
    # print(sortedZScoreDict)

    return sortedModifiedZScoreDict

def calculateExpertise(graph) :

    # calculateModifiedZScore(graph)
    # calculateDegree()
    # calculateHITS()


    #1. sortedOutWeightScore holds the sum of the weights of the out going edges for
    #    each node in the graph in a sorted manner

    #2. nodeOutWeightDict holds the sum of the weights of out going edges for each node.

    '''
    Modified Z Score = A /  B ; where
    A = ∑ outweights  - ∑ (1 - inweights * 𝛃)
    B = √ (∑ outweights  + ∑ (1 - inweights * 𝛃)) ; 𝛃 is a parameter

    '''


    nodeOutWeightDict = calculateNodeOutWeights(graph)
    sortedOutWeightScore = calculateDegree(nodeOutWeightDict)
    # print('printing sorted out weight score..')
    # print(sortedOutWeightScore)
    #sortedZScoreList = calculateZScore(nodeOutWeightDict, graph)

    sortedModifiedZScoreDict = calculateModifiedZScore(graph, nodeOutWeightDict)
    return (sortedOutWeightScore, sortedModifiedZScoreDict)
    #print(sortedModifiedZScoreDict)



def main() :

    filename = 'Posts.xml' ## THIS INPUT FILE CONTAINS THE DATASET.
    window = 30 ## 30 DAYS CORRESPOND TO 1 TIME WINDOW.
    ## mapRowIdToOtherDetails, mapAnswerIdToOtherDetails = readInputFile(filename)
    mapRowIdToOtherDetails, answerDetails = readInputFile(filename)
    sortedByDate = sortAccordingToDate(answerDetails)
    # print ("printing out sortedByDate")
    # for _ in sortedByDate :
    #     print (_[1])
    graph = createUserRelationshipGraph(sortedByDate, mapRowIdToOtherDetails, window)
    degree, z_score = calculateExpertise(graph)
    graphTranspose = graph.reverse()

    from HITS import hits
    epsilon = 1e-7 ## ERROR BOUND.
    hub, auth = hits(graph, epsilon)
    # print('printing hubs..')
    # print(hub)
    # print('printing authorities..')
    # print(auth)
    hits_current = auth
    z_score_current = z_score
    degree_current = degree

    return (hits_current, z_score_current, degree_current)

def pearsonCorrelation(old, new) :

    x = set(str(y) for y in old.keys()) - set(str(z) for z in new.keys())
    # print('printing keys in old but not in new..')
    # print(x)


    y = set(str(y) for y in new.keys()) - set(str(z) for z in old.keys())

    for eachKey in x :

        del(old[int(eachKey)])

    # print('printing the old dict...')
    # print(old)

    for eachKey in y :
        del(new[eachKey])

    # new1 = del(new[y for y in x])
    # print('printing keys in new but not in old..')
    # print(x)
    # print('\n\n\n\n\n\n\n\n\n\n\n\n')
    # print('printing the new dict..')
    # print(new)

    from CORRELATION import correlation

    dict1 = OrderedDict()
    dict2 = OrderedDict()
    sortedTup1 = sorted(old.items(), key = lambda obj : obj[1], reverse = True)
    sortedTup2 = sorted(new.items(), key = lambda obj : obj[1], reverse = True)
    sortedDict1 = OrderedDict()
    sortedDict2 = OrderedDict()

    for (k, v) in sortedTup1 :
        sortedDict1[str(k)] = v

    for (k, v) in sortedTup2 :
        sortedDict2[str(k)] = v

    corr_values = OrderedDict()

    count = 0
    old = dict(old)
    new = dict(new)
    permissible_count = 100

    for eachKey in sortedDict1 :

        dict1[eachKey] = sortedDict1[eachKey]
        try :
            dict2[eachKey] = sortedDict2[eachKey]
        except :
            dict2[eachKey] = 1.0

        count += 1

        if count == permissible_count :
            val = correlation(dict1, dict2)
            corr_values[count] = val
            permissible_count *= 2
            if permissible_count > 1000 :
                break

    # print('returning corr_values')
    return corr_values
    # return None


def plot_points(my_dict, string1, string2) :

    import matplotlib.pyplot as plt

    x_list = [x for x in my_dict.keys()]
    y_list = [x for x in my_dict.values()]

    fig = plt.figure()
    fig.suptitle(string1+" Vs. "+string2, fontsize = 14, fontweight = 'bold')
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel("TOP K USERS ")
    ax1.set_ylabel("PEARSON CORRELATION AT K ")
    plt1=ax1.plot(x_list,y_list ,'b',label=string1)


    # ax2=fig.add_subplot(111)
    # ax2.set_xlabel("TOP K USERS ")
    # ax2.set_ylabel("PEARSON CORRELATION AT K ")
    # plt2=ax2.plot(plot2KeyList, plot2ValueList,'r',label=string2)
    #
    # ax3=fig.add_subplot(111)
    # ax3.set_xlabel("TOP K USERS ")
    # ax3.set_ylabel("PEARSON CORRELATION AT K ")
    # plt3=ax3.plot(plot3KeyList, plot3ValueList,'g',label=string3)

    plt.legend()
    fig.savefig("output/"+string1+"-vs-"+string2+".pdf")
    # plt.show()
    plt.close(fig)


def correlation_between_metrics(new_hits, new_z_score, new_degree) :

    '''

        THIS FUNCTION JUST FINDS THE CORRELATION BETWEEN THE ALREADY EXISTING METRICS AGAINST THE NEW METRICS.

    '''

    from THESIS_STAGE_2 import main2
    old_hits, old_z_score, old_degree = main2()

    hits_corr_values = pearsonCorrelation(dict(old_hits), dict(new_hits))
    z_score_corr_values = pearsonCorrelation(dict(old_z_score), dict(new_z_score))
    degree_corr_values = pearsonCorrelation(dict(old_degree), dict(new_degree))

    # hits_comparison = correlation(dict(old_hits), dict(new_hits))
    # print('corrcoef returns..')
    # print(hits_comparison)
    # z_score_comparison = correlation(dict(old_z_score), dict(new_z_score))
    # degree_comparison = correlation(dict(old_degree), dict(new_degree))
    # print(z_score_comparison)
    # print(degree_comparison)

    plot_points(hits_corr_values, 'HITS', 't - HITS')
    plot_points(z_score_corr_values, 'z score', 't - z score')
    plot_points(degree_corr_values, 'DEGREE', 't - DEGREE')

    '''
        ASCERTAINING THE CORRELATION FOR FIRST 100, THEN 200, THEN 400, THEN 800, THEN 1000 USERS.

    '''



# def comparison_last_two_vs_whole_dataset(new_hits, new_z_score, new_degree) :





if __name__ == '__main__' :

    new_hits, new_z_score, new_degree = main()


    '''

                                    CORRELATION BETWEEN THE METRICS IN THE PAPER AND
                                    THE MODIFIED ONE.

    '''

    correlation_between_metrics(new_hits, new_z_score, new_degree)
    # comparison_last_two_vs_whole_dataset(new_hits, new_z_score, new_degree)
