# coding=utf-8

import os
import subprocess
import shutil
from shutil import move

MuatetionNumInOneTest = 20
MuatetionNumForOneConfig = 5
Software = 'Nginx'

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
			if i==0: 
				sp.append(tv)
				continue
			if Software == 'MySQL' and i==1: sp.append(tv)
			else: valuelist.append(tv)
		sp.append(valuelist)
		res.append(sp)
	return res


def recoverDefaultConfigFile():
	if Software == 'MySQL':
		MySQLConfigDir = "/usr/local/mysql/mysql-test/include/default_my.cnf"
		try:
			move(MySQLConfigDir+"_bak", MySQLConfigDir)
		except IOError:
			print "recoverDefaultConfigFile Error!", Software

	if Software == 'Nginx':
		NginxConfigDir = "/usr/local/nginx/nginx.conf"
		try:
			move(NginxConfigDir+"_bak", NginxConfigDir)
		except IOError:
			print "recoverDefaultConfigFile Error!", Software
	

def updateDefaultConfigFile(key, value):
	print "I am setting " + key + " into " + value
	if Software == 'MySQL':
		MySQLConfigDir = "/usr/local/mysql/mysql-test/include/default_my.cnf"
		flag = 0
		try:
			with open( MySQLConfigDir, 'r' ) as fp:
				lines = fp.readlines()
				for line in lines:
					if key in line and line[0] != "#":
						new_line = key + "=" + value + "\n"
						lines[lines.index( line )] = new_line
						flag = 1
						break
				if flag == 0: lines.append(str(key) + "=" + str(value) + "\n")

			with open( MySQLConfigDir+"_tmp", 'w' ) as fp:
				fp.writelines( lines )
			move(MySQLConfigDir, MySQLConfigDir+"_bak")
			move(MySQLConfigDir+"_tmp", MySQLConfigDir)
		except IOError:
			print "updateDefaultConfigFile Error!"

	if Software == 'Nginx':
		NginxConfigDir = "/usr/local/nginx/nginx.conf"
		try:
			with open( NginxConfigDir, 'r' ) as fp:
				lines = fp.readlines()
				lines.append("\n\n"+str(key) + " " + str(value) + "\n")

			with open( NginxConfigDir+"_tmp", 'w' ) as fp:
				fp.writelines( lines )
			move(NginxConfigDir, NginxConfigDir+"_bak")
			move(NginxConfigDir+"_tmp", NginxConfigDir)
		except IOError:
			print "updateDefaultConfigFile Error!"

def getResultDir(config, oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos >= 0:
		oneTest = oneTest[:pos]
	else:
		if Software == 'MySQL':
			oneTest = oneTest.replace(".test","")
		if Software == 'Nginx':
			oneTest = oneTest.replace(".t","")
	res = "./"+Software+ "/TestResult/" + config + "/" + oneTest + "/"
	return res

def getOriginalTestName(oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos == -1: 
		if Software == 'MySQL':
			return oneTest
		if Software == 'Nginx':
			return oneTest.replace(".t", "")

	if Software == 'MySQL':
		oneTest = oneTest[:pos] + ".test"
		return oneTest
	if Software == 'Nginx':
		oneTest = oneTest[:pos] + ".t"
		return oneTest

def excuteOneTestWithConfig(config, value, oneTestDir, oneTest):
	updateDefaultConfigFile(config, value)
	if Software == 'MySQL':
		OriginalTestName = getOriginalTestName(oneTest)
		TestToolDir = "/usr/local/mysql/mysql-test"
		CMD = "sudo mv " + TestToolDir + "/t/" + OriginalTestName + "  "+TestToolDir+"/t/" + OriginalTestName + "_bak  ; "
		CMD = CMD + "sudo cp " + oneTestDir + " " + TestToolDir  + "/t/" + OriginalTestName + "; "
		hahaTest = oneTest
		oneTest = OriginalTestName

		CMD = CMD + "cd " + TestToolDir + " ;"
		CMD = CMD + "./mysql-test-run.pl ./t/" + oneTest + " --record --testcase-timeout=5 --nocheck-testcases; "

		print CMD
		os.system(CMD)

		ResultDir = getResultDir(config, oneTest)
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)

		CMD = "pwd; sudo mv " + TestToolDir + "/r/" + oneTest.replace(".test", ".result") + " "+ ResultDir + oneTest.replace(".test", "_StartWith_"+str(value)+".result")
		os.system(CMD)
		CMD = "pwd; sudo mv " + TestToolDir + "/var/log/main." + oneTest.replace(".test", "")+"/" +oneTest.replace(".test", ".log")+ " "+ ResultDir + hahaTest.replace(".test", "_StartWith_"+str(value)+".result")
		os.system(CMD)
		if oneTest.find("mutated") > -1:
			CMD = "sudo rm " + TestToolDir + "/t/" + oneTest + ";"
			os.system(CMD)
		
		CMD = "sudo mv " + TestToolDir + "/t/" + OriginalTestName + "_bak "+TestToolDir+"/t/" + OriginalTestName
		os.system(CMD)

	if Software == 'Nginx':
		OriginalTestName = getOriginalTestName(oneTest) #xx.t
		TestToolDir = "/nginx-tests-master/"
		TestCaseDir = TestToolDir
		#test_helper.t

		CMD = "cp " + oneTestDir + " "  + TestCaseDir + OriginalTestName + "; "
		print CMD
		os.system(CMD)
		

		CMD = "cd " + TestToolDir + "; "
		CMD = CMD + "TEST_NGINX_BINARY=/usr/local/nginx/nginx prove ./" + OriginalTestName + "  -v  | tee oc.txt ; "
		print CMD
		os.system(CMD)

		ResultDir = getResultDir(config, oneTest)
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)
		CMD = "pwd; mv /nginx-tests-master/oc.txt " + "  "+ ResultDir + oneTest.replace(".t", "_StartWith_"+str(value)+".result")
		print CMD
		os.system(CMD)

	recoverDefaultConfigFile()

def getUpdate(filename):
	st = filename.replace("\r","")
	pos1 = st.find("UpdateWith_")
	pos2 = st.find("_mutated_")
	return st[pos1+len("UpdateWith_") : pos2]
	
def excute2():
	TestSuitList = readfile(Software + "/TestSuitList.txt")
	TestSuitList = TestSuitList.replace("\r","").split('\n')
	ConfSpecList = readfile(Software + "/ConfSpecList.txt")
	ConfSpecList = getConfSpecList(ConfSpecList)	

	for config in ConfSpecList:
		valuelist = config[len(config)-1]
		print valuelist
		ResultDir = "./" + Software + "/TestResult/" + config[0]
		if os.path.exists("./" + Software + "/TestResult/") == False: os.mkdir("./" + Software + "/TestResult/")
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)

		for onetest in TestSuitList:
			print onetest
			onetestname = onetest.replace(".t","")
			if len(onetest) < 2: continue
			oneTestPath = "./" + Software + "/TestSuit/" + onetest
			NewTestSuitDir = "./" + Software + "/NewTestSuit/" + config[0] + "/" + onetestname + "/"

			for value in valuelist:
				excuteOneTestWithConfig(config[0], value, oneTestPath, onetest)

				files = os.listdir(NewTestSuitDir)
			    	for file in files:
						UUpdate = getUpdate(file)
						if str(UUpdate) == str(value): continue
						file_path = os.path.join(NewTestSuitDir, file)
						if os.path.isfile(file_path):
					    		excuteOneTestWithConfig(config[0], value, file_path, file)


excute2()
