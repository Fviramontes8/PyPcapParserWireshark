/**
 * Author: Francisco Viramontes
 * 
 * Description: TBD
 * 
 * TO COMPILE: g++ parser5.cpp DatabaseConnect.cpp -ltins -lboost_system -lboost_filesystem -lpq -o *executable_name*
 * TO CAPTURE DATA: tshark -i <<WiFi Interface>> -I -a duration:60 -b duration:1 -w data.pcap
 * *!*!*!*!*!*!*MAKE SURE YOUR WIRELESS INTERFACE IS IN MONITOR MODE*!*!*!*!*!*!*!*!
 */
#include <iostream>
#include <tins/tins.h> //For use of the pcap parser
#include <bitset>
#include <stddef.h>
#include <string> // For use of std::string
#include <vector> // For use of std::vector
#include <boost/filesystem.hpp> //To read multiple pcap files in a folder
#include "DatabaseConnect.hpp" //From local file to talk to postgresql database
#include <algorithm> //For searching for unique MAC addresses using std::find()

using namespace Tins;

int main(int argc, char* argv[]) {
	//Opening connection with database
	DatabaseConnect db("postgres", "129.24.26.75", "postgres", "Cerculsihr4T");
	db.connect();
	
	//Declaring table name to write to
	std::string table_name = "sun";
	
	//Getting the most recent key from database table
	int z = db.getNextKey(table_name);
	
	//Creating a local cache of recent files parsed so that we don't re-parse a pcap file
	std::vector<std::string> recentFiles;
	
	//If the parser waits for too long we want to set an exit condition
	int wait_count = 0;
	
	//Flag to break out of main loop and end the parser
	int loopbreak = 1;
	int breakout = 0;
	
	//The string path is to go to the selected path to parse pcap files
	/******************************************************************/
	const std::string path("/root/Pkt_data/sun/");
	/******************************************************************/
	
	//Iterator to iterate throught the chosen path above
	boost::filesystem::directory_iterator end_itr;
	
	//Wait 0.1 seconds to let tshark start producing pcap files
	usleep(100000);
	
	while(loopbreak) {
		//std::cout << "Is this a loop?" << std::endl;
		for(boost::filesystem::directory_iterator i(path); i != end_itr; i++) {
			//Counting the number of packets that have been parsed
			int pktCount;
			
			//Timestamp to keep track of what time pcap files are read
			int ts;
			
			/* Vector of integers that keeps track of these characteristics:
			 * Timestamp, Number of Unique Users, Total Bits sent,
			 * Number of Packets sent, Average Signal Strength, Average 
			 * Data Rate, Bits of 802.11
			 */
			std::vector<int> statVect = {0,0,0,0,0,0,0,0,0};
			
			//Vector for determining unique MAC addresses
			std::vector<std::string> uniqueMAC;
			
			//Checks if directory exists
			if(!boost::filesystem::is_regular_file(i->status())) {
				continue;
			}
			
			//Looks for pcap files in directory
			if(i->path().extension() == ".pcap") {
				int fileCheck = 0;
				for(auto& t : recentFiles) {
					//If file is new file check is flipped to 1 and is parsed
					if(t == i->path().string()) {
						fileCheck = 1;
					}
				}
				//std::cout << fileCheck << std::endl;
				if(breakout == 6) {
					//This means that the parser has waited long enough
					// and will end
					loopbreak = 0;
					db.disconnect();
				}
				else if(fileCheck != 0) {
					std::cout << "Waiting..." << std::endl;
					//Waiting 0.9 seconds
					usleep(900000);
					//fileCheck is flipped to 0 because no more unique files
					fileCheck = 0;
					//If breakout reaches 6 the parser will end
					breakout++;
				}
				else {
					if(recentFiles.size() > 8) {
						//Adds file name to list of files so it is not parsed again
						recentFiles.erase(recentFiles.begin());
						recentFiles.push_back(i->path().string());
					}
					else  {
						recentFiles.push_back(i->path().string());
					}
					//We take the pcap from the directory of chosing and begin parsing
					FileSniffer sniffer(i->path().string());
					breakout = 0;
					pktCount = 1;
					
					//While packets can be parsed
					while(Packet pkt = sniffer.next_packet()) {
						//Initializing packet object
						const PDU &pdu = *pkt.pdu();
						
						//Declaration of important variables
						std::string M_src = "None"; //Source MAC address
						std::string M_dst;			//Destination MAC address
						std::string IP_src = "None", IP_dst = "None"; //IP source and destination
						int len, sigS, cFlags; //Packet length, signal strength, channel flags
						float dR = 0;			//Data rate
						
						//Timestamp of the packet
						Timestamp tstamp = pkt.timestamp();
						ts = tstamp.seconds();
						//std::cout << ts << std::endl;
						
						//802.11 data layer with packets that have IP addresses
						if(pkt.pdu()->find_pdu<Dot11Data>()) {
							//Initializing 802.11 data layer object
							const Dot11Data &d11d = pdu.rfind_pdu<Dot11Data>();
							//Source MAC address
							M_src = d11d.addr2().to_string();
							//Destination MAC address
							M_dst = d11d.addr1().to_string();
						}
						//For management frames like probe and beacons without IP addresses
						else if(pkt.pdu()->find_pdu<Dot11ManagementFrame>()) {
							const Dot11ManagementFrame &d11m = pdu.rfind_pdu<Dot11ManagementFrame>();
							M_src = d11m.addr2().to_string();
							M_dst = d11m.addr1().to_string();
						}
						//For special frames that only have a destination
						else if(pkt.pdu()->find_pdu<Dot11>()) {
							const Dot11 &d11 = pdu.rfind_pdu<Dot11>();
							M_dst = d11.addr1().to_string();
						}
						//std::cout << M_src << std::endl << M_dst << std::endl;
						
						//Grabbing communication statistcs
						if(pkt.pdu()->find_pdu<RadioTap>()) {
							//Initializing the Radio Tap layer of the packet
							const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>();
							
							//Determining the channel
							if((radiotap.present() & RadioTap::CHANNEL) != 0) {
								/**
								 * 0x140 = 320 -> 802.11a and 802.11n using data rate to separate
								 **/
								
								//We take the channel flag and get details on frequency and channel
								cFlags = radiotap.channel_type();
							}
							
							//Determining data rate in Mb/s
							if((radiotap.present() & RadioTap::RATE) != 0) {
								dR = radiotap.rate()/2.0;
							}
							
							//Determining signal strength in dB
							if((radiotap.present() & RadioTap::DBM_SIGNAL) != 0) {
								sigS = radiotap.dbm_signal();
							}
						}
						
						//Taking a look at the IP layer
						if (pkt.pdu()->find_pdu<IP>()) {
							//Initializing IP layer of the packet
							const IP &ip = pdu.rfind_pdu<IP>();
							//IP source
							IP_src = ip.src_addr().to_string();
							//IP Destination
							IP_dst = ip.dst_addr().to_string();
						}
						
						/*Determining number of users based on unique MAC address
						 * The case of initializing the vector if we have two 
						 * distinct MAC addresses
						 */
						if((uniqueMAC.empty()) & (M_src != "None")){
							statVect[1] = 2;
							uniqueMAC.push_back(M_src);
							uniqueMAC.push_back(M_dst);
						}
						//The case of initializing the vector by encountering 
						// the special packet with only a destination MAC address
						else if((uniqueMAC.empty()) & (M_src == "None")){
							statVect[1] = 1;
							uniqueMAC.push_back(M_dst);
						}
						else if(M_src == "None") {
							;
						}
						//The case of adding to the vector once we encounter 
						// other unique MAC addresses
						else{
							if(std::find(uniqueMAC.begin(), uniqueMAC.end(), M_src) != uniqueMAC.end()) {
								;
							}
							else {
								statVect[1] += 1;
								uniqueMAC.push_back(M_src);
							}
							if(std::find(uniqueMAC.begin(), uniqueMAC.end(), M_dst) != uniqueMAC.end()) {
								;
							}
							else {
								statVect[1] += 1;
								uniqueMAC.push_back(M_dst);
							}
						}
						
						//Adding up every size of the packet in bytes
						statVect[2] += pdu.size();
						
						//Adding up the signal strength of all packets
						statVect[4] += sigS;
						
						//Adding the data rate of all packets
						statVect[5] += dR;
						
						pktCount += 1;
						
						
						if(dR > 0){
							//std::cout << "802.11a" << std::endl << std::endl;
							statVect[6] += pdu.size();
						}
						else {
							//std::cout << "802.11n" << std::endl << std::endl;
							statVect[8] += pdu.size();
						}
						
					}
					/*
					for(auto& stat: statVect) {
						std::cout << stat << std::endl;
					}
					*/
					
					/**Update this**/
					
					//Timestamp of the last packet
					statVect[0] = ts;
					
					//Total number of packets
					statVect[3] = pktCount;
					//Taking average signal strength
					statVect[4] = statVect[4] / statVect[3];
					//Taking average data rate
					statVect[5] = statVect[5] / statVect[3];
					
					//std::cout << "Number of users " << statVect[1] << std::endl;
					
					//String vector to upload the data to the database
					std::vector<std::string> stringVect(9);
					for(int i = 0; i < 9; i++) {
						stringVect[i] = std::to_string(statVect[i]);
					}
					/*
					std::cout << std::endl;
					for(auto& stat: statVect) {
						std::cout << stat << std::endl;
					}
					*/
					
					//Only write to database if there is user activity in the pcap file
					if(statVect[1] > 0) {
						//Creates table with the name as the variable t_name
						//db.makeTable("");
						std::string keyString = std::to_string(z);
						//First input to choose table to write to, second the vector of data
						db.writeData(table_name, keyString, stringVect);
						std::cout << "Wrote to table" << std::endl;
						z++;
						std::cout << std::endl;
					}
					else {
						std::cout << statVect[1] << std::endl;
					}
				}
			/**Delete pcap file**/
			std::string del = i->path().string();
			std::cout << del << std::endl;
			usleep(750000);
			//std::cout << "Removed: " << del << std::endl;
			
			if(remove(del.c_str()) != 0) {
				perror("Error deleting file");
			}
			else {
				std::cout << "Deleted " << del << std::endl;
			}
			}
		}
	usleep(1000100);
	//loopbreak = 0;
	}
	db.disconnect();
}
