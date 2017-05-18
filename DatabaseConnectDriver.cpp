/*
 * Author: Seth Decker
 * 
 * Description: 
 * 
 */
#include <iostream>
#include <string>
#include "DatabaseConnect.hpp"



int main() {
	std::string dbname = "postgres";
	std::string hostname = "129.24.26.136";
	std::string username = "postgres";
	std::string password = "postgresUNM";

	//std::cout << hostname << std::endl;
	DatabaseConnect db(dbname, hostname, username, password);
	//DatabaseConnect db();
	std::cout << "hello\n";
	db.connect();
	//db.writeData();
	
	//db.disconnect();
}
