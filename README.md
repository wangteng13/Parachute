# Understanding and Detecting On-the-Fly Configuration Bugs

The repository includes the following artifacts:

```OCBug dataset``` : The information of 75 OCBugs studied in this paper. The bugs are from 5 open-source projects (MySQL, Redis, PostgreSQL, Nginx and Squid). All the data sheets are in the format of CSV, with titles/labels as the first rows.

```Code``` : The source code of Parachute to detect OCBugs.

```Evaluation``` : The evaluation results of Parachute.

## Public Dataset

The OCBug data set can be accessed by [HERE](https://github.com/ocbug/Parachute/tree/main/dataset)

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
