/***********************************************************************
 * Authors: Francisco Viramontes, Seth Decker
 * 
 * Description: This program is a packet parser intended to take  
 *  statistical information from all users in a folder of pcap files
 *  and organize it to display meaningful statistics in the format of: 
 * 
 * 	Timestamp, number of users, total bits in the pcap file, 
 * 	number of packets in the pcap file, average signal strength, 
 * 	average data rate, number of 802.11b packets, number of 802.11g
 *  packets, and  number of 802.11n packets
 * 
 * Input: Any pcap file that captured packets via Wi-Fi (A 
 * 	tutorial link for capturing via Wi-Fi through wireshark is here:
 * 	https://wiki.wireshark.org/CaptureSetup/WLAN). This parser DOES NOT
 * 	WORK with pcap files that captured packets via ETHERNET.
 * 
 * Output: 
 *  A vector that contains a sequence of integers that can be pushed 
 *  into a database.
 * 
 **********************************************************************/


#include <tins/tins.h> //Header for pcap parser
#include <iostream>
#include <bitset>
#include <stddef.h>
#include <string> //For use of std::string
#include <vector> //For the use of vectors
#include <boost/filesystem.hpp> //To get multiple pcap files in a folder
#include "DatabaseConnect.hpp" //From local file to talk to a postgresql database
#include <algorithm> //For searching the vector of unique MAC addresses

using namespace Tins;

int main(int argc, char* argv[]) {
	//Opening connection with database
	DatabaseConnect db("postgres", "129.24.26.137", "postgres", "Cerculsihr4T");
	db.connect();
	
	std::string table_name = "Mon_Tues";
	
	//Getting database key
	int z = db.getNextKey(table_name);
	
	//Making sure we don't reparse files
	std::vector<std::string> lastFiles;
	
	//String for table name
	std::string t_name;
	
	int breakout = 0;
	int loopbreak = 1;
	
	//The path given is to open the pcap files in the directory of chosing
/**********************************************************************/
	const std::string path("/root/Desktop/Pkt_data_live/");
/**********************************************************************/
	
	//Time to iterate through the directory of chosing to parse the pcap files
	boost::filesystem::directory_iterator end_itr;
	usleep(100000);
	while(loopbreak) {
	for(boost::filesystem::directory_iterator i(path); i != end_itr; i++) {
		//To keep track of how many packets have been parsed
		int count;
		
		//Total number of channel flags
		int bgn = 0;
		
		//Time stamp
		int ts;
		
		/*A vector of integers that will have a layout of:
		 * <Timestamp, Number of Users, Total Bits, Packets,
		 * Average Signal Strength, Average Data Rate, 
		 * percentage of 802.11b packets, percentage of 802.11g packets,
		 * percentage of 802.11n packets>
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
			for(auto& t : lastFiles) {
				if(t == i->path().string()) {
					fileCheck = 1;
				}
			}
			if(breakout == 6) {
				loopbreak = 0;
			}
			else if(fileCheck != 0) {
				std::cout << "Waiting..." << std::endl;
				usleep(1000000);
				fileCheck = 0;
				breakout++;
			}
			else {
				if(lastFiles.size() > 8) {
					lastFiles.erase(lastFiles.begin());
					lastFiles.push_back(i->path().string());
				}
				else  {
					lastFiles.push_back(i->path().string());
				}
			
			//We take the pcap from the directory of chosing and begin parsing
			FileSniffer sniffer(i->path().string());
			breakout = 0;
			count = 1;
			
/***********************************************************************
 * Try making vector size 3 and adding file names to it
 * when full, use myVector.erase(myVector.begin()); to pop first element
 * push_back the next file.
 * ********************************************************************/
			
			while(Packet pkt = sniffer.next_packet())  {
				//Packet object
				const PDU &pdu = *pkt.pdu();
				
				/*/Prints out every 100th packet
				if(count % 100 == 0){
					std::cout << "Packet: " << count << std::endl;
				}*/
				
				//Declaration of important variables
				std::string M_src = "None";
				std::string M_dst;
				int len, sigS, cFlags;
				float dR = 0;
				
				//Timestamp of the packet
				Timestamp tstamp = pkt.timestamp();
				ts = tstamp.seconds();
				//t_name = "pcap_data"; //"t_" + std::to_string(ts);
					
				
				//802.11 data layer with packets that have IP addresses
				if (pkt.pdu()->find_pdu<Dot11Data>()) {
					//802.11 data layer object
					const Dot11Data &d11d = pdu.rfind_pdu<Dot11Data>();
					//Source MAC address
					M_src = d11d.addr2().to_string();
					//Destination MAC address
					M_dst = d11d.addr3().to_string();
				}
				//This is for management frames like probe and beacons 
				// without IP addresses
				else if (pkt.pdu()->find_pdu<Dot11ManagementFrame>()) {
					const Dot11ManagementFrame &d11m = pdu.rfind_pdu<Dot11ManagementFrame>();
					
					//Source MAC address
					M_src = d11m.addr2().to_string();
					//Destination MAC address
					M_dst = d11m.addr1().to_string();
				}
				//This is for special frames that only have a destination
				else if (pkt.pdu()->find_pdu<Dot11>()) {
					const Dot11 &d11 = pdu.rfind_pdu<Dot11>();
					
					M_dst = d11.addr1().to_string();
				}
				
				//This layer gives us information related to communications
				if (pkt.pdu()->find_pdu<RadioTap>()) {
					//RadioTap layer of packet
					const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>();
					
					if ((radiotap.present() & RadioTap::CHANNEL) != 0) {
						/**802.11b is 0xa0 or 160
						 * 802.11g is 0xc0 or 192
						 * 802.11n is 0x480 or 1152
						 **/
						 
						//Channel flags can give us type of modulation,
						// frequency band, and if it is 802.11b, g, or n.
						cFlags = radiotap.channel_type();
					}
					if ((radiotap.present() & RadioTap::RATE) != 0) {
						//Data rate in Mb/s
						dR = radiotap.rate()/2.0;
					}
					if ((radiotap.present() & RadioTap::DBM_SIGNAL) != 0) {
						//Signal strength in dB
						sigS = radiotap.dbm_signal();
					}
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
				
				//Updating 802.11b/g/n counter with bgn being total flags
				if(cFlags == 160) {
					statVect[6]++;
					bgn++;
				}
				else if(cFlags == 192) {
					statVect[7]++;
					bgn++;
				}
				else if(cFlags == 1152) {
					statVect[8]++;
					bgn++;
				}
					
								
				count++;
			}
			
			/**Updating the vector with finalized statistics**/
			
			//Timestamp of the last packet
			statVect[0] = ts;
			
			//Total number of packets
			statVect[3] = count;
			//Taking average signal strength
			statVect[4] = statVect[4] / statVect[3];
			//Taking average data rate
			statVect[5] = statVect[5] / statVect[3];
			statVect[6] = (static_cast<float>(statVect[6]) / bgn) * 100;
			statVect[7] = (static_cast<float>(statVect[7]) / bgn) * 100;
			statVect[8] = (static_cast<float>(statVect[8]) / bgn) * 100;
			
			std::vector<std::string> stringVect(9);
			for(int i = 0; i < 9; i++) {
				stringVect[i] = std::to_string(statVect[i]);
			}
			//Only write to database if there is user activity in the pcap file
			if(statVect[1] > 0) {
				//Creates table with the name as the variable t_name
				//db.makeTable("pcap_data");
				std::string keyString = std::to_string(z);
				//First input to choose table to write to, second the vector of data
				db.writeData(table_name, keyString, stringVect);
				z++;
				std::cout << std::endl;
			}
			}
		}
	}
	}
	db.disconnect();
	return 0;
}
