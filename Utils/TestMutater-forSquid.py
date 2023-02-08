# coding=utf-8

import os
import random

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 5
Software = 'Squid'

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

def createUpdateString(ConfName, ConfValue, Property):
	UpdateString = "#####@@ This is Inserted by TestMytater! @@#####\nset " 

	if Software == 'MySQL':
		if str(Property) == str(0): UpdateString = UpdateString + "global "
		else: UpdateString = UpdateString + "session "
		UpdateString = UpdateString + ConfName + " = " + str(ConfValue) + ";"
	if Software == 'Squid':
		SquidConfigDir = "/etc/squid/squid.conf"

		UpdateString = "#####@@ This is Inserted by TestMytater! @@#####\n"
		UpdateString = UpdateString + "system(\"python /root/workspace/UpdateConfile.py " + SquidConfigDir + " "+str(ConfName) + " "+str(ConfValue) + " \"); \n"
		UpdateString = UpdateString + "system(\"/usr/sbin/squid -k reconfigure\"); \n"
		UpdateString = UpdateString + 'print "OCTester is testing!\\n";\n'

	return UpdateString

# check whether to insert an updateString just before the con stmt 
def checkCanInsert(con, Software):
	con = con.replace("\n","").replace("\r","")
	if Software == "MySQL":
		if len(con)>=2 and con[0]!='#' and con[0]!='\n' and con[0]!='\r':
			return True
	if Software == "Squid":
		if len(con)>=2 and con[0]!='#' and con[0]!='\n' and con[0]!='\r':
			return True
	return False

# insert the UpdateString into TestContent at pos
# return the string
def insertAt(UpdateString, pos, TestContent):
	res = ""
	for i in range(len(TestContent)):
		res = res + TestContent[i] + ";\n"
		if pos == i:
			res = res + UpdateString + "\n"
	return res


def findOkRange(TestContent):
	res = []
	flag = -1
	st = 0
	for i in range(len(TestContent)):
		con = TestContent[i]
		if flag == -1:
			if con.find("plan test")!=-1:
				flag == 1
				res.append((i, len(TestContent)-1))
	return res

def inOkRange(okRange, i):
	for ran in okRange:
		if ran[0]<=i and i<=ran[1]:
			return True
	return False

# create newTest with the UpdateString
# insert times are limited by MuatetionNumInOneTest
def createNewTest(OriginalTest, UpdateString):
	TestContent = readfile("./"+Software + "/TestSuit/" + OriginalTest)
	TestContent = TestContent.split(';\n')

	okRange = findOkRange(TestContent)
	print okRange

	result = []
	temp = []
	for i in range(0,len(TestContent)):
		if inOkRange(okRange, i) == False:
			continue
		con = TestContent[i]
		if checkCanInsert(con, Software):
			temp.append(i)

	if len(temp) <= MuatetionNumInOneTest:
		for i in range(len(temp)):
			result.append(insertAt(UpdateString, temp[i], TestContent))
	else:
		step = len(temp)/MuatetionNumInOneTest
		st = 0
		end = step
		for i in range(MuatetionNumInOneTest):
			pos = random.randint(st, end)
			if pos >= len(temp): break
			result.append(insertAt(UpdateString, temp[pos], TestContent))
			st = st + step
			end = end + step

	return result
	
# check whether the Test is related with configA
def isConfRelatedTest(config, TestSuit):
	return True

# TestSuit is like user.t
# return the name before '.t'
def modify(TestSuit):
	res = TestSuit.split('.')
	return res[0]

def makeUpdateStringList(config):
	print config
	res = []
	for i in range(len(config[2])):
		if i >= MuatetionNumForOneConfig: break;
		UpdateString = createUpdateString(config[0], str(config[2][i]), config[1])
		res.append(UpdateString)
	return res
	

# read the ConfSpecListfile content, and get speclist
# [confname, Property, v1, v2, v3]
def getConfSpecList(ConfSpecList):
	res = []
	ConfSpecList = ConfSpecList.split('\n')
	for spec in ConfSpecList:
		sp = []
		valuelist = []
		temp = spec.split(',')
		for i in range(len(temp)):
			tv = temp[i]
			tv = tv.replace(' ', '')
                        tv = tv.replace("'",'')
                        tv = tv.replace("'",'')
			if i==0: 
				sp.append(tv)
				sp.append(1)
				continue
			if Software == 'MySQL' and i==1: sp.append(tv)
			else: valuelist.append(tv)
		sp.append(valuelist)
		res.append(sp)
	return res


def main():
	TestSuitList = readfile("./"+Software + "/TestSuitList.txt")
	TestSuitList = TestSuitList.replace("\r","").split('\n')
	ConfSpecList = readfile("./"+Software + "/ConfSpecList.txt")
	ConfSpecList = getConfSpecList(ConfSpecList)

	if os.path.exists("./" + Software + "/NewTestSuit/") == False: os.mkdir("./" + Software + "/NewTestSuit/")


	for config in ConfSpecList:
		for TestSuit in TestSuitList:
			if len(TestSuit) < 1: continue
			if isConfRelatedTest(config, TestSuit):
				UpdateStringList = makeUpdateStringList(config)
				for j in range(len(config[2])):
					if j >= MuatetionNumForOneConfig: break
					uv = config[2][j]
					UpdateString = createUpdateString(config[0], str(config[2][j]), config[1])
					NewTestList = createNewTest(TestSuit, UpdateString)

					configDir = "./" + Software + "/NewTestSuit/" + config[0]
					configTestDir = "./" + Software + "/NewTestSuit/" + config[0] + "/" + TestSuit.replace(".t","").replace("\r","")
					if os.path.exists("./" + Software + "/NewTestSuit/") == False: os.mkdir("./" + Software + "/NewTestSuit/")
					if os.path.exists(configDir) == False: os.mkdir(configDir)
					if os.path.exists(configTestDir) == False: os.mkdir(configTestDir)

					NewTestNum = 0
					for NewTest in NewTestList:
						writefile(NewTest, configTestDir + "/" + modify(TestSuit) + "_UpdateWith_" + str(config[2][j]) + "_mutated_" + str(NewTestNum) + ".t", "w")
						NewTestNum = NewTestNum + 1


main()




