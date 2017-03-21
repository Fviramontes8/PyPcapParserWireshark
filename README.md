# PyPcapParserWireshark
Here is code for a Pcap parcer taking pcap files outputted by wireshark in addition to some test code
Wireshark has the capability to export .pcap files every second if configured correctly, we are using this feature to our 
  advantage by reading each file that is exported and seeing what information these packet have to offer. We want to see number 
  of users, bits from users A to B and B to A, the services they are using, and timestamps for statistical analysis.
