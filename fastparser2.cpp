#include <tins/tins.h>
#include <iostream>
#include <bitset>
#include <stddef.h>
#include <time.h>

using namespace Tins;


int main(int argc, char* argv[])
{
	int count = 0;
	timeval tm1, tm2;
	FileSniffer sniffer(argv[1]);
	gettimeofday(&tm1,NULL);
	while (Packet pkt = sniffer.next_packet()) 
	{
		std::cout << "Packet " << count << std::endl;
		Timestamp ts = pkt.timestamp();
		std::cout << "Timestamp: " << ts.seconds() << std::endl;
		const PDU &pdu = *pkt.pdu();
		
		
			
		if (pkt.pdu()->find_pdu<RadioTap>())
		{
			const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>(); // Find the RadioTap layer
			
			if ((radiotap.present() & RadioTap::CHANNEL) != 0)
			{
				std::cout << "frequency: " << (int)radiotap.channel_freq() << std::endl;
				std::cout << "type: " << std::bitset<12>(radiotap.channel_type()) << std::endl;
			}
			if ((radiotap.present() & RadioTap::RATE) != 0)
			{
				std::cout << "rate: " << (int)radiotap.rate() << std::endl;
			}

			if ((radiotap.present() & RadioTap::FLAGS) != 0)
			{
				std::cout << "flags: " << std::bitset<12>(radiotap.flags()) << std::endl;
			}
			
			if ((radiotap.present() & RadioTap::DBM_SIGNAL) != 0)
			{
				std::cout << "signal str: " << (int)radiotap.dbm_signal() << std::endl;
			}
		
		}

		
		if (pkt.pdu()->find_pdu<IP>())
		{
			const IP &ip = pdu.rfind_pdu<IP>(); // Find the IP layer
			
			std::cout << "IP: "<< ip.src_addr() << ':' << ip.dst_addr() << std::endl;
		}
		
		if (pkt.pdu()->find_pdu<TCP>())
		{
			const TCP &tcp = pdu.rfind_pdu<TCP>(); // Find the TCP layer
			
			std::cout << "TCP: " << tcp.sport() << ':' << tcp.dport() << std::endl;
		}
		
		std::cout << std::endl;
		count++;
	}
	
	gettimeofday(&tm2,NULL);
	
	std::cout << "Microseconds: "<< tm2.tv_usec - tm1.tv_usec << std::endl;
}
