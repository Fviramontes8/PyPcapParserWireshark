#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

#include "DatabaseConnect.hpp"

int main(int argc, char* argv[]) {
	std::ifstream ip_file, mac_file;
	std::stringstream dummy_string, dummy_string1;
	std::string IP_addr, MAC_addr;
	
	/**IP address**/
	ip_file.open("ip.txt");
	if(!ip_file) {
		std::cout << "IP file does not exist!" << std::endl;
		exit(1);
	}
	char IP[20];
	std::ifstream ip_in("ip.txt", std::ifstream::ate | std::ifstream::binary);
	//Size of the file
	//std::cout << ip_in.tellg() << std::endl;
	int ip_size = ip_in.tellg();
	
	if(ip_size > 18) {
		std::cout << "IP file is too large to read" << std::endl;
		ip_file.close();
		exit(1);
	}
	
	if(ip_file.is_open()) {
		ip_file >> IP;
		//std::cout << IP << std::endl;
	}
	ip_file.close();
	
	dummy_string << IP;
	dummy_string >> IP_addr;
	std::cout << "This is my IP address " << IP_addr << std::endl;
	
	/**MAC address**/
	mac_file.open("mac.txt");
	if(!mac_file) {
		std::cout << "MAC file does not exist!" << std::endl;
		exit(1);
	}
	char MAC[20]; //Max length 17
	std::ifstream mac_in("mac.txt", std::ifstream::ate | std::ifstream::binary);
	int mac_size = mac_in.tellg();
	
	if(mac_size > 18) {
		std::cout << "MAC file is too large to read" << std::endl;
		mac_file.close();
		exit(1);
	}
	if(mac_file.is_open()) {
		mac_file >> MAC;
		//std::cout << MAC << std::endl;
	}
	ip_file.close();
	
	dummy_string1 << MAC;
	dummy_string1 >> MAC_addr;
	std::cout << "This is my MAC address " << MAC_addr << std::endl;
	
	
	std::string table_name = "ip";
	std::vector<std::string> info_vector(2);
	info_vector[1] = IP_addr;
	info_vector[0] = MAC_addr;
	DatabaseConnect db("postgres", "129.24.26.75", "postgres", "Cerculsihr4T");
	db.connect();
	std::cout << "Connected to database and about ot call function" << std::endl;
	
	std::string sql_response = db.searchMAC(table_name, info_vector[0]);
	std::cout << sql_response << std::endl;
	/*
	int z = db.getNextKey(table_name);
	std::string keyString = std::to_string(z);
	db.writeIPData(table_name, keyString, info_vector);
	*/
	db.disconnect();
}
