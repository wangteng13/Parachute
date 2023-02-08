# coding=utf-8

import os
import random

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 10
Software = 'Redis'

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
	UpdateString = ""

	if Software == 'MySQL':
		UpdateString = "#####@@ This is Inserted by TestMytater! @@#####\nset " 
		if str(Property) == str(0): UpdateString = UpdateString + "global "
		else: UpdateString = UpdateString + "session "
		UpdateString = UpdateString + ConfName + " = " + str(ConfValue) + ";"
	if Software == 'PostgreSQL':
		UpdateString = "-- #####@@ This is Inserted by TestMytater! @@#####\n"
		UpdateString = UpdateString + " UPDATE pg_settings SET setting = " +"'" +str(ConfValue)+"'" + " WHERE name = '"+ConfName+"';"
	if Software == 'Redis':
		UpdateString = "#####@@ This is Inserted by TestMytater! @@#####\n"
		UpdateString = UpdateString + "r config set " +ConfName + " " + str(ConfValue) + "\n"
		UpdateString = UpdateString + 'puts "OCTester is testing!"; \n'

	#print UpdateString
	return UpdateString

# check whether to insert an updateString just before the con stmt 
def checkCanInsert(con, Software):
	con = con.replace("\n","").replace("\r","")
	if Software == "MySQL":
		if len(con)>=2 and con[0]!='#' and con[0]!='\n' and con[0]!='\r':
			return True
	if Software == "PostgreSQL":
		if len(con)>=2 and con[0]!='#' and con[0]!='\n' and con[0]!='\r' and con[0]!='-' and con[0]!='\\':
			return True
	if Software == "Redis":
		while(True):
			flag = 0
			if len(con) > 1 and con[0] == ' ':
				con = con.replace(' ', '')
				flag = 1
			if len(con) > 1 and con[0] == '\t':
				con = con.replace('\t', '')
				flag = 1
			if flag == 0: break
		if len(con)>=2 and con[0]=='r':
			return True
	return False

# insert the UpdateString into TestContent at pos
# return the string
def insertAt(UpdateString, pos, TestContent):
	res = ""
	for i in range(len(TestContent)):
		res = res + TestContent[i] + "\n"
		if pos == i:
			res = res + UpdateString + "\n"
	return res

# remove the starting ' ' or '\t'
def getStart(con):
	while(True):
		flag = 0
		if len(con) >= 1 and con[0] == ' ':
			con = con.replace(' ', '',1)
			flag = 1
		if len(con) >= 1 and con[0] == '\t':
			con = con.replace('\t', '',1)
			flag = 1
		if flag == 0: break
	return con

def startwith(con, st):
	len1 = len(con)
	len2 = len(st)
	if len1 < len2: return False
	for i in range(len2):
		if con[i] != st[i]:
			return False
	return True

def findOkRange(TestContent):
	res = []
	flag = -1
	pre = ""
	for i in range(len(TestContent)):
		con = TestContent[i]
		if flag == -1:
			if startwith(getStart(con), "test ") == True:
				flag = i
				pre = con[:con.find("test ")]
		else:
			if startwith(con, pre) == True:
				nxt = getStart(con)
				if len(nxt) >= 1 and nxt[0] == '}':
					res.append((flag,i))
					flag = -1
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
	TestContent = TestContent.split('\n')

	# [(1,2), (3,5)]
	okRange = findOkRange(TestContent)
	print okRange

	result = []
	temp = []
	for i in range(0,len(TestContent)):
		if inOkRange(okRange, i) == False:
			continue
		con = TestContent[i]
		# can not insert stmt before these stmts
		#if i+1<len(TestContent) and TestContent[i+1].lower().find("show warnings")!=-1: continue
		#if i+1<len(TestContent) and TestContent[i+1].lower().find("show errors")!=-1: continue
		#if i+1<len(TestContent) and TestContent[i+1].lower().find("get diagnostics")!=-1: continue
		# select @@warning_count,@@error_count;
		# select row_count();
		# SELECT TRACE
		# GET CURRENT DIAGNOSTICS
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
# have not implenment now, and return True now
def isConfRelatedTest(config, TestSuit):
	return True

# TestSuit is like user.test
# return the name before '.test'
def modify(TestSuit):
	res = TestSuit.split('.')
	return res[0]

def makeUpdateStringList(config):
	print config
	res = []
	for i in range(len(config[2])):
		if i >= MuatetionNumForOneConfig: break
		UpdateString = createUpdateString(config[0], str(config[2][i]), config[1])
		res.append(UpdateString)
	return res
	#for i in range(MuatetionNumForOneConfig):
	#	UpdateString = createUpdateString(config[0], str(i), config[1])
	#	res.append(UpdateString)
	

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
		#if len(sp) <=2: continue
		res.append(sp)
	return res



#createNewTest('user_var-binlog.test', 'set global xx = ;')

def main():
	TestSuitList = readfile("./"+Software + "/TestSuitList.txt")
	TestSuitList = TestSuitList.replace("\r","").split('\n')
	ConfSpecList = readfile("./"+Software + "/ConfSpecList.txt")
	ConfSpecList = getConfSpecList(ConfSpecList)

	if os.path.exists("./" + Software + "/NewTestSuit/") == False: os.mkdir("./" + Software + "/NewTestSuit/")

	#ConfSpecList = [["server_id", 0, 0]]
	#TestSuitList = ["user_var-binlog.test", "show_check.test"]

	for config in ConfSpecList:
		for TestSuit in TestSuitList:
			if len(TestSuit) < 1: continue
			if isConfRelatedTest(config, TestSuit):
				for j in range(len(config[2])):
					if j >= MuatetionNumForOneConfig: break
					uv = config[2][j]
					UpdateString = createUpdateString(config[0], str(config[2][j]), config[1])
					NewTestList = createNewTest(TestSuit, UpdateString)

					configDir = "./" + Software + "/NewTestSuit/" + config[0]
					configTestDir = "./" + Software + "/NewTestSuit/" + config[0] + "/" + TestSuit.replace(".tcl","").replace("\r","")
					if os.path.exists("./" + Software + "/NewTestSuit/") == False: os.mkdir("./" + Software + "/NewTestSuit/")
					if os.path.exists(configDir) == False: os.mkdir(configDir)
					if os.path.exists(configTestDir) == False: os.mkdir(configTestDir)

					NewTestNum = 0
					for NewTest in NewTestList:
						writefile(NewTest, configTestDir + "/" + modify(TestSuit) + "_UpdateWith_" + str(config[2][j]) + "_mutated_" + str(NewTestNum) + ".tcl", "w")
						NewTestNum = NewTestNum + 1


main()




