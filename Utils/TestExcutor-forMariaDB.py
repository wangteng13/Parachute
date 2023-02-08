# coding=utf-8

import os
import subprocess
import shutil
from shutil import move

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 5
Software = 'MariaDB'

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
			if i==0 or i==1: sp.append(tv)
			else: valuelist.append(tv)
		sp.append(valuelist)
		if len(sp) <=2: continue
		res.append(sp)
	return res

def recoverDefaultConfigFile():
	if Software == 'MariaDB':
		MariaDBConfigDir = "/usr/local/mysql/mysql-test/include/default_my.cnf"
		try:
			move(MariaDBConfigDir+"_bak", MariaDBConfigDir)
		except IOError:
			print "recoverDefaultConfigFile Error!"

def updateDefaultConfigFile(key, value):
	print "I am setting " + key + " into " + value
	if Software == 'MariaDB':
		MariaDBConfigDir = "/usr/local/mysql/mysql-test/include/default_my.cnf"
		flag = 0
		try:
			with open( MariaDBConfigDir, 'r' ) as fp:
				lines = fp.readlines()
				for line in lines:
					if key in line and line[0] != "#":
						new_line = key + "=" + value + "\n"
						lines[lines.index( line )] = new_line
						flag = 1
						break
				if flag == 0: lines.append(str(key) + "=" + str(value) + "\n")
				#print lines

			with open( MariaDBConfigDir+"_tmp", 'w' ) as fp:
				fp.writelines( lines )
			move(MariaDBConfigDir, MariaDBConfigDir+"_bak")
			move(MariaDBConfigDir+"_tmp", MariaDBConfigDir)
		except IOError:
			print "updateDefaultConfigFile Error!"

def getResultDir(config, oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos >= 0:
		oneTest = oneTest[:pos]
	else:
		oneTest = oneTest.replace(".test","")
	res = "./"+Software+ "/TestResult/" + config + "/" + oneTest + "/"
	return res

def getOriginalTestName(oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos == -1: return oneTest
	oneTest = oneTest[:pos] + ".test"
	return oneTest

def excuteOneTestWithConfig(config, value, oneTestDir, oneTest):
	updateDefaultConfigFile(config, value)
	if Software == 'MariaDB':
		OriginalTestName = getOriginalTestName(oneTest)
		TestToolDir = "/usr/local/mysql/mysql-test"
		#CMD = "sudo cp " + oneTestDir + " " + TestToolDir + "/t/ ;" 
		CMD = "sudo mv " + TestToolDir + "/main/" + OriginalTestName + "  "+TestToolDir+"/main/" + OriginalTestName + "_bak  ; "
		CMD = CMD + "sudo cp " + oneTestDir + " " + TestToolDir  + "/main/" + OriginalTestName + "; "
		hahaTest = oneTest
		oneTest = OriginalTestName

		CMD = CMD + "sudo rm " + TestToolDir + "/main/" + oneTest.replace(".test", ".result") + " ; "
		os.system(CMD)

		CMD = CMD + "cd " + TestToolDir + " ;"
		CMD = CMD + "./mysql-test-run ./main/" + oneTest + " --record --testcase-timeout=5 --nocheck-testcases; "

		print CMD
		os.system(CMD)

		ResultDir = getResultDir(config, oneTest)
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)

		CMD = "pwd; sudo mv " + TestToolDir + "/main/" + oneTest.replace(".test", ".result") + " "+ ResultDir + hahaTest.replace(".test", "_StartWith_"+str(value)+".result")
		os.system(CMD)
		CMD = "pwd; sudo mv " + TestToolDir + "/var/log/" + oneTest.replace(".test", ".log")+ " "+ ResultDir + hahaTest.replace(".test", "_StartWith_"+str(value)+".result")
		os.system(CMD)
		if oneTest.find("mutated") > -1:
			CMD = "sudo rm " + TestToolDir + "/main/" + oneTest + ";"
			os.system(CMD)
		
		CMD = "sudo mv " + TestToolDir + "/main/" + OriginalTestName + "_bak "+TestToolDir+"/main/" + OriginalTestName
		os.system(CMD)

		#new add
		CMD = "sudo mv " + TestToolDir + "/var/log/mysqld.1.err" + " " + ResultDir + hahaTest.replace(".test", "_StartWith_"+str(value)+".log")
		print CMD
		os.system(CMD)
	recoverDefaultConfigFile()

def RunTestWithNoUpdate(config, value, TestSuitList):
	for oneTest in TestSuitList:
		if len(oneTest) < 1: continue
		oneTestDir = "./" + Software + "/TestSuit/" + oneTest
		excuteOneTestWithConfig(config, value, oneTestDir, oneTest)

def RunTestWithNewTest(config, value):
	NewTestSuitDir = "./" + Software + "/NewTestSuit/" + config
	files = os.listdir(NewTestSuitDir)
    	for file in files:
        	file_path = os.path.join(NewTestSuitDir, file)
        	if os.path.isfile(file_path):
            		excuteOneTestWithConfig(config, value, file_path, file)

def excuteTest():
	TestSuitList = readfile(Software + "/TestSuitList.txt")
	TestSuitList = TestSuitList.replace("\r","").split('\n')
	ConfSpecList = readfile(Software + "/ConfSpecList.txt")
	ConfSpecList = getConfSpecList(ConfSpecList)

	for config in ConfSpecList:
		valuelist = config[2]
		print valuelist
		ResultDir = "./" + Software + "/TestResult/" + config[0]
		if os.path.exists("./" + Software + "/TestResult/") == False: os.mkdir("./" + Software + "/TestResult/")
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)

		for value in valuelist:
			RunTestWithNoUpdate(config[0], value, TestSuitList)

		for value in valuelist:
			RunTestWithNewTest(config[0], value)

def getUpdate(filename):
	st = filename.replace("\r","")
	pos1 = st.find("UpdateWith_")
	pos2 = st.find("_mutated_")
	return st[pos1+len("UpdateWith_") : pos2]
	
# new added
def chazhuang(config):
	#TaintedFile = readfile(Software + "/TaintedResult/" + config + "-records.dat")
	TaintedFile = Software + "/TaintedResult/" + config + "-records.dat"
	CompileFile = "/root/mariadb-10.9.1/compile_commands.json"
	CMD = " /root/chazhuang/chazhuang " + TaintedFile + " -p " + CompileFile + " ; "
	print CMD
	os.system(CMD)

	#mv out.c.tmp to out.c
	OutList = readfile("./out.txt")
	OutList = OutList.replace("\r","").split('\n')
	for item in OutList:
		if len(item) <= 2: continue
		CMD = "mv " + item + " " + item+".bak ;"
		os.system(CMD)
		CMD = "mv " + item+".tmp" + " " + item + " ; "
		os.system(CMD)

	#rebuild the software
	CMD = "cd /root/mariadb-10.9.1; make ; make install ;"
	os.system(CMD)

def unchazhuang():
	#mv out.c.bak to out.c
	OutList = readfile("./out.txt")
	OutList = OutList.replace("\r","").split('\n')
	for item in OutList:
		if len(item) <= 2: continue
		CMD = "mv " + item+".bak" + " " + item + " ;"
		os.system(CMD)

def excute2():
	TestSuitList = readfile(Software + "/TestSuitList.txt")
	TestSuitList = TestSuitList.replace("\r","").split('\n')
	ConfSpecList = readfile(Software + "/ConfSpecList.txt")
	ConfSpecList = getConfSpecList(ConfSpecList)	

	for config in ConfSpecList:
		valuelist = config[2]
		print valuelist
		ResultDir = "./" + Software + "/TestResult/" + config[0]
		if os.path.exists("./" + Software + "/TestResult/") == False: os.mkdir("./" + Software + "/TestResult/")
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)

		chazhuang(config[0])
		for onetest in TestSuitList:
			print onetest
			onetestname = onetest.replace(".test","")
			if len(onetest) < 2: continue
			oneTestPath = "./" + Software + "/TestSuit/" + onetest
			NewTestSuitDir = "./" + Software + "/NewTestSuit/" + config[0] + "/" + onetestname + "/"

			for value in valuelist:
				print "excuteOneTestWithConfig(config[0], value, oneTestPath, onetest)"
				#excuteOneTestWithConfig(config[0], value, oneTestPath, onetest)

				files = os.listdir(NewTestSuitDir)
			    	for file in files:
						UUpdate = getUpdate(file)
						if str(UUpdate) == str(value): continue
						file_path = os.path.join(NewTestSuitDir, file)
						if os.path.isfile(file_path):
							print "excuteOneTestWithConfig(config[0], value, file_path, file)"
					    	#excuteOneTestWithConfig(config[0], value, file_path, file)
		unchazhuang()


excute2()
