# Parachute: Detecting On-the-Fly Configuration Bugs

Parachute is a tool for detecting on-the-fly configuration bugs (**OCBugs**) in runtime configurable systems. Parachute first generates test cases of on-the-fly configuration updating for the target options. And then leverages metamorphic testing to detect OCBugs with two oracles (Internal Effects and External Effects).


The repository contains all the artifacts (including all the code and datasets) of the paper

- [Understanding and Detecting On-the-Fly Configuration Bugs](https://raw.githubusercontent.com/wangteng13/Parachute/main/paper/icse23-Parachute.pdf)  
Teng Wang, Zhouyang Jia, Shanshan Li, Si Zheng, Yue Yu, Erci Xu, Shaoliang Peng, Xiangke Liao.  
Proceedings of the 45th International Conference on Software Engineering (ICSE) May 2023.   
(**Distinguished Paper Award**)

---

## Public Dataset

The OCBug data set can be accessed by [HERE](https://github.com/ocbug/Parachute/tree/main/dataset)

The information of 75 OCBugs studied in this paper. The bugs are from 5 open-source projects (MySQL, Redis, PostgreSQL, Nginx and Squid). All the data sheets are in the format of CSV, with titles/labels as the first rows.

---

## How to use Parachute:

### Setp 1:
First, conduct taint analysis for the target configuration option, and instrument the target program.

The taint analysis tool is dependent on llvm-10.0.0

Build the taint analysis tool before conducting it.

It is suggested to build the bitcode of target program with wllvm or gllvm.

```
cd ./ConfigTainter
cmake -DCMAKE_CXX_COMPILER=/usr/bin/clang++-10 -DCMAKE_C_COMPILER=/usr/bin/clang-10 -DLLVM_DIR=/usr/lib/llvm-10/cmake . 
make


./ConfigTainter/tainter MySQL.bc MySQL-var.txt
```

### Setp 2:

Build the instrumentation tool before testing. 

The instrumentation tool is dependent on clang-10.0.0

Edit ./Instrumentation/CMakeLists.txt fisrt.

```
cd ./Instrumentation
cmake .
make

./Instrumentation/instrumentation -software MySQL ./TaintedResult/MySQL-records.dat -p compile_commands.json
```
### Setp 3:

Then, sample configuration option values with option_list_example.json.

option_list_example.json lists the target option and its constraints.

```
python ConfigSampler.py MySQL ./option_list_example.json
```

### Setp 4:

After that, generate on-the-fly configuration tests for the target options.

Please prepare TestSuitList.txt before this step, which lists the test suits to use.

```
python TestMutater.py MySQL
```

### Setp 5:

Then, execute the original tests and mutated tests.

Finally, analyze results and report alarms.

```
python TestExcutor.py MySQL
python TestResultChecker.py MySQL
```
