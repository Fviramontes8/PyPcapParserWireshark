/*
 * Authors: Francisco Viramontes, Seth Decker
 * 
 * Description: This program is a packet parser intended to accomplish
 * 	two things: 
 * 	First, to take statistical information from all users in one pcap
 * 	file as given by the command line and organize it to display a set
 * 	amount of conversations between two users for all users, and to 
 * 	display it in the format of: 
 * 
 * 	Key (To upload to database), Timestamp, MAC source, MAC destination,
 * 	IP source, IP destination, bits from MAC source to MAC destination, 
 * 	number of packets in the conversation, average signal strength, 
 * 	average data rate, frequency used in the conversation, 
 * 	802.11b counter, 802.11g counter, and 802.11n counter
 * 
 * 	Note: If there are no addresses for either the MAC or IP it will 
 * 	say "none" (Some 802.11 packets only talk on the data link-layer 
 * 	and other on the networking layer so we can have packets with all 
 * 	four addresses [MAC src & dst, IP src & dst], just MAC addresses or 
 * 	even some with just a MAC destination address.)
 * 
 * 	Second, the parser will look for any dns (Domain Name Service)
 * 	response packets and put any answers they have in to map
 * 	(A data structure that has a key/value pair with the value mapped to 
 * 	a unique key) with the key being an IP address and the value being 
 * 	the full qualified domian name. Later this data structure will be
 * 	used to determine services used in the set of conversations like
 * 	video, audio, and VoIP.
 * 
 * Input: Any pcap file that captured packets via Wi-Fi (A 
 * 	tutorial link for capturing via Wi-Fi through wireshark is here:
 * 	https://wiki.wireshark.org/CaptureSetup/WLAN). This parser DOES NOT
 * 	WORK with pcap files that captured packets via Ethernet.
 * 
 * Output: TBD
*/

#include <tins/tins.h> //Header for pcap parser
#include <iostream>
#include <bitset>
#include <stddef.h>
#include <time.h> //For measuring run time of parsing
#include <map> //For use of the map data structure
#include <string> //For use of std::string
#include <boost/variant.hpp>//For use of having a map that contain strings and ints
#include <vector>


/***********************************************************************
*REMEMBER DNS ANSWER
***********************************************************************/

using namespace Tins;
//typedef boost::variant<int, std::string> IntOrString;

/*int getDKey(int x) {
	//Add fn to get key from data base
	return x;
}*/

int main(int argc, char* argv[]) {
	//To keep track of where we are in the pcap file
	int count = 0;
	//Index to keep track how many converations are in the database
	int x = 0;
	int nPkt = 0; //Local version
	//Variables to keep track on how long the program is running
	timeval tm1, tm2;
	//We take the pcap from the command line to read it
	FileSniffer sniffer(argv[1]);
	gettimeofday(&tm1,NULL);
	
	//Creating maps within maps to get converations
	/*Map list has this format: key, ts, M_src, M_dst, IP_src, IP_dst,
	*  bits from M_src to M_dst, # of pkts, signal strength, data rate,
	*  frequency, b/g/n counter.
	*/
	
	//Probably the array for the final output, probably
	////std::array<IntOrString, 14> stat;
	
	/*Four layer map for organizing conversations, using a map is quick
	 * to find keys and to see if you have them or not as oppossed to 
	 * a list, in which you have to loop through every element. It is
	 * much faster to organize the conversations and to call specific
	 * converations based on variables.
	 */
	
	//One map for string
	std::map<std::string, std::map<std::string,std::map<std::string, \
	std::map<std::string, std::array<std::string, 5>>>>> stringDict;
	
	//Another map for intergers
	std::map<std::string, std::map<std::string,std::map<std::string, \
	std::map<std::string, std::array<int, 10>>>>> intDict;
	
	while (Packet pkt = sniffer.next_packet())  {
		//Packet object
		const PDU &pdu = *pkt.pdu();
		
		//Declaration of important variables
		std::string M_src = "None";
		std::string M_dst = "None";
		std::string IP_src = "None";
		std::string IP_dst = "None";
		int len, freq, sigS, ts, cFlags;
		float dR = 0;
		
		//getDKey(x);
		
		//Timestamp of a given packet
		Timestamp tstamp = pkt.timestamp();
		ts = tstamp.seconds();
		//802.11 data layer with IP addresses
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
			M_src = d11m.addr1().to_string();
			//Destination MAC address
			M_dst = d11m.addr2().to_string();
		}
		//This is for the special frames that only have a destination
		else if (pkt.pdu()->find_pdu<Dot11>()) {
			const Dot11 &d11 = pdu.rfind_pdu<Dot11>();
			
			M_dst = d11.addr1().to_string();
		}
		//IP layer
		if (pkt.pdu()->find_pdu<IP>()) {
			const IP &ip = pdu.rfind_pdu<IP>();
			
			//IP source
			IP_src = ip.src_addr().to_string();
			//IP Destination
			IP_dst = ip.dst_addr().to_string();
		}
		
		std::cout << "Packet " << count + 1 << std::endl;
		
		//Size of the packet in bytes
		len = pdu.size();
		//This layer gives us information related to communications
		if (pkt.pdu()->find_pdu<RadioTap>()) 
		{
			//RadioTap layer of packet
			const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>();
			
			if ((radiotap.present() & RadioTap::CHANNEL) != 0) {
				//Communication Frequency
				freq = radiotap.channel_freq();
				
				//802.11b = 0xa0 or 160
				//802.11g = 0xc0 or 192
				//802.11n = 0x480 or 1152
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
		
		//A totally new conversation
		if (stringDict.count(M_src) == 0) {
			stringDict[M_src][M_dst][IP_src][IP_dst][0] = std::to_string(nPkt);
			stringDict[M_src][M_dst][IP_src][IP_dst][1] = M_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][2] = M_dst;
			stringDict[M_src][M_dst][IP_src][IP_dst][3] = IP_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][4] = IP_dst;
			
			intDict[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
			intDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			intDict[M_src][M_dst][IP_src][IP_dst][2] = len;
			intDict[M_src][M_dst][IP_src][IP_dst][3] = 1;
			intDict[M_src][M_dst][IP_src][IP_dst][4] = sigS;
			intDict[M_src][M_dst][IP_src][IP_dst][5] = dR;
			intDict[M_src][M_dst][IP_src][IP_dst][6] = freq;
			
			if(cFlags == 160) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 192) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 1152) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 1;
			}
			nPkt++;
		}
		//The source is the same but now there is a different destination
		else if (stringDict[M_src].count(M_dst) == 0) {
			stringDict[M_src][M_dst][IP_src][IP_dst][0] = std::to_string(nPkt);
			stringDict[M_src][M_dst][IP_src][IP_dst][1] = M_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][2] = M_dst;
			stringDict[M_src][M_dst][IP_src][IP_dst][3] = IP_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][4] = IP_dst;
			
			intDict[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
			intDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			intDict[M_src][M_dst][IP_src][IP_dst][2] = len;
			intDict[M_src][M_dst][IP_src][IP_dst][3] = 1;
			intDict[M_src][M_dst][IP_src][IP_dst][4] = sigS;
			intDict[M_src][M_dst][IP_src][IP_dst][5] = dR;
			intDict[M_src][M_dst][IP_src][IP_dst][6] = freq;
			
			if(cFlags == 160) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 192) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 1152) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 1;
			}
			nPkt++;
		}
		//There is a new IP source
		else if (stringDict[M_src][M_dst].count(IP_src) == 0) {
			stringDict[M_src][M_dst][IP_src][IP_dst][0] = std::to_string(nPkt);
			stringDict[M_src][M_dst][IP_src][IP_dst][1] = M_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][2] = M_dst;
			stringDict[M_src][M_dst][IP_src][IP_dst][3] = IP_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][4] = IP_dst;
			
			intDict[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
			intDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			intDict[M_src][M_dst][IP_src][IP_dst][2] = len;
			intDict[M_src][M_dst][IP_src][IP_dst][3] = 1;
			intDict[M_src][M_dst][IP_src][IP_dst][4] = sigS;
			intDict[M_src][M_dst][IP_src][IP_dst][5] = dR;
			intDict[M_src][M_dst][IP_src][IP_dst][6] = freq;
			
			if(cFlags == 160) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 192) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 1152) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 1;
			}
			nPkt++;
		}
		//There is a new IP destination
		else if (stringDict[M_src][M_dst][IP_src].count(IP_dst) == 0) {
			stringDict[M_src][M_dst][IP_src][IP_dst][0] = std::to_string(nPkt);
			stringDict[M_src][M_dst][IP_src][IP_dst][1] = M_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][2] = M_dst;
			stringDict[M_src][M_dst][IP_src][IP_dst][3] = IP_src;
			stringDict[M_src][M_dst][IP_src][IP_dst][4] = IP_dst;
			
			intDict[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
			intDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			intDict[M_src][M_dst][IP_src][IP_dst][2] = len;
			intDict[M_src][M_dst][IP_src][IP_dst][3] = 1;
			intDict[M_src][M_dst][IP_src][IP_dst][4] = sigS;
			intDict[M_src][M_dst][IP_src][IP_dst][5] = dR;
			intDict[M_src][M_dst][IP_src][IP_dst][6] = freq;
			
			if(cFlags == 160) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 192) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 1;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 0;
			}
			else if(cFlags == 1152) {
				intDict[M_src][M_dst][IP_src][IP_dst][7] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][8] = 0;
				intDict[M_src][M_dst][IP_src][IP_dst][9] = 1;
			}
			nPkt++;
		}
		//Once all unique conversations are created, now we just need
		// to keep them updated
		else {
			intDict[M_src][M_dst][IP_src][IP_dst][2] += len;
			intDict[M_src][M_dst][IP_src][IP_dst][3]++;
			intDict[M_src][M_dst][IP_src][IP_dst][4] += sigS;
			intDict[M_src][M_dst][IP_src][IP_dst][5] += dR;
			
			if(cFlags == 160) {
				intDict[M_src][M_dst][IP_src][IP_dst][7]++;
			}
			else if(cFlags == 192) {
				intDict[M_src][M_dst][IP_src][IP_dst][8]++;
			}
			else if(cFlags == 1152) {
				intDict[M_src][M_dst][IP_src][IP_dst][9]++;
			}
		}
		count++;
	}
	
	//A vector that has a vector of strings
	std::vector<std::vector <std::string>> stringFinal(nPkt,std::vector<std::string>(5));
	//u is supposed to be the rows, of number of conversations in stringDict
	int u = nPkt - 1;
	for(auto& iter_a : stringDict) {
		for(auto& iter_b :stringDict[iter_a.first]) {
			for(auto& iter_c : stringDict[iter_a.first][iter_b.first]){
				for(auto& iter_d : stringDict[iter_a.first][iter_b.first][iter_c.first]) {
					//v is for every element that is in a single conversation
					int v = 0;
					for(auto& iter_e : stringDict[iter_a.first][iter_b.first][iter_c.first][iter_d.first]){
						stringFinal[u][v] = iter_e;
						std::cout << iter_e << std::endl;
						v++;
					}
					u--;
					std::cout << std::endl;
				}
			}
		}
	}
	//Printing the vector of strings
	std::cout << "Vector of strings" << std::endl;
	for(int p = 0; p < nPkt; p++){
		for(int q = 0; q < 5; q++) {
			std::cout << stringFinal[p][q] << std::endl;
		}
		std::cout << std::endl;
	}
	
	std::vector<std::vector <int>> intFinal(nPkt,std::vector<int>(10));
	//Reinitializing u to use again for the int vector
	u = nPkt - 1;
	for (auto& iter : intDict) {
		for(auto& iter1 : intDict[iter.first]) {
			for (auto& iter2 : intDict[iter.first][iter1.first]) {
				for(auto& iter3 : intDict[iter.first][iter1.first][iter2.first]) {
					//Taking averages of signal strength and data rate
					int miniIter = 0;
					int miniDiv = 1;
					for(auto& iter4 : intDict[iter.first][iter1.first][iter2.first][iter3.first]) {
						if(miniIter == 3) {
							miniDiv = iter4;
						}
						if(miniIter == 4){
							iter4 = iter4 / miniDiv;
						}
						if(miniIter == 5) {
							iter4 = iter4 / miniDiv;
						}
						intFinal[u][miniIter] = iter4;
						std::cout << iter4 << std::endl;
						miniIter++;
					}
					u--;
					std::cout << std::endl;
				}
			}
		}
	}
	//Printing the vector of ints
	std::cout << "Vector of ints" << std::endl;
	for(int p = 0; p < nPkt; p++){
		for(int q = 0; q < 10; q++) {
			std::cout << intFinal[p][q] << std::endl;
		}
		std::cout << std::endl;
	}
	//int someint = std::stoi(somestring);
	gettimeofday(&tm2,NULL);
	
	std::cout << "Microseconds: "<< tm2.tv_sec * 1000000  + tm2.tv_usec - (tm1.tv_sec * 1000000 + tm1.tv_usec) << std::endl;
}
