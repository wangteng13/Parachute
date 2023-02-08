# coding=utf-8

import os

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 5
Software = 'Redis'

BugList = []

# read the file and return string
def readfile(filepath):
    fp = open(filepath, 'r')
    fileread = fp.read()
    fileread = fileread.replace("\r", "")
    fp.close()
    return fileread

# write the string into the file
def writefile(content, filepath, di):
    fp = open(filepath, di)
    fp.write(content)
    return fp.close()

def findKeyword(con):
	pos1 = con.find("[")
	if pos1 == -1: return False
	con = con[pos1+1:]
	pos3 = con.find("]")
	if pos3 == -1: return False
	con = con[:pos3]

	if con.find("ok")!= -1 or con.find("err")!=-1:
		return True
	return False
def mySplit(mystring):
    mystring = mystring.split('\n')
    mytest = [i for i in mystring if len(i) > 0]
    return mytest

def mySplitR(mytest):
	res = []
	for i in range(len(mytest)):
		if findKeyword(mytest[i]) == True:
			res.append(mytest[i])
	return res
def findstr(ml, con):
    for i in range(len(ml)):
        if ml[i].find(con) != -1: return i
    return -1
# check whether the two result lists are same
# return value 
# 0  : Failed
# 1  : Successed
def checkTheLists(MutatedTestResult, OriginalTestResult, UpdateString):
	len1 = len(MutatedTestResult)
	len2 = len(OriginalTestResult)
	print len1,len2

	j = 0
	for i in range(len1):
		if MutatedTestResult[i].find("#####@@ This is Inserted by TestMytater! @@#####")!=-1: continue
		if MutatedTestResult[i].find(UpdateString.replace(";", ""))!=-1: continue
		
		if j>=len2: break
		if MutatedTestResult[i] != OriginalTestResult[j]:
			return [0,OriginalTestResult[j],MutatedTestResult[i]]
		j = j+1
 
	return [1, "",""]

def findtheprestmt(TestResult, OperationList):
        pos = 0
	if len(OperationList) == 0: return -1

	for i in range(len(TestResult)):
		if TestResult[i].replace("\t","").replace(" ","").find(OperationList[pos].replace("\t","").replace(" ","")) != -1:
			pos = pos + 1
		if pos == len(OperationList):
			print "pre stmt: ",TestResult[i]
			return i
	return -1

# check whether the two result files are same after the UpdateString
# return value 
# -1 : ERROR or Warning
# 0  : Failed
# 1  : Successed, no bugs
# Note: maybe there are some false postive
def checkResult(MutatedTestResult, OriginalTestResult, UpdateString, config):
	print "checkResult,",MutatedTestResult, OriginalTestResult
	MutatedTestResultFile = MutatedTestResult
	OriginalTestResultFile = OriginalTestResult

	UpdateString = UpdateString.replace('\n', '')
	MutatedTestResult = mySplit(readfile(MutatedTestResult))
	OriginalTestResult = mySplit(readfile(OriginalTestResult))

	pos1 = findstr(MutatedTestResult, UpdateString)
	if pos1 == -1:
		print "ERROR: Can not find UpdateString and NXT in MutatedTestResult!\n"
		return -1
	pcon = MutatedTestResult[pos1-1]
	pcon = pcon[pcon.find("]: ")+3:]
	pos2 = findstr(OriginalTestResult[pos1-2:], pcon)
	MutatedTestResult = mySplitR(MutatedTestResult[pos1:])
	OriginalTestResult = mySplitR(OriginalTestResult[pos1-2:][pos2+1:])


	if len(MutatedTestResult)!=len(OriginalTestResult):
		print "length not same!\n"
	if MutatedTestResult != OriginalTestResult:
		BugList.append([config, OriginalTestResultFile, MutatedTestResultFile])
	return 0


def getOperationListFromTestResult(config, ResultFile):
	UpdateString = getUpdateStringFromTestResult(config, ResultFile)
	Dir = "./"+Software+"/NewTestSuit/"+config+"/"
	pos = ResultFile.find("_StartWith_")
	TestFile = Dir + ResultFile[:pos] + ".sql"
	ppos = ResultFile.find("_UpdateWith_")
	TestDir = Dir + ResultFile[:ppos] + "/" + ResultFile[:pos] + ".sql"
	test = readfile(TestDir).replace("\r","")
	test = test.split('\n')
	test = [i for i in test if len(i) > 2 and i[len(i)-1]==';' and i[0]!='-'  and i[1]!='-']
        

        
	res = []
	for i in range(len(test)):
                #print "in ", str(i)
		if test[i].find(UpdateString) == -1:
			res.append(test[i])
		if test[i].find(UpdateString) != -1:
			if i+1 < len(test) and len(test[i+1])>2 :
				res.append(test[i+1])
			break
        print len(res)
	if len(res) > 20: return res[len(res)-20:]
	return res

def getUpdateStringFromTestResult(config, ResultFile):
	Dir = "./"+Software+"/NewTestSuit/"+config+"/"
	pos = ResultFile.find("_StartWith_")
	TestFile = Dir + ResultFile[:pos] + ".sql"
	ppos = ResultFile.find("_UpdateWith_")
	TestDir = Dir + ResultFile[:ppos] + "/" + ResultFile[:pos] + ".sql"
	#print TestFile
	test = readfile(TestDir)
	test = mySplit(test)
	pos = -1
	for i in range(len(test)):
		if test[i].find('#####@@ This is Inserted by TestMytater! @@#####')!=-1:
			pos = i
	if pos > -1 and pos < len(test):
		return test[pos+1]
	else:
		return "ERROR when find UpdateString"

def isOriginalTest(ResultFile):
	if ResultFile.find("_UpdateWith_") == -1:
		return True
	else:
		return False

def getStartWithFromTestResult(ResultFile):
	pos = ResultFile.find("_StartWith_")
	Value = ResultFile[pos:]
	Value = Value.replace("_StartWith_", "")
	Value = Value.replace(".result", "")
	return Value

def getUpdateWithFromTestResult(ResultFile):
	pos = ResultFile.find("_UpdateWith_")
	Value = ResultFile[pos:]
	Value = Value.replace("_UpdateWith_", "")

	pos = Value.find("_mutated_")
	Value = Value[:pos]
	return Value

def checkOneTestResult(config, oneTest, oneTest_path):
	ResultFiles = os.listdir(oneTest_path)
	for ResultFile1 in ResultFiles: 
		if isOriginalTest(ResultFile1) == True:
			for ResultFile2 in ResultFiles: 
				if isOriginalTest(ResultFile2) == False:
					StartWith1 = getStartWithFromTestResult(ResultFile1)
					StartWith2 = getStartWithFromTestResult(ResultFile2)
					UpdateWith2 = getUpdateWithFromTestResult(ResultFile2)
					if StartWith1==UpdateWith2 and StartWith2 != UpdateWith2:
						UpdateString = "OCTester is testing!"
						print "UpdateString=",UpdateString
						res = checkResult(oneTest_path+"/"+ResultFile2, oneTest_path+"/"+ResultFile1, UpdateString, config)
						

def mainChecker():
	BugList = []

	Dir = "./" + Software + "/TestResult/"
	dir_or_files = os.listdir(Dir)

	for dir_file in dir_or_files:
                print "dir_file: ",dir_file
		config_path = os.path.join(Dir, dir_file)
		if os.path.isdir(config_path):
			config = dir_file
			TestResultDirs = os.listdir(config_path)
			for oneTest in TestResultDirs:
				print "oneTest: ",oneTest
				oneTest_path = os.path.join(config_path, oneTest)
				if os.path.isdir(oneTest_path):
					checkOneTestResult(config, oneTest, oneTest_path)

def recordBugList(Path):
    res = ""
    for item in BugList:
        res = res + str(item) + "\n"
    writefile(res, Path, "w+")


mainChecker()
recordBugList("./alarm.txt")

