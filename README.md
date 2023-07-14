# omnisDEC-rewrite
omnisDEC - Monitor an infinite amount of internet streams for SAME (Specific Area Message Encoding) Headers. Name came from the Latin word omnis which means all and dec which is short for decoder.

# How It Works
Theoretically, omnisDEC monitors an infinite amount of internet streams for SAME headers. These streams may be NOAA Weather Radio streams, "listen live" streams of broadcast radio stations located in the United States, or an internet radio station with Emergency Alert System or SAME equipment that can receive and relay SAME Alerts.

# It is Broken
Yup, it doesn’t work. It is a concept. If you would like to fix it, feel free to! 

# What is SAME?
SAME, short for Specific Area Message Encoding is a method of digital message transfer using anolog (or digital) means. It uses audio frequency-shift keying to transmit digital data at a baud rate of 520.83333 bits/second. A SAME decoder takes a SAME header and decodes it into an ASCII text string. Here is an example of a decoded header:

ZCZC-WXR-SVR-027007+0030-1950022-KFGF/NWS-

You can use another program called an interpreter to make sense of this header. Running this program through an interpreter gives us this output which can be recognized:

The National Weather Service has issued a Severe Thunderstorm Warning for Beltrami, MN beginning at 7:22 PM and ending at 7:52 PM. Message from KFGF/NWS.
