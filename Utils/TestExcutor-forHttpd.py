# coding=utf-8

import os
import subprocess
import shutil
from shutil import move

MuatetionNumInOneTest = 5
MuatetionNumForOneConfig = 10
Software = 'Httpd'

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

	if Software == 'Httpd':
		HttpdConfigDir = "/mod_perl-2.0.12/t/conf/httpd.conf"
		try:
			move(HttpdConfigDir+"_bak", HttpdConfigDir)
		except IOError:
			print "recoverDefaultConfigFile Error!", Software
	
def replacewith(lines, key, value):
	res = []
	flag = 0
	for line in lines:
		if line.find( str(key) ) != -1 and flag == 0:
			ss = str(key) + " " + str(value) + "\n"
			res.append(ss)
			flag = 1
		else:
			res.append(line)
	return res

def updateDefaultConfigFile(key, value):
	print "I am setting " + key + " into " + value

	if Software == 'Httpd':
		HttpdConfigDir = "/mod_perl-2.0.12/t/conf/httpd.conf"
		try:
			with open( HttpdConfigDir, 'r' ) as fp:
				lines = fp.readlines()
				lines = replacewith(lines, key, value)

			with open( HttpdConfigDir+"_tmp", 'w' ) as fp:
				fp.writelines( lines )
			move(HttpdConfigDir, HttpdConfigDir+"_bak")
			move(HttpdConfigDir+"_tmp", HttpdConfigDir)
		except IOError:
			print "updateDefaultConfigFile Error!"

def getResultDir(config, oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos >= 0:
		oneTest = oneTest[:pos]
	else:
		if Software == 'MySQL':
			oneTest = oneTest.replace(".test","")
		if Software == 'Httpd':
			oneTest = oneTest.replace(".t","")
	res = "./"+Software+ "/TestResult/" + config + "/" + oneTest + "/"
	return res

def getOriginalTestName(oneTest):
	pos = oneTest.find("_UpdateWith_")
	if pos == -1: 
		if Software == 'MySQL':
			return oneTest
		if Software == 'Httpd':
			return oneTest

	if Software == 'MySQL':
		oneTest = oneTest[:pos] + ".test"
		return oneTest
	if Software == 'Httpd':
		oneTest = oneTest[:pos] + ".t"
		return oneTest

def excuteOneTestWithConfig(config, value, oneTestDir, oneTest):
	updateDefaultConfigFile(config, value)
	
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

	if Software == 'Httpd':
		OriginalTestName = getOriginalTestName(oneTest)
		TestToolDir = "/mod_perl-2.0.12/t/"
		TestCaseDir = TestToolDir

		CMD = "cp " + oneTestDir + " "  + TestCaseDir + OriginalTestName + "; "
		print CMD
		os.system(CMD)
		

		CMD = "cd " + TestToolDir + " ; "
		CMD = CMD + "./TEST " + OriginalTestName + "  -verbose  | tee oc.txt ; "
		print CMD
		os.system(CMD)

		ResultDir = getResultDir(config, oneTest)
		if os.path.exists(ResultDir) == False: os.mkdir(ResultDir)
		CMD = "pwd; mv /mod_perl-2.0.12/t/oc.txt " + "  "+ ResultDir + oneTest.replace(".t", "_StartWith_"+str(value)+".result")
		print CMD
		os.system(CMD)

		CMD = "rm " + TestCaseDir + OriginalTestName + "; "
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
