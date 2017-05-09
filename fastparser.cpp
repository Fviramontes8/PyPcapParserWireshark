#include <tins/tins.h>
#include <iostream>
#include <bitset>
#include <stddef.h>

using namespace Tins;

size_t counter(0);

bool count_packets(const PDU &pdu)
{
	counter ++;
	const RadioTap &radiotap = pdu.rfind_pdu<RadioTap>(); // Find the RadioTap layer



	if ((radiotap.present() & RadioTap::CHANNEL) != 0)
	{
		std::cout << "frequency: " << (int)radiotap.channel_freq() << std::endl;
		std::cout << "type: " << std::bitset<32>(radiotap.channel_type()) << std::endl;
	}
	if ((radiotap.present() & RadioTap::RATE) != 0)
	{
		std::cout << "rate: " << (int)radiotap.rate()/2 << std::endl;
	}

	if ((radiotap.present() & RadioTap::FLAGS) != 0)
	{
		std::cout << "flags: " << std::bitset<32>(radiotap.flags()) << std::endl;
	}
	
	if ((radiotap.present() & RadioTap::DBM_SIGNAL) != 0)
	{
		std::cout << "signal str: " << (int)radiotap.dbm_signal() << std::endl;
	}
	else 
	{
		std::cout << "No signal strength?" << std::endl;
	}
	
	const IP &ip = pdu.rfind_pdu<IP>(); // Find the IP layer
    const TCP &tcp = pdu.rfind_pdu<TCP>(); // Find the TCP layer
    std::cout << ip.src_addr() << ':' << tcp.sport() << " -> " 
              << ip.dst_addr() << ':' << tcp.dport() << std::endl;
	
	return true;
}

int main(int argc, char* argv[])
{
	//RadioTap radio = RadioTap() / Dot11Beacon();
    //PacketWriter writer("output.pcap", PacketWriter::RADIOTAP);
    //writer.write(radio);
	FileSniffer sniffer(argv[1]);
	sniffer.sniff_loop(count_packets);
	std::cout << "There are " << counter << " packets in the pcap file\n";
}
