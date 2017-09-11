/***********************************************************************
 * Author: Seth Decker, Francisco Viramontes
 * 
 * Description: This program is intended to  act as a front to 
 * comunicate with an sql database via c++ code. Inputs vary and
 * the user should see each function for their inputs and outputs.
 * 
 **********************************************************************/
#include "DatabaseConnect.hpp"
#include <string>
#include <vector>

/*/Initializes variables to connect to PostgreSQL database
DatabaseConnect::DatabaseConnect()
{
	databasename = "postgres";
	username = "postgres";
	password = "Cerculsihr4T";
	host = "129.24.26.137";
	
}*/

//Function to save variables to log on to the database
DatabaseConnect::DatabaseConnect(std::string _databasename, std::string _host, std::string _username, std::string _password)
{
	databasename = _databasename;
	username = _username;
	password = _password;
	host = _host;
	
}

//Function to log on to the database and then to check the integrity of the connection
int DatabaseConnect::connect()
{
	std::string conninfo =  "dbname=" + databasename + " " + " host=" + host + " " + " user=" + username + " " + " password=" + password;
	
	conn = PQconnectdb(conninfo.c_str());
	
	//Checks to see that the backend connection was successfully made
	if(PQstatus(conn) == CONNECTION_OK) {
		std::cout << "Connected to database!" << std::endl;
	}
    else if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Connection to database failed: %s",
                PQerrorMessage(conn));
    }
	return 0;
}

int DatabaseConnect::deleteTableContent(std::string v) {
	std::string u = "DELETE FROM " + v;
	PQexec(conn, u.c_str());
	return 0;
}


/*Given a string input this function will make a table under the name of
 * the input string. It will have these columns (all integers):
 * 
 * Key
 * Timestamp
 * Number of Users
 * Bits
 * Number of Packets
 * Average signal strength
 * Average data rate
 * Percentage of 802.11b packets
 * Percentage of 802.11g packets
 * Percentage of 802.11n packets
 * 
 * Return a print statement saying that the table was made.
 */
int DatabaseConnect::makeTable(std::string s) {
	std::string k = "Create Table "+ s +"(Key int PRIMARY KEY, ts int, NoU int, bits int, pkt_num int, sigS int, dR int, phyb int, phyg int, phyn int)";
	PQexec(conn, k.c_str());
	std::cout << "Made table: " << s << std::endl;
	return 0;
}

/*These two lines grab the highest key from the database (if it is 
	 * empty, 0) then adds one so that we can add more data to the 
	 * database.
	 */
int DatabaseConnect::getNextKey(std::string s) {
	std::string query = "select * from " + s;
	int k = PQntuples(PQexec(conn, query.c_str())) + 1;
	return k;
}

/*This function takes a string and a vector of 9 "int" elements 
 * (converted to strings) as an input and writes the data from the
 * vector to a database of name of the string given. If there is there
 * is any data in the database beforehand, it will add to the database
 * without overriding the data that was there before.
 */
int DatabaseConnect::writeData(std::string s, std::string k, std::vector<std::string> p)
{ 
	//String to write to database in sql syntax
	std::string y = "INSERT INTO "+ s +" (Key, ts, NoU, bits, pkt_num, sigS, dR, phyb, phyg, phyn) VALUES('"+ k +"', '"+ p[0] +"', '"+ p[1] +"', '"+ p[2] +"', '"+ p[3] +"', '"+ p[4] +"', '"+ p[5] +"', '"+ p[6] +"', '"+ p[7] +"', '"+ p[8] +"')";
	
	//Executes command to write to database
	PQexec(conn, y.c_str());
	
	//To avoid memory leakage
	PQclear(PQexec(conn, y.c_str()));
	return 0;
}

//Disconnects from database
int DatabaseConnect::disconnect() {
	PQfinish(conn);
	std::cout << "Disconnected" << std::endl;
	
	return 0;
}
