from datetime import date
import math

def memoryScore(mapUserToLastDate) :
	retentionDict = {}
	for eachKey in mapUserToLastDate :
		noOfDays = (date.today()-mapUserToLastDate[eachKey]).days
		retentionDict[eachKey] = pow(math.e, -1.0*(noOfDays/180))
	return retentionDict


def modification(mapUserToLastDate) :

	## THIS IS MY FIRST MODEL. IT JUST CALCULATES SCORE OF EACH OF THE USERS BASED ON WHEN THEY HAD ANSWERED LAST.
	retentionDict = memoryScore(mapUserToLastDate)
	return retentionDict

def M_spam(filename) :
	mapUserToSpamCount = {}
	mapPostIdToOwner = {}

	for eachLine in open(filename) :
		index = eachLine.find('PostTypeId="1"')
		if index == -1 :
			continue
		else :
			ownerUserId = eachLine[eachLine.find('OwnerUserId="') + len('OwnerUserId="') : eachLine.find('"', eachLine.find('OwnerUserId="') + len('OwnerUserId="')+1, len(eachLine))]
			postId = eachLine[eachLine.find('row Id="') + len('row Id="') : eachLine.find('"', eachLine.find('row Id="') + len('row Id="') + 1, len(eachLine))]
			mapPostIdToOwner[postId] = ownerUserId

	for eachLine in open(filename) :
		index = eachLine.find('PostTypeId="2"')
		if index == -1 :
			continue
		else :
			ownerUserId = eachLine[eachLine.find('OwnerUserId="') + len('OwnerUserId="') : eachLine.find('"', eachLine.find('OwnerUserId="') + len('OwnerUserId="')+1, len(eachLine))]
			parentId = eachLine[eachLine.find('ParentId="') + len('ParentId="') : eachLine.find('"', eachLine.find('ParentId="') + len('ParentId="') + 1, len(eachLine))]
			if parentId in mapPostIdToOwner :
				mapUserToSpamCount[int(ownerUserId)] = mapUserToSpamCount.get(int(ownerUserId) , 0) + 1

	return mapUserToSpamCount


def M_getActiveDatesList(filename) :

	mapUserToDateList = {}
	for eachLine in open(filename) :
		if 'PostTypeId="2"' in eachLine :
			ownerUserId = eachLine[eachLine.find('OwnerUserId="') + len('OwnerUserId="') : eachLine.find('"', eachLine.find('OwnerUserId="') + len('OwnerUserId="') + 1, len(eachLine))]
			creationDate = eachLine[eachLine.find('CreationDate="') + len('CreationDate="') : eachLine.find('T', eachLine.find('CreationDate="') + len('CreationDate="') + 1, len(eachLine))]
			if int(ownerUserId) in mapUserToDateList :
				mapUserToDateList[int(ownerUserId)].append(creationDate)
			else :
				mapUserToDateList[int(ownerUserId)] = [creationDate]
	return mapUserToDateList
