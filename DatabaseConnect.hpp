#include <stdio.h>
#include <string>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <postgresql/libpq-fe.h>

class DatabaseConnect{
private:
	PGconn *conn;
	std::string host = "129.24.26.137";
	std::string password = "Cerculsihr4T";
	std::string databasename = "postgres";
	std::string username = "postgres";

public:
	int getNextKey(std::string);
	int deleteTableContent(std::string);
	int getTableNames();
	int readTable(std::string);
	int makeTable(std::string);
	int writeData(std::string, std::string, std::vector<std::string>);
	int connect();
	int disconnect();
	DatabaseConnect(std::string, std::string, std::string, std::string);
	DatabaseConnect();
};
