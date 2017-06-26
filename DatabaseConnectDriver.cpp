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
	std::string hostname = "129.24.26.137";
	std::string username = "postgres";
	std::string password = "Cerculsihr4T";

	//std::cout << hostname << std::endl;
	DatabaseConnect db(dbname, hostname, username, password);
	//DatabaseConnect db(); <- is the general function
	db.connect();

	db.writeData();
	
	db.disconnect();
}
