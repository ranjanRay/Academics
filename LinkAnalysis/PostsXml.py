## THIS FILE JUST PREPROCESSES THE posts.xml FILE TO GENERATE ALL INFORMATION FROM EVERY ROW IN THE XML FILE.

from datetime import date

class Posts :
	Id = -1
	postTypeId = -1
	ownerUserId = -1
	parentId = -1
	creationDate = -1
	def __init__(this, Id, postTypeId, ownerUserId, parentId, creationDate) :
		this.Id = Id
		this.postTypeId = postTypeId
		this.ownerUserId = ownerUserId
		this.parentId = parentId
		this.creationDate = creationDate


def getPostsInfo(filename) :

	postAttribute = [] ## contains all the required details from each row in the xml file

	bestAnswerSet = set() ## ID of the answer that has been selectes as best answer
	mapUserToBestAnswer = {} ## Number of best answers given by this user
	mapUserToNumberOfAnswers = {} ## Total answer attempts made by this user
	userToPositiveVotes = {} ## stores total # of positive votes the user received on the posted answers
	userToNegativeVotes = {}	## stores total # of negative votes the user received on the posted answers
	mapUserToNumberOfQuestions = {}
	mapUserToLastDate = {}

	for eachLine in open(filename) :
		postId = eachLine[eachLine.find("row Id=") + len("row Id=") + 1 : eachLine.find('"', eachLine.find("row Id=") +  len("row Id=") + 2, len(eachLine))]

		postTypeId = eachLine[eachLine.find("PostTypeId=") + len("PostTypeId=") + 1 : eachLine.find('"', eachLine.find("PostTypeId=") +  len("PostTypeId=") + 2, len(eachLine))]

		ownerUserId = eachLine[eachLine.find("OwnerUserId=") + len("OwnerUserId=") + 1 : eachLine.find('"', eachLine.find("OwnerUserId=") +  len("OwnerUserId=") + 2, len(eachLine))]

		parentId = eachLine[eachLine.find("ParentId=") + len("ParentId=") + 1 : eachLine.find('"', eachLine.find("ParentId=") +  len("ParentId=") + 2, len(eachLine))]

		creationdate= eachLine[eachLine.find("CreationDate=") + len("CreationDate=") + 1 : eachLine.find('"', eachLine.find("CreationDate=") +  len("CreationDate=") + 2, len(eachLine))]

		present = eachLine.find("AcceptedAnswerId=")

		if present is not -1 :
			acceptedAnswerId = eachLine[eachLine.find("AcceptedAnswerId=") + len("AcceptedAnswerId=") + 1 : eachLine.find('"', eachLine.find("AcceptedAnswerId=") +  len("AcceptedAnswerId=") + 2, len(eachLine))]

		#print postId
		#print "parentId: "+parentId

		if postId in bestAnswerSet :
			mapUserToBestAnswer[ownerUserId] = mapUserToBestAnswer.get(ownerUserId, 0)+1

		if present != -1 :
			bestAnswerSet.add(acceptedAnswerId)

		if postTypeId == str(2) :
			mapUserToNumberOfAnswers[ownerUserId] = mapUserToNumberOfAnswers.get(ownerUserId, 0)+1
			score = int(eachLine[eachLine.find("Score=") + len("Score=") + 1 : eachLine.find('"', eachLine.find("Score=") +  len("Score=") + 2, len(eachLine))])
			dateTime = eachLine[eachLine.find("CreationDate=") + len("CreationDate=") + 1 : eachLine.find('"', eachLine.find("CreationDate=") +  len("CreationDate=") + 2, len(eachLine))]
			index = dateTime.find("T")
			Date = dateTime[:index]
			split = Date.split("-")
			myDate = date(int(split[0]), int(split[1]), int(split[2]))
			#print "printing the extracted date....."
			# print myDate
			try :
				previous = mapUserToLastDate[int(ownerUserId)]
				if myDate - previous > 0 :
					mapUserToLastDate[int(ownerUserId)] = myDate
			except :
				mapUserToLastDate[int(ownerUserId)] = myDate

			if score > 0 :
				userToPositiveVotes[int(ownerUserId)] = userToPositiveVotes.get(int(ownerUserId), 0) + int(score)
			elif score < 0 :
				userToNegativeVotes[int(ownerUserId)] = userToNegativeVotes.get(int(ownerUserId), 0) + -1*(int(score))
		elif  postTypeId == str(1) :
			mapUserToNumberOfQuestions[int(ownerUserId)] = mapUserToNumberOfQuestions.get(int(ownerUserId), 0)+1

		try :
			postid = int(postId)
			posttypeid = int(postTypeId)
			ownerid = int(ownerUserId)
			try :
				parentid = int(parentId)
				obj = Posts(postid, posttypeid, ownerid, parentid, creationdate);
				postAttribute.append(obj)
			except :
				obj = Posts(postid, posttypeid, ownerid, -1, creationdate)
				postAttribute.append(obj)

		except :
			continue

	return postAttribute, mapUserToBestAnswer, mapUserToNumberOfAnswers, userToPositiveVotes, userToNegativeVotes, mapUserToNumberOfQuestions, mapUserToLastDate
