# PyPcapParserWireshark [DEPRECATED]
Code for a Pcap parser that takes pcap files produced by wireshark and analyzes meaningful statistical data in C++.
The C++ code uses the libtins library to analyze packets and the libpq library to interface with a PostgreSQL database.
The Python code uses the psychopg2 library to interface with a PostgreSQL database.
The time_series python files take the data from the database and fit them into a Gaussian Process Regressor to make a prediction of the network's future state.
