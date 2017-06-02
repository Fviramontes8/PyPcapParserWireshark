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
	//std::cout << conninfo << std::endl;
	std::cout << "You have connected to the database" << std::endl;
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
	/*******************************************************************
	 * This is the type of data that is planned to be inserted:
	 * Key(int)
	 * Timestamp(int)
	 * MAC src(string)[17]
	 * MAC dst(string)[17]
	 * IP src(string)[15]
	 * IP dst(string)[15]
	 * Bits from A -> B(int)
	 * Avg Signal Strengh(int)
	 * Avg Data Rate(int)
	 * Frequency used(int)
	 * # of 802.11b pkts(int)
	 * # of 802.11g pkts(int)
	 * # of 802.11n pkts(int)
	 ******************************************************************/
	PQexec(conn, "CREATE TABLE cpp_yo(user_id serial PRIMARY KEY, num int, data varchar(20));");
	//PQexec(conn, "INSERT INTO cp_yo VALUES('burp2', 100000, 100000)");
	printf("%s\n", PQerrorMessage(conn));
	return 0;
}

int DatabaseConnect::disconnect()
{
	std::cout << "Disconnecting..." << std::endl;
	PQfinish(conn);
	std::cout << "Disconnected" << std::endl;
	
	return 0;
}
