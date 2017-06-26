#include <stdio.h>
#include <string>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <postgresql/libpq-fe.h>
#include <boost/variant.hpp>

typedef boost::variant<int, std::string> IntOrString;

class DatabaseConnect{
private:
	PGconn *conn;
	std::string host = "129.24.26.137";
	std::string password = "Cerculsihr4T";
	std::string databasename = "postgres";
	std::string username = "postgres";

public:
	int getTableNames();
	int readTable(std::string);
	int makeTable(std::string);
	int writeData(std::string, std::vector<int>);
	int connect();
	int disconnect();
	DatabaseConnect(std::string, std::string, std::string, std::string);
	DatabaseConnect();
};
