# Cheat Sheet for IEC 104 Protocol

## What is IEC 104?
IEC 60870-5-104 (IEC 104) is a telecontrol network protocol used in energy distribution systems for SCADA and station communication.

## IEC 104 Frame Formats
There are three different control field formats:
- **U-Format**
  - consists of an APCI only
  - is used for controlling the connection: start, stop, test frames
  - each U-Format frame is sent as an "ACT" = activation and must be responded with a "CON" confirmation 
- **S-Format**
  - consists of an APCI only
  - is only used for acknowledging I-Format frames
- **I-Format**
  - contains information (one or multiple ASDU)
  - includes Sent and Receive Sequence Numbers

## APDU
A whole IEC 104 frame is called an APDU (Application Protocol Data Unit)

An APDU consists of
  - an APCI (Application Protocol Control Information)
  - (if it is an I-Format): one or multiple ASDU (Application Service Data Unit)

**APDU = APCI + n * ASDU**

## APCI
An Apci consits of six bytes.

 - Byte 1: Start Byte (0x68)
 - Byte 2: Length of APDU (max. 253)
 - Byte 3 .. 6: Control field byte 1 .. 4

### U-Format

 - **Byte 1:** Bit 8: TESTFR con, Bit 7: TESTFR act, Bit 6: STOPDT con, Bit 5: STOPDT act, Bit 4: STARTDT con, Bit 3: STARTDT act, Bit 2: 1, Bit 1: 1
 - **Byte 2** Bit 8 .. Bit 1 : 0
 - **Byte 3** Bit 8 .. Bit 1 : 0
 - **Byte 4** Bit 8 .. Bit 1 : 0

Each U-Format frame can only have one function, e.g. STARTDT con = 0x0B, 0x00, 0x00, 0x00

Functions are
- **TESTFR act:** Send a test frame to check connection (heart beat)
- **TESTFR con:** Confirmation response to a test frame activation
- **STOPDT act:** Stop data transmission
- **STOPDT con:** Confirmation response of stop of data transmission
- **STARTDT act:** Start data transmission
- **STARTDT con:** Confirmation response of start data transmission


### S-Format

If there are no I-Format frames to be sent, an S-Format frame can be used to acknowledge received I-Format frames.

 - **Byte 1:** Bit 8 .. Bit 2: 0, Bit 1: 1
 - **Byte 2** Bit 8 .. Bit 1 : 0
 - **Byte 3** Bit 8 .. Bit 2: RSN (LSB) Bit 1 : 0
 - **Byte 4** Bit 8 .. Bit 1 :(MSB) RSN
 
 
 ### I-Format
Each I-Format frame consists of an APCI and one or multiple ASDU.
The I-Format APCI consists of two sequence numbers: RSN and SSN.

 - **Byte 1:** Bit 8 .. Bit 2: SSN (LSB), Bit 1: 0
 - **Byte 2** Bit 8 .. Bit 1 : (MSB) SSN
 - **Byte 3** Bit 8 .. Bit 2: RSN (LSB) Bit 1 : 0
 - **Byte 4** Bit 8 .. Bit 1 :(MSB) RSN
 

### Sequence Numbers
Each I-Format frame has a send sequence number (SSN) and a receive sequence number (RSN), which consist of 15 bits each: 0 .. 32767.

For each sent I-Format frame the SSN is incremented by one.
The RSN of the I-Format frame equals the last SSN (plus one) that was received by the communication instance sending the I-Format frame (RSN is one ahead).
A RSN acknowledges all frames before its number (RSN = 7 means 6 ... 0 are also acknwoledged.

If one communication instance does not send I-Format frames, it must use S-Format frames for acknowledgment.

Acknowledgment must be done within timeout t2.

### ASDU
An ASDU consists of a Data Unit Identifier and one or multiple Information Objects.
The structure is as follows:
1. Byte: Type Identification
2. Byte: Variable Structure Qualifier
3. Byte: Cause of Transmission
4. Byte: Originator Address
5. Byte: Common Address of ASDU
6. Byte: Common Address of ASDU
7. Byte: Information Object Address
8. Byte: Infromation Object Address
9. Byte: Infromation Object Address
10. Byte ... : Set of Information Elements (different per Type Identification)

#### Type Identification (Type ID)
The data type of the Information Object.

Some important ones:

-	1:   M_SP_NA_1, single point information
-	3:   M_DP_NA_1, double point information
-	9:   M_ME_NA_1, measured value normalized
-	11:  M_ME_NB_1, measured value scaled
-	13:  M_ME_NC_1, measured value float
-	15:  M_IT_NA_1, integrated total
-	30:  M_SP_TB_1, signle point information with time tag
-	31:  M_DP_TB_1, double point information with time tag
-	34:  M_ME_TD_1, measured value normalized with time tag
-	35:  M_ME_TE_1, measured value scaled with time tag
-	36:  M_ME_TF_1, measured value float with time tag
-	37:  M_IT_TB_1, integrated total with time tag
-	45:  C_SC_NA_1, single command
-	46:  C_DC_NA_1, double command
-	47:  C_RC_NA_1, regulating step command
-	100: C_IC_NA_1, interrogation command
-	105: C_RP_NA_1, reset process command
// tba

#### Variable Structure Qualifier
Consists of 
Bit 8: SQ bit (Sequence)
Bit 7 .. 1: Number

SQ=0: contains only one Info Element or combination of info elements of same type, each with its own Info Object Address
SQ=1: sequence of single (not continuous) Info Objects. The Info Object Address is the first object's address, the next are incremented by one.

#### Cause of Transmission
This Byte contains a test bit (Bit 8), Positive/Negative bit (Bit 7) and Cause of Transmission number as follows.

- 0:  "UNDEFINED",
-	1:  "per/cyc",
-	2:  "back",
-	3:  "spont",
-	4:  "init",
-	5:  "req",
-	6:  "act",
-	7:  "actcon",
-	8:  "deact",
-	9:  "deactcon",
-	10: "actterm",
-	11: "retrem",
-	12: "retloc",
-	13: "file",

-	20: "inrogen",
-	21: "inro1",
-	22: "inro2",
-	23: "inro3",
	// ...

-	37: "reqcogen",
-	38: "reqco1",
-	39: "reqco2",
	// ...

-	44: "unknown TypeID",
-	45: "unknown Cause Of TX",
-	46: "unknown CASDU",
-	47: "unknown IOA",

#### Common Address of ASDU (CASDU)
Two Bytes: Is used as a substation reference number.
Each station has its unique CASDU

#### Info Object Address (IOA)
Three Bytes: References the Information Object
Each Info Object has its unique IOA.

### Timeouts
- **t0** TCP SYN timeout, default 30 s
- **t1** Max response time for any frames, default 15 s
- **t2** Max time for acknowledgments, default 10 s
- **t3** Max idle time, triggers test frames, default 20 s

### TCP Port
TCP Port is 2404
