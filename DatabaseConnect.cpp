/*
 * Author: Seth Decker
 * 
 * Description:
 * 
 */
#include "DatabaseConnect.hpp"

DatabaseConnect::DatabaseConnect()
{
	
}
DatabaseConnect::DatabaseConnect(std::string _databasename, std::string _host, std::string _username, std::string _password)
{
	databasename = _databasename;
	username = _username;
	password = _password;
	host = _host;
	
}

int DatabaseConnect::connect()
{
	std::string conninfo =  "dbname=" + databasename + " " + " host=" + host + " " + " user=" + username + " " + " password=" + password;
	std::cout << conninfo << std::endl;
	conn = PQconnectdb(conninfo.c_str());
	/* Check to see that the backend connection was successfully made */
    if (PQstatus(conn) != CONNECTION_OK)
    {
        fprintf(stderr, "Connection to database failed: %s",
                PQerrorMessage(conn));
    }
	return 0;
}

int DatabaseConnect::writeData(/*list here*/)
{
	/*loop and format data*/
	PQexec(conn, "INSERT INTO cplusplustest VALUES('burp2', 100000, 100000)");
	printf("%s\n", PQerrorMessage(conn));
	return 0;
}

int DatabaseConnect::disconnect()
{
	PQfinish(conn);
	
	return 0;
}
