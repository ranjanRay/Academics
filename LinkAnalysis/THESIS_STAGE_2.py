from PostsXml import getPostsInfo
from Modifications import modification, M_spam, memoryScore, M_getActiveDatesList
from collections import OrderedDict
from datetime import date
import networkx as nx
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import warnings
import collections
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


def createDictionary(postList) :
	postIdToOwnerIdDict = {}
	for eachObj in postList :
		if eachObj.postTypeId != -1 :
			postIdToOwnerIdDict[eachObj.Id] = eachObj.ownerUserId
	#print postIdToOwnerIdDict
	userToUserDict = {}
	for eachObj in postList :
		if eachObj.postTypeId == 2 :
			#userToUserDict[postIdToOwnerIdDict[eachObj.parentId]] = eachObj.ownerUserId
			if postIdToOwnerIdDict[eachObj.parentId] in userToUserDict :
				myList = []
				myList = userToUserDict[postIdToOwnerIdDict[eachObj.parentId]]
				#print myList
				myList = myList+[eachObj.ownerUserId]
				userToUserDict[postIdToOwnerIdDict[eachObj.parentId]] = myList
				del myList
			else :
				userToUserDict[postIdToOwnerIdDict[eachObj.parentId]] = [eachObj.ownerUserId]

	return userToUserDict

def createGraph(adjList) :
	G = nx.DiGraph()
	for eachKey in adjList :
		for eachValue in adjList[eachKey] :
			G.add_edge(eachKey, eachValue)
			#print G.edges()
	return G

def executeHits(G) :
	h, a = nx.hits(G, max_iter = 100, tol = 1e-08, nstart = None, normalized = True)
	return h, a

def sortReverse(auth) :
	items = [(v, k) for k, v in auth.items()]
	items.sort(reverse = True)
	items = [(k, v) for (v, k) in items]
	return items

def getDegreeScore(graph, myDict) :
	indegree = {}
	for eachKey in myDict.keys() :
		#print "key whose indegree is to be found: "+str(eachKey)
		indegree[eachKey] = graph.in_degree(eachKey)

	for eachValue in myDict.values() :
		for eachElement in eachValue :
			indegree[eachElement] = graph.in_degree(eachElement)
	return indegree


def pearsonCorrelation(authScore, degreeScore) :
	listAuth =  []
	listDegree = []
	for eachKey in authScore.keys() :
		listAuth.append(authScore[eachKey])
	#	print "current Key "+str(eachKey)
		try :
			listDegree.append(degreeScore[eachKey])
		except :
			listDegree.append(0)
	#print np.corrcoef(listAuth, listDegree)[0, 1]
	return np.corrcoef(listAuth, listDegree)[0, 1]


def percentBest(mapUserToBestAnswer, mapUserToNumberOfAnswers) :
	percentBestScore = {}
	for eachKey in mapUserToBestAnswer.keys() :
		#print mapUserToBestAnswer[eachKey]
		#print mapUserToNumberOfAnswers[eachKey]
		percentBestScore[int(eachKey)] = float(mapUserToBestAnswer[eachKey])/ mapUserToNumberOfAnswers[eachKey]

	for eachKey in mapUserToNumberOfAnswers.keys() :
		if int(eachKey) not in percentBestScore :
			percentBestScore[int(eachKey)] = 0.0

	return percentBestScore

def votes(positiveDict, negativeDict, answersAttempted) :
	voteScore = {}
	for eachKey in positiveDict.keys() :
		if eachKey in negativeDict :
			x = float(positiveDict[eachKey])/(positiveDict[eachKey] + negativeDict[eachKey])
			y = 1.0*(positiveDict[eachKey] - negativeDict[eachKey])*x
			voteScore[eachKey] = y / answersAttempted[str(eachKey)]
		else :
			try :
				voteScore[eachKey] = 1.0/ answersAttempted[str(eachKey)]
			except :
				voteScore[eachKey] = 0.0

	for eachkey in answersAttempted :
		if int(eachkey) not in voteScore :
			voteScore[int(eachkey)] = 0.0

	return voteScore

def top50Auth(authScore) :

	printAuthInBlue = []
	printAuthScore = []
	printRemaining = []
	i = 0
	for eachEntry in authScore :
		i += 1
		printAuthInBlue.append(int(eachEntry[0]))
		printAuthScore.append(eachEntry[1])
		if i == 30 :
			break

	printRemaining = []
	for eachEntry in authScore :
		if eachEntry[0] not in printAuthInBlue :
			printRemaining.append(int(eachEntry[0]))

	return printAuthInBlue, printAuthScore, printRemaining

def plotBarForTop50Auth(X, Y, string1, string2) :

	fig=plt.figure()
	fig.suptitle("TOP 30 AUTHORITIES BASED ON "+string1,fontsize=14,fontweight="bold")
	ax=fig.add_subplot(111)
	fig.subplots_adjust(top=0.95)
	ax.set_xlabel("USER ID", fontsize = 8)
	ax.set_ylabel(string2)
	plt.bar(range(len(Y)),Y, align='center')
	plt.xticks(range(len(X)),X)
	fig.autofmt_xdate(rotation=90)
	#plt.show()
	fig.savefig("output/top50AuthBy"+string1+".pdf")

def printGraph(G, printAuthInBlue, printRemaining) :
	fig = plt.figure()
	fig.suptitle("USER RELATIONSHIP GRAPH", fontsize = 14, fontweight = "bold")
	sp = nx.spring_layout(G)
	nx.draw_networkx(G, pos = sp, with_labels = False, node_size = 35, width = 0.1)
	nx.draw_networkx_nodes(G,sp,printAuthInBlue,node_color='blue', node_size = 40, width=0.1)
	nx.draw_networkx_nodes(G,sp,printRemaining,node_color='green', node_size = 35, width=0.1)
	fig.savefig("output/graph.pdf")

def extractTop50Authorities(authScore) :

	printAuthInBlue = [] ## LIST OF AUTH. USER IDs
	printAuthScore = [] ## LIST OF CORRESPONDING AUTHORITY SCORES
	printAuthInBlue, printAuthScore = top50Auth(authScore)
	plotBarForTop50Auth(printAuthInBlue, printAuthScore)
	return printAuthInBlue, printAuthScore

def plotPoints(plot1, plot2, plot3, string1, string2, string3, string4) :
	plot1KeyList = []
	plot2KeyList = []
	plot3KeyList = []
	plot1ValueList = []
	plot2ValueList = []
	plot3ValueList = []

	plot1KeyList = plot1.keys()
	plot2KeyList = plot2.keys()
	plot3KeyList = plot3.keys()

	plot1ValueList = plot1.values()
	plot2ValueList = plot2.values()
	plot3ValueList = plot3.values()

	fig = plt.figure()
	fig.suptitle(string1+", "+string2+" AND "+string3+" Vs. "+string4, fontsize = 14, fontweight = 'bold')
	ax1 = fig.add_subplot(111)
	ax1.set_xlabel("TOP K USERS ")
	ax1.set_ylabel("PEARSON CORRELATION AT K ")
	plt1=ax1.plot(plot1KeyList,plot1ValueList ,'b',label=string1)

	ax2=fig.add_subplot(111)
	ax2.set_xlabel("TOP K USERS ")
	ax2.set_ylabel("PEARSON CORRELATION AT K ")
	plt2=ax2.plot(plot2KeyList, plot2ValueList,'r',label=string2)

	ax3=fig.add_subplot(111)
	ax3.set_xlabel("TOP K USERS ")
	ax3.set_ylabel("PEARSON CORRELATION AT K ")
	plt3=ax3.plot(plot3KeyList, plot3ValueList,'g',label=string3)

	plt.legend()
	fig.savefig("output/"+string1+"-"+string2+"-"+string3+"vs"+string4+".pdf")
	#plt.show()
	plt.close(fig)

def topKUsersCorrelation(sortedDict1, sortedDict2, sortedDict3, Dict, string1, string2, string3, string4) :

	plot1 = collections.OrderedDict()
	plot2 = collections.OrderedDict()
	plot3 = collections.OrderedDict()
	noOfUsers = 100
	while noOfUsers <= 1000 :
		Dict1 = collections.OrderedDict()
		Dict2 = collections.OrderedDict()
		Dict3 = collections.OrderedDict()
		k = 1
		for eachKey in sortedDict1.keys() :
			if k > noOfUsers :
				break
			Dict1[eachKey] = sortedDict1[eachKey]
			k += 1

		k = 1
		for eachKey in sortedDict2.keys() :
			if k > noOfUsers :
				break
			Dict2[eachKey] = sortedDict2[eachKey]
			k += 1

		k = 1
		for eachKey in sortedDict3.keys() :
			if k > noOfUsers :
				break
			Dict3[eachKey] = sortedDict3[eachKey]
			k += 1
		point1 = pearsonCorrelation(Dict1, Dict)
		point2 = pearsonCorrelation(Dict2, Dict)
		point3 = pearsonCorrelation(Dict3, Dict)
		plot1[noOfUsers] = point1
		plot2[noOfUsers] = point2
		plot3[noOfUsers] = point3
		noOfUsers += 100
		# while ends
	plotPoints(plot1, plot2, plot3, string1, string2, string3, string4)

def getZScore(mapUserToNumberOfQuestions, mapUserToNumberOfAnswers) :

	zScoreDict = {}
	for eachKey in mapUserToNumberOfAnswers :
		a = mapUserToNumberOfAnswers[eachKey]
		try :
			q = mapUserToNumberOfQuestions[eachKey]
			tempScore = 1.0*(a - q)/math.sqrt(a+q)
			zScoreDict[int(eachKey)] = tempScore
		except :
			zScoreDict[int(eachKey)] = 1.0*a/math.sqrt(a)

	for eachKey in mapUserToNumberOfQuestions :
		if int(eachKey) not in zScoreDict :
			q = mapUserToNumberOfQuestions[eachKey]
			zScoreDict[int(eachKey)] = -1.0*math.sqrt(q)


	# print('The keys in the zScoreDict are as below::')
	# for eachKey in zScoreDict :
	# 	print(eachKey)

	return zScoreDict

def getModifiedScore(retentionDict, Dict) :

	modifiedScoreDict = {}
	for eachKey in retentionDict :
		score = retentionDict[eachKey]*Dict[eachKey]
		modifiedScoreDict[eachKey] = score

	return modifiedScoreDict

def computeRetentionScore(retentionDict, auth, degree, zScoreDict, voteDict, percentBestDict, string) :

	modifiedAuthDict = getModifiedScore(retentionDict, auth)
	modifiedDegreeDict = getModifiedScore(retentionDict, degree)
	modifiedZScoreDict = getModifiedScore(retentionDict, zScoreDict)
	modifiedVotesDict = getModifiedScore(retentionDict, voteDict)
	modifiedPercentBestDict = getModifiedScore(retentionDict, percentBestDict)

	modifiedAuthScore = sortReverse(modifiedAuthDict)
	modifiedDegreeScore = sortReverse(modifiedDegreeDict)
	modifiedZScore = sortReverse(modifiedZScoreDict)

	topKUsersCorrelation(OrderedDict(modifiedAuthScore), OrderedDict(modifiedDegreeScore), OrderedDict(modifiedZScore), modifiedPercentBestDict, string+"-m-HITS", string+"-m-DEGREE", string+"-m-Z-SCORE", string+"-m-%BEST")
	topKUsersCorrelation(OrderedDict(modifiedAuthScore), OrderedDict(modifiedDegreeScore), OrderedDict(modifiedZScore), modifiedVotesDict, string+"-m-HITS", string+"-m-DEGREE", string+"-m-Z-SCORE", string+"-m-VOTES")


def basicRetentionModel(auth, degree, zScoreDict, voteDict, percentBestDict, mapUserToLastDate) :

	retentionDict = modification(mapUserToLastDate) ## modification() is defined in the Modifications.py file.
	computeRetentionScore(retentionDict, auth, degree, zScoreDict, voteDict, percentBestDict, "Basic")

def getDate(string) :
	tempList = string.split('-')
	return date(int(tempList[0]), int(tempList[1]), int(tempList[2]))

def calculateDistributedRetentionScore(listOfSets, mapUserToDateList) :
	## THE VALUE OF `A` in the forgetting curve changes as we calculate the previous contribution..
	distributedRetentionScoreDict = {}

	for eachKey in mapUserToDateList.keys() :
		if eachKey in listOfSets[0] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 1.0
			continue
		if eachKey in listOfSets[1] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.95*pow(math.e, -1.0*(math.sqrt(1)))
		if eachKey in listOfSets[2] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.90*pow(math.e, -1.0*(math.sqrt(2)))
		if eachKey in listOfSets[3] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.85*pow(math.e, -1.0*(math.sqrt(3)))
		if eachKey in listOfSets[4] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.80*pow(math.e, -1.0*(math.sqrt(4)))
		if eachKey in listOfSets[5] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.75*pow(math.e, -1.0*(math.sqrt(5)))
		if eachKey in listOfSets[6] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.70*pow(math.e, -1.0*(math.sqrt(6)))
		if eachKey in listOfSets[7] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.65*pow(math.e, -1.0*(math.sqrt(7)))
		if eachKey in listOfSets[8] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.60*pow(math.e, -1.0*(math.sqrt(8)))
		if eachKey in listOfSets[9] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.55*pow(math.e, -1.0*(math.sqrt(9)))
		if eachKey in listOfSets[10] :
			distributedRetentionScoreDict[eachKey] = distributedRetentionScoreDict.get(eachKey, 0.0) + 0.50*pow(math.e, -1.0*(math.sqrt(10)))

	return distributedRetentionScoreDict

def divideIntoRanges(mapUserToDateList) :

	listOfSets = [set() for i in range(11)]
	for eachKey in mapUserToDateList.keys() :
		dateList = []
		dateList = mapUserToDateList[eachKey]
		dateList = sorted(mapUserToDateList[eachKey], reverse = True)
		for entry in dateList :
			date = getDate(entry)
			daysDiff = (date.today() - date).days
			if daysDiff < 180 :
				listOfSets[0].add(eachKey)
			elif daysDiff >= 180 and daysDiff < 360 :
				listOfSets[1].add(eachKey)
			elif daysDiff >= 360 and daysDiff < 540 :
				listOfSets[2].add(eachKey)
			elif daysDiff >= 540 and daysDiff < 720 :
				listOfSets[3].add(eachKey)
			elif daysDiff >= 720 and daysDiff < 900 :
				listOfSets[4].add(eachKey)
			elif daysDiff >= 900 and daysDiff < 1080 :
				listOfSets[5].add(eachKey)
			elif daysDiff >= 1080 and daysDiff < 1260 :
				listOfSets[6].add(eachKey)
			elif daysDiff >= 1260 and daysDiff < 1440 :
				listOfSets[7].add(eachKey)
			elif daysDiff >= 1440 and daysDiff < 1620 :
				listOfSets[8].add(eachKey)
			elif daysDiff >= 1620 and daysDiff < 1800 :
				listOfSets[9].add(eachKey)
			else :
				listOfSets[10].add(eachKey)

	return listOfSets

def distributedRetentionModel(filename, auth, degree, zScoreDict, voteDict, percentBestDict) :
	mapUserToDateList = {}
	mapUserToDateList = M_getActiveDatesList(filename)
	#print mapUserToDateList
	listOfSets = divideIntoRanges(mapUserToDateList)
	distributedRetentionScoreDict = calculateDistributedRetentionScore(listOfSets, mapUserToDateList)
	computeRetentionScore(distributedRetentionScoreDict, auth, degree, zScoreDict, voteDict, percentBestDict, "Distr.")
	#print distributedRetentionScoreDict

def main2() :

	filename = "Posts.xml"
	postList, mapUserToBestAnswer, mapUserToNumberOfAnswers, userToPositiveVotes, userToNegativeVotes, mapUserToNumberOfQuestions, mapUserToLastDate = getPostsInfo(filename) ## GETS DETAILS ABOUT THE EACH ENTRY IN THE posts.xml FILE.  THE CODE FOR THIS FUCNTION IS IN PostsXml.py FILE.
	adjList = createDictionary(postList) ## CREATES ADJACENCY LIST OF CONNECTED USERS
	G = createGraph(adjList) ## GRAPH CREATION DONE
	hub, auth = executeHits(G) ## EXECUTE HITS ON THE GRAPH
	degree = getDegreeScore(G, adjList) ## DEGREE SCORE FROM THE GRAPH

	zScoreDict = getZScore(mapUserToNumberOfQuestions, mapUserToNumberOfAnswers)

	hits_result = auth
	z_score_result = zScoreDict
	degree_result = degree

	return (hits_result, z_score_result, degree_result)


def main() :
	filename = "Posts.xml"
	postList, mapUserToBestAnswer, mapUserToNumberOfAnswers, userToPositiveVotes, userToNegativeVotes, mapUserToNumberOfQuestions, mapUserToLastDate = getPostsInfo(filename) ## GETS DETAILS ABOUT THE EACH ENTRY IN THE posts.xml FILE.  THE CODE FOR THIS FUCNTION IS IN PostsXml.py FILE.


		################################                      SPAMMERS           ###########################################
		## WEEDING OUT THE SPAMMERS.

	mapUserToSpamCount = M_spam(filename) ## this function is in the Modificatios.py file.


	adjList = createDictionary(postList) ## CREATES ADJACENCY LIST OF CONNECTED USERS
	G = createGraph(adjList) ## GRAPH CREATION DONE
	hub, auth = executeHits(G) ## EXECUTE HITS ON THE GRAPH
	authScore = sortReverse(auth) ## SORTED AUTHORITY SCORES
	degree = getDegreeScore(G, adjList) ## DEGREE SCORE FROM THE GRAPH
	degreeScore = sortReverse(degree) ##SORTED DEGREE SCORES

	printAuthInBlue = [] ## LIST OF AUTH. USER IDs
	printAuthScore = [] ## LIST OF CORRESPONDING AUTHORITY SCORES
	printAuthInBlue, printAuthScore, printRemaining = top50Auth(authScore)
	plotBarForTop50Auth(printAuthInBlue, printAuthScore, "HITS", "AUTHORITY VALUES")
	printAuthByDegree, printAuthByDegreeScore, remainingByDegree = top50Auth(degreeScore)
	plotBarForTop50Auth(printAuthByDegree, printAuthByDegreeScore, "DEGREE", "DEGREE VALUES")

	printGraph(G, printAuthInBlue, printRemaining) ## GRAPH PRINTING MARKING TOP AUTHORITIES IN BLUE
	#hubScore = sortReverse(hub)

	percentBestDict = percentBest(mapUserToBestAnswer, mapUserToNumberOfAnswers) ## %BEST
	zScoreDict = getZScore(mapUserToNumberOfQuestions, mapUserToNumberOfAnswers)
	zScore = sortReverse(zScoreDict)
	## finds top k users.. also genertes the graph for the same
	#topKUsersHitsAndDegreeVsPercentBest(OrderedDict(authScore), OrderedDict(degreeScore), percentBestDict)
	topKUsersCorrelation(OrderedDict(authScore), OrderedDict(degreeScore), OrderedDict(zScore), percentBestDict, "HITS", "DEGREE", "Z-SCORE", "%BEST")
	voteDict = votes(userToPositiveVotes, userToNegativeVotes, mapUserToNumberOfAnswers)
	topKUsersCorrelation(OrderedDict(authScore), OrderedDict(degreeScore), OrderedDict(zScore), voteDict, "HITS", "DEGREE", "Z-SCORE", "VOTES")


	###############  *****************  MODIFICATIONS  ******************************************
	## Modifications.py contains the function modification() which implements different modifications.

	basicRetentionModel(auth, degree, zScoreDict, voteDict, percentBestDict, mapUserToLastDate)
	distributedRetentionModel(filename, auth, degree, zScoreDict, voteDict, percentBestDict)


if __name__ == "__main__" :

	main()

else :
	main2()
