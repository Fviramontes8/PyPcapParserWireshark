/*
 * Authors: Francisco Viramontes, Seth Decker
 * 
 * 
*/

#include <tins/tins.h> //Header for pcap parser
#include <iostream>
#include <bitset>
#include <stddef.h>
#include <time.h> //For measuring run time of parsing
#include <map> //For use of the map data structure
#include <string> //For use of std::string
#include <boost/variant.hpp>//For use of having a map that contain strings and ints


/***********************************************************************
*REMEMBER DNS ANSWER
***********************************************************************/

using namespace Tins;
typedef boost::variant<int, std::string> IntOrString;

/*int getDKey(int x) {
	//Add fn to get key from data base
	return x;
}*/

int main(int argc, char* argv[])
{
	int count = 0;
	int x = 0;
	timeval tm1, tm2;
	FileSniffer sniffer(argv[1]);
	gettimeofday(&tm1,NULL);
	
	//Creating maps within maps to get converations
	/*Map list has this format: key, ts, M_src, M_dst, IP_src, IP_dst,
	*  bits from M_src to M_dst, # of pkts, signal strength, data rate,
	*  frequency, b/g/n counter.
	*/
	
	std::array<IntOrString, 14> stat;
	
	std::map<std::string, std::map<std::string,std::map<std::string, \
	std::map<std::string, std::array<IntOrString, 14>>>>> statDict;
	
	while (Packet pkt = sniffer.next_packet()) 
	{
		const PDU &pdu = *pkt.pdu();
		
		//Declaration of important variables
		std::string M_src = "None";
		std::string M_dst = "None";
		std::string IP_src = "None";
		std::string IP_dst = "None";
		int len, freq, sigS, ts, cFlags;
		float dR = 0;
		
		//getDKey(x);
		
		Timestamp tstamp = pkt.timestamp();
		ts = tstamp.seconds();
		
		if (pkt.pdu()->find_pdu<Dot11Data>()) {
			const Dot11Data &d11d = pdu.rfind_pdu<Dot11Data>(); // Find the 802.11 data layer
			
			//Source MAC address
			M_src = d11d.addr3().to_string();
			//Destination MAC address
			M_dst = d11d.addr1().to_string();
		}
		else if (pkt.pdu()->find_pdu<Dot11ManagementFrame>()) {
			const Dot11ManagementFrame &d11m = pdu.rfind_pdu<Dot11ManagementFrame>();
			
			//Source MAC address
			M_src = d11m.addr2().to_string();
			//Destination MAC address
			M_dst = d11m.addr1().to_string();
		}
		else if (pkt.pdu()->find_pdu<Dot11>()) {
			const Dot11 &d11 = pdu.rfind_pdu<Dot11>();
			
			M_dst = d11.addr1().to_string();
		}
		if (pkt.pdu()->find_pdu<IP>()) {
			const IP &ip = pdu.rfind_pdu<IP>(); // Find the IP layer
			
			//IP source
			IP_src = ip.src_addr().to_string();
			//IP Destination
			IP_dst = ip.dst_addr().to_string();
		}
		
		std::cout << "Packet " << count + 1 << std::endl;
		
		len = pdu.size();
		
		if (pkt.pdu()->find_pdu<RadioTap>()) 
		{
			const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>(); // Find the RadioTap layer
			
			if ((radiotap.present() & RadioTap::CHANNEL) != 0)
			{
				//Communication Frequency
				freq = radiotap.channel_freq();
				
				//802.11b = 0xa0 or 160
				//802.11g = 0xc0 or 192
				//802.11n = 0x480 or 1152
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
			
	/*Map list has this format: key, ts, M_src, M_dst, IP_src, IP_dst,
	*  bits from M_src to M_dst, # of pkts, signal strength, data rate,
	*  frequency, b/g/n counter.
	*/
		
		if (statDict.count(M_src) == 0) {
			std::cout << "Fresh convo!" << std::endl;
			
			statDict[M_src][M_dst][IP_src][IP_dst][0] = 0;
			statDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			statDict[M_src][M_dst][IP_src][IP_dst][2] = M_src;
			statDict[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
			statDict[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][6] = len;
			statDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
			statDict[M_src][M_dst][IP_src][IP_dst][8] = sigS;
			statDict[M_src][M_dst][IP_src][IP_dst][9] = dR;
			statDict[M_src][M_dst][IP_src][IP_dst][10] = freq;
			
			if((cFlags & 160) != 0){
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 192) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 1152) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 1;
			}
			
			
			std::cout << "M_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][2] << std::endl;
			std::cout << "M_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][3] << std::endl;
			std::cout << "IP_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][4] << std::endl;
			std::cout << "IP_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][5] << std::endl;
		}
		else if (statDict[M_src].count(M_dst) == 0) {
			std::cout << "Fresh Destination!" << std::endl;
			
			statDict[M_src][M_dst][IP_src][IP_dst][0] = 0;
			statDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			statDict[M_src][M_dst][IP_src][IP_dst][2] = M_src;
			statDict[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
			statDict[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][6] = len;
			statDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
			statDict[M_src][M_dst][IP_src][IP_dst][8] = sigS;
			statDict[M_src][M_dst][IP_src][IP_dst][9] = dR;
			statDict[M_src][M_dst][IP_src][IP_dst][10] = freq;
			
			if((cFlags & 160) != 0){
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 192) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 1152) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 1;
			}
			
			std::cout << "M_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][2] << std::endl;
			std::cout << "M_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][3] << std::endl;
			
			std::cout << "IP_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][4] << std::endl;
			std::cout << "IP_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][5] << std::endl;
		}
		else if (statDict[M_src][M_dst].count(IP_src) == 0) {
			std::cout << "Fresh IP!" << std::endl;
			
			
			statDict[M_src][M_dst][IP_src][IP_dst][0] = 0;
			statDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			statDict[M_src][M_dst][IP_src][IP_dst][2] = M_src;
			statDict[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
			statDict[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][6] = len;
			statDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
			statDict[M_src][M_dst][IP_src][IP_dst][8] = sigS;
			statDict[M_src][M_dst][IP_src][IP_dst][9] = dR;
			statDict[M_src][M_dst][IP_src][IP_dst][10] = freq;
			
			if((cFlags & 160) != 0){
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 192) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 1152) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 1;
			}
			
			std::cout << "M_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][2] << std::endl;
			std::cout << "M_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][3] << std::endl;
			
			std::cout << "IP_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][4] << std::endl;
			std::cout << "IP_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][5] << std::endl;
		}
		else if (statDict[M_src][M_dst][IP_src].count(IP_dst) == 0) {
			std::cout << "Fresh IP Dst!" << std::endl;
			
			statDict[M_src][M_dst][IP_src][IP_dst][0] = 0;
			statDict[M_src][M_dst][IP_src][IP_dst][1] = ts;
			statDict[M_src][M_dst][IP_src][IP_dst][2] = M_src;
			statDict[M_src][M_dst][IP_src][IP_dst][3] = M_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][4] = IP_src;
			statDict[M_src][M_dst][IP_src][IP_dst][5] = IP_dst;
			statDict[M_src][M_dst][IP_src][IP_dst][6] = len;
			statDict[M_src][M_dst][IP_src][IP_dst][7] = 1;
			statDict[M_src][M_dst][IP_src][IP_dst][8] = sigS;
			statDict[M_src][M_dst][IP_src][IP_dst][9] = dR;
			statDict[M_src][M_dst][IP_src][IP_dst][10] = freq;
			
			if((cFlags & 160) != 0){
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 192) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 1;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 0;
			}
			else if((cFlags & 1152) != 0) {
				statDict[M_src][M_dst][IP_src][IP_dst][11] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][12] = 0;
				statDict[M_src][M_dst][IP_src][IP_dst][13] = 1;
			}
			
			std::cout << "M_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][2] << std::endl;
			std::cout << "M_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][3] << std::endl;
			
			std::cout << "IP_Src: " << statDict[M_src][M_dst][IP_src][IP_dst][4] << std::endl;
			std::cout << "IP_dst: " << statDict[M_src][M_dst][IP_src][IP_dst][5] << std::endl;
		}
		else {
			std::cout << "Help" << std::endl;
		}
		
		}
			
		std::cout << std::endl;
		count++;
	}
/////////////////////////////////////////////////////////////////////////////////////////
		//std::map<string, list<string>> mapex; list<string> li;
		typedef std::map<std::string, std::map<std::string,std::map<std::string, \
		std::map<std::string, std::array<IntOrString, 14>>>>>::const_iterator MapIterator;
		for (MapIterator iter = statDict.begin(); iter != statDict.end(); iter++)
		{
			typedef std::map<std::string,std::map<std::string, \
			std::map<std::string, std::array<IntOrString, 14>>>>::const_iterator MapIterator1;
			for(MapIterator1 iter1 = iter->second.begin(); iter1 != iter->second.end(); iter1++) {
				typedef std::map<std::string, std::map<std::string, \
				std::array<IntOrString, 14>>>::const_iterator MapIterator2;
				for (MapIterator2 iter2 = iter1->second.begin(); iter2 != iter1->second.end(); iter2++) {
					typedef std::map<std::string, std::array<IntOrString, 14>>::const_iterator MapIterator3;
					for(MapIterator3 iter3 = iter2->second.begin(); iter3 != iter2->second.end(); iter3++) {
						
						std::cout <<  iter->first << " " << iter1->first\
						<< " " << iter2->first << " " << iter3->first <<\
						std::endl;
					}
				}
			}
			
			/*typedef list<string>::const_iterator ListIterator;
			for (ListIterator list_iter = iter->second.begin(); list_iter != iter->second.end(); list_iter++)
				std::cout << " " << *list_iter << std::endl;*/
		}
///////////////////////////////////////////////////////////////////////////////////////////
	gettimeofday(&tm2,NULL);
	
	std::cout << "Microseconds: "<< tm2.tv_sec * 1000000  + tm2.tv_usec - (tm1.tv_sec * 1000000 + tm1.tv_usec) << std::endl;
}
