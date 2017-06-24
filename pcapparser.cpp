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
 * Output: 
 *  Firstly, a matrix that contains a sequence of integers 
 *  and strings as given above (Key, Timestamp, MAC source, etc.
 *  
 *  Secondly, a map that contains IP addresses as a key (as a string) 
 *  and values (also as a string) that match the IP address to a website
 *  (like 208.77.78.215 to youtube-ui.l.google.com)
*/

#include <tins/tins.h> //Header for pcap parser
#include <iostream>
#include <bitset>
#include <stddef.h>
#include <time.h> //For measuring run time of parsing
#include <map> //For use of the map data structure
#include <string> //For use of std::string
#include <boost/variant.hpp>//For use of having a map that contain strings and ints
#include <vector> //For the use of vectors
#include <boost/filesystem.hpp> //To get multiple pcap files in a folder
#include "DatabaseConnect.hpp"

using namespace Tins;
typedef boost::variant<int, std::string> IntOrString;

int main(int argc, char* argv[]) {
	//Variables to keep track on how long the program is running
	timeval tm1, tm2;
	gettimeofday(&tm1,NULL);
	
	//The path given is to open the pcap files in the directory of chosing
/**********************************************************************/
	const std::string path("/root/PyPcapParserWireshark/");
/**********************************************************************/
	
	//Time to iterate through the directory of chosing to parse the pcap files
	boost::filesystem::directory_iterator end_itr;
	for(boost::filesystem::directory_iterator i(path); i != end_itr; i++) {
		//To keep track of where we are in the pcap file
		int count = 0;
		//Index to keep track how many converations are in the database
		int x = 0;
		int nPkt = 0; //Local version
		
		/*Four layer map for organizing conversations, using a map is quick
		* to find keys and to see if you have them or not as oppossed to 
		* a list, in which you have to loop through every element. It is
		* much faster to organize the conversations and to call specific
		* converations based on variables.
		* 
		* Map list has this format: key, ts, M_src, M_dst, IP_src, IP_dst,
		*  bits from M_src to M_dst, # of pkts, signal strength, data rate,
		*  frequency, b/g/n counter.
		*/
		
		std::map<std::string, std::map<std::string,std::map<std::string, \
		std::map<std::string, std::array<IntOrString, 14>>>>> statMap;
		
		//Map for DNS responses to later determine services used in the
		// format of {Unique IP address : website that corresponds to the
		// unique IP address}
		std::map<std::string, std::string> dnsMap;
		
		if(!boost::filesystem::is_regular_file(i->status())) {
			continue;
		}
		
		if(i->path().extension() == ".pcap") {
			//We take the pcap from the directory of chosing and begin parsing
			FileSniffer sniffer(i->path().string());
			
			while(Packet pkt = sniffer.next_packet())  {
				//Packet object
				const PDU &pdu = *pkt.pdu();
				
				std::cout << "Packet " << count + 1 << std::endl;
				
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
					M_src = d11m.addr2().to_string();
					//Destination MAC address
					M_dst = d11m.addr1().to_string();
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
					
					/* To obtain DNS informaion we first check if the packet
					 * has a UDP layer, then if it does we look at port 53 for
					 * dns provided by RFC 1010:
					 * https://tools.ietf.org/html/rfc1010
					 * on page 7, we also look at port 5353 for multicast dns:
					 * https://tools.ietf.org/html/rfc6762
					 * on page 60. If it is using either of those ports the we
					 * get the mdns/dns layer and parse the responses to the 
					 * mdns/dns query.
					 * 
					 * This is done because libtins (tins) does not 
					 * automatically parse DNS packets so it had to be
					 * done the hard way.
					 */
					if(pkt.pdu()->find_pdu<UDP>()) {
						const UDP &udp11 = pdu.rfind_pdu<UDP>();
						if(udp11.sport() == 53 || udp11.dport() == 53 || \
						udp11.sport() == 5353 || udp11.dport() == 5353){
							const DNS &dns11 = pdu.rfind_pdu<RawPDU>().to<DNS>();
							for(auto& dnsAns : dns11.answers()) {
								if(dnsAns.query_type() == 1) {
									std::string dnsIP = dnsAns.data();
									std::string dnsName = dnsAns.dname();
									//Checking if the IP address and the dns
									// dns name are already in the map.
									if(dnsMap.count(dnsIP) == 0) {
										//Assigning dns names to unique 
										// IP addresses.
										dnsMap[dnsIP] = dnsName;
									}
								}
							}
						}
					}
					
					//To check the IP address if it is part of the dns response
					if(!dnsMap.empty()) {
						for(auto& d : dnsMap){
							if(d.first == IP_src) {
								IP_src = d.second;
							}
							if(d.first == IP_dst) {
								IP_dst == d.second;
							}
						}
					}
				}
				
				//Size of the packet in bytes
				len = pdu.size();
				//This layer gives us information related to communications
				if (pkt.pdu()->find_pdu<RadioTap>()) {
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
/***********************************************************************
 * Add MAC filter here
 **********************************************************************/
				
				//A totally new conversation!
				if (statMap.count(M_src) == 0) {
					statMap[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
					statMap[M_src][M_dst][IP_src][IP_dst][1] = ts;
					statMap[M_src][M_dst][IP_src][IP_dst][2] = M_src;
					statMap[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
					statMap[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][6] = len;
					statMap[M_src][M_dst][IP_src][IP_dst][7] = 1;
					statMap[M_src][M_dst][IP_src][IP_dst][8] = sigS;
					statMap[M_src][M_dst][IP_src][IP_dst][9] = dR;
					statMap[M_src][M_dst][IP_src][IP_dst][10] = freq;
					
					if(cFlags == 160) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 192) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 1152) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 1;
					}
					nPkt++;
				}
				//The source is the same but now there is a different destination!
				else if (statMap[M_src].count(M_dst) == 0) {
					statMap[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
					statMap[M_src][M_dst][IP_src][IP_dst][1] = ts;
					statMap[M_src][M_dst][IP_src][IP_dst][2] = M_src;
					statMap[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
					statMap[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][6] = len;
					statMap[M_src][M_dst][IP_src][IP_dst][7] = 1;
					statMap[M_src][M_dst][IP_src][IP_dst][8] = sigS;
					statMap[M_src][M_dst][IP_src][IP_dst][9] = dR;
					statMap[M_src][M_dst][IP_src][IP_dst][10] = freq;
					
					if(cFlags == 160) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 192) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 1152) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 1;
					}
					nPkt++;
				}
				//There is a new IP source!
				else if (statMap[M_src][M_dst].count(IP_src) == 0) {
					statMap[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
					statMap[M_src][M_dst][IP_src][IP_dst][1] = ts;
					statMap[M_src][M_dst][IP_src][IP_dst][2] = M_src;
					statMap[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
					statMap[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][6] = len;
					statMap[M_src][M_dst][IP_src][IP_dst][7] = 1;
					statMap[M_src][M_dst][IP_src][IP_dst][8] = sigS;
					statMap[M_src][M_dst][IP_src][IP_dst][9] = dR;
					statMap[M_src][M_dst][IP_src][IP_dst][10] = freq;
					
					if(cFlags == 160) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 192) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 1152) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 1;
					}
					nPkt++;
				}
				//There is a new IP destination!
				else if (statMap[M_src][M_dst][IP_src].count(IP_dst) == 0) {
					statMap[M_src][M_dst][IP_src][IP_dst][0] = nPkt;
					statMap[M_src][M_dst][IP_src][IP_dst][1] = ts;
					statMap[M_src][M_dst][IP_src][IP_dst][2] = M_src;
					statMap[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
					statMap[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
					statMap[M_src][M_dst][IP_src][IP_dst][6] = len;
					statMap[M_src][M_dst][IP_src][IP_dst][7] = 1;
					statMap[M_src][M_dst][IP_src][IP_dst][8] = sigS;
					statMap[M_src][M_dst][IP_src][IP_dst][9] = dR;
					statMap[M_src][M_dst][IP_src][IP_dst][10] = freq;
					
					if(cFlags == 160) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 192) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 1;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 0;
					}
					else if(cFlags == 1152) {
						statMap[M_src][M_dst][IP_src][IP_dst][11] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = 0;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = 1;
					}
					nPkt++;
				}
				//Once all unique conversations are created, now we just need
				// to keep them updated.
				else {
					/*Since we are using a map that uses both strings and ints
					 * we must pull the ints, modify them and put them back
					 * boost does not like it when you try to modify it on the fly.
					 */
					int newLen = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][6]);
					newLen += len;
					statMap[M_src][M_dst][IP_src][IP_dst][6] = newLen;
					
					int newCount = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][7]);
					newCount++;
					statMap[M_src][M_dst][IP_src][IP_dst][7] = newCount;
					
					int newSigS = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][8]);
					newSigS += sigS;
					statMap[M_src][M_dst][IP_src][IP_dst][8] = newSigS;
					
					int new_dR = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][9]);
					new_dR += dR;
					statMap[M_src][M_dst][IP_src][IP_dst][9] = new_dR;
					
					if(cFlags == 160) {
						int newFlag = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][11]);
						newFlag++;
						statMap[M_src][M_dst][IP_src][IP_dst][11] = newFlag;
					}
					else if(cFlags == 192) {
						int newFlag = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][12]);
						newFlag++;
						statMap[M_src][M_dst][IP_src][IP_dst][12] = newFlag;
					}
					else if(cFlags == 1152) {
						int newFlag = boost::get<int>(statMap[M_src][M_dst][IP_src][IP_dst][13]);
						newFlag++;
						statMap[M_src][M_dst][IP_src][IP_dst][13] = newFlag;
					}
				}
				count++;
			}
		}
	
		//A matrix that now contains the conversations
		//This is one of the FINAL outputs
		std::vector<std::vector <IntOrString>> statFinal(nPkt,std::vector<IntOrString>(14));
		//u is supposed to be the rows, of number of conversations in stringMap
		int u = nPkt - 1;
		for(auto& iter_a : statMap) {
			for(auto& iter_b :statMap[iter_a.first]) {
				for(auto& iter_c : statMap[iter_a.first][iter_b.first]){
					for(auto& iter_d : statMap[iter_a.first][iter_b.first][iter_c.first]) {
						//v is for every element that is in a single conversation
						int v = 0;
						for(auto& iter_e : statMap[iter_a.first][iter_b.first][iter_c.first][iter_d.first]){
							statFinal[u][v] = iter_e;
							v++;
						}
						u--;
					}
				}
			}
		}
		
		//Printing the vector of strings
		for(int p = 0; p < nPkt; p++){
			std::cout << "[";
			for(int q = 0; q < 14; q++) {
				if(q == 13) {
					std::cout << statFinal[p][q] << "]" << std::endl;
				}
				else {
					std::cout << statFinal[p][q] << ", ";
				}
			}
		}
	}
	// TO CONNECT TO DATABASE
	DatabaseConnect db("postgres", "129.24.26.137", "postgres", "Cerculsihr4T");
	db.connect();
	
	db.writeData();
	db.disconnect();
	
	//int someint = std::stoi(somestring);
	gettimeofday(&tm2,NULL);
	
	std::cout << "Microseconds: "<< tm2.tv_sec * 1000000  + tm2.tv_usec - (tm1.tv_sec * 1000000 + tm1.tv_usec) << std::endl;
	return 0;
}
