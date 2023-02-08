#include "tainter.h"


const int vertif = 0x1234abcd; 
string filePath = "gepData";	


int saveData(vector< pair < pair < Type *, vector<int> >, Value* > > & Data){

	ofstream ofile(filePath.c_str(), ios::binary);
	if(ofile.is_open()==false){
		cout<<"Open file fail!"<<endl;
		exit(1);
	}
	ofile.write((char*)&vertif, sizeof(int));

	int length = Data.size();
	ofile.write((char*)&length, sizeof(int)); 
     
    for(vector<pair<pair<Type* , vector<int>>, Value* >>::iterator it = Data.begin(); it!=Data.end(); it++)    {    

        // Type
        ofile.write((char*)&(*(it->first.first)), sizeof(Type));

        // lenght of `vector<int>`
        int l = it->first.second.size();
        ofile.write((char*)&l, sizeof(int)); 

        // vector<int>
        for(vector<int>::iterator it2 = it->first.second.begin(); it2!=it->first.second.end(); it2++){
            ofile.write((char*)&(*it2), sizeof(int));
        }

        // Value
        ofile.write((char*)&(*(it->second)), sizeof(Value));              
    }

	ofile.write((char*)&vertif, sizeof(int));
	
	ofile.close();
    llvm::outs() << "SAVED.\n";
	return 0;
} 


vector< pair < pair < Type*, vector<int> >, Value*> > restore(){
	ifstream ifile(filePath.c_str(), ios::binary);
	int tmpVertif, length, totalSize;

	ifile.read((char*)&tmpVertif, sizeof(int));
	if (tmpVertif!=vertif){
		cout<<"Unknow format at the begin of file..."<<endl;
		exit(1);
	} else {
        cout<<"Restore verify OK. [START]"<<endl;
    }

	ifile.read((char*)&length, sizeof(int));

	vector< pair < pair < Type*, vector<int> >, Value*> > Data;	

    for(int i=0; i<length; i++){    

        // Type
        Type* t = (Type*) malloc(sizeof(Type));
        ifile.read((char*)&(*t), sizeof(Type));

        // lenght of `vector<int>`
        int l;
        ifile.read((char*)&l, sizeof(int)); 

        // vector<int>
        vector<int> vec(l);
        for(int j=0; j<l; j++){
            ifile.read((char*)&(vec[j]), sizeof(int));
        }

        // Value
        Value* v = (Value*) malloc(sizeof(Value));
        ifile.read((char*)&(*v),   sizeof(Value));

        pair < Type*, vector<int> > pp(t, vec);
        pair < pair < Type*, vector<int> >, Value*> p(pp, v);
        Data.push_back(p);
    }

	ifile.read((char*)&tmpVertif, sizeof(int));	
    if (tmpVertif!=vertif){
		cout<<"Unknow format at the end of file..."<<endl;
		exit(1);
	} else {
        cout<<"Restore verify OK. [END]"<<endl;
    }

    for(vector< pair < pair < Type*, vector<int> >, Value*> >::iterator it = Data.begin(); it!=Data.end(); it++)    {    

        for(vector<int>::iterator it2 = it->first.second.begin(); it2!=it->first.second.end(); it2++)
            llvm::outs() << ", " << *it2;
        //llvm::outs() << "\n";
    }

	return Data;
} 
