# coding=utf-8

import os

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 5
Software = 'Httpd'

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

def mySplit(mystring):
    mystring = mystring.split('\n')
    mytest = [i for i in mystring if len(i) > 0]
    return mytest

def mySplitR(mytest):
	res = []
	for i in range(len(mytest)):
		res.append(mytest[i])
	return res
def findstr(ml, con):
    for i in range(len(ml)):
        if ml[i].find(con) != -1: return i
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

	len1 = len(MutatedTestResult)
	len2 = len(OriginalTestResult)

	pos1 = findstr(MutatedTestResult, UpdateString)
	if pos1 == -1:
		print "ERROR: Can not find UpdateString and NXT in MutatedTestResult!\n"
		return -1
	pcon = MutatedTestResult[pos1-1]
	pos2 = findstr(OriginalTestResult[pos1-2:], pcon)
	MutatedTestResult = mySplitR(MutatedTestResult[pos1:len1-2])
	OriginalTestResult = mySplitR(OriginalTestResult[pos1-2:][pos2+1:len2-2])


	if len(MutatedTestResult)!=len(OriginalTestResult):
		print "length not same!\n"
	if MutatedTestResult != OriginalTestResult:
		BugList.append([config, OriginalTestResultFile, MutatedTestResultFile])
	return 0



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
