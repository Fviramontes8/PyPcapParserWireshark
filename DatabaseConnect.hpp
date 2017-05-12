#include <stdio.h>
#include <string>
#include <stdlib.h>
#include <iostream>
#include <postgresql/libpq-fe.h>

class DatabaseConnect{
private:
	PGconn *conn;
	std::string databasename;
	std::string username;
	std::string password;
	std::string host;

public:
	int writeData(/*list here*/);
	int connect();
	int disconnect();
	DatabaseConnect(std::string, std::string, std::string, std::string);
	DatabaseConnect();
};
