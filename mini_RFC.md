# Reliable UDP File Transfer Protocol 
Mini RFC Documentation  
NSCOM01 – Machine Project  

---

## a. Introduction
This document describes the implementation of a reliable UDP file transfer system developed.

UDP is a connectionless and unreliable transport protocol. It does not guarantee:
- Packet delivery
- Packet ordering
- Duplicate prevention
- Congestion control

To address these limitations, this implementation introduces reliability mechanisms such as:

- Three-way handshake for connection establishment
- Stop-and-Wait Automatic Repeat reQuest (ARQ)
- Sequence numbers
- Acknowledgment (ACK) packets
- Retransmission on timeout
- Graceful connection termination using FIN handshake

The protocol supports reliable file upload and download between a client and server.

---

## b. Protocol Overview
The system uses a client-server architecture where:

- The **client** initiates connections, requests downloads/uploads, and terminates connections.
- The **server** listens for connections, handles file requests, and responds reliably.

The protocol operates in three major phases:

### 1. Connection Establishment

Client initiates connection using a three-way handshake:

1. Client → Server: `SYN`
2. Server → Client: `SYN-ACK`
3. Client enters `CLIENT_ESTABLISHED`
4. Server enters `SERVER_ESTABLISHED`

This ensures both parties are synchronized before file transfer begins.

---

### 2. Data Transfer Phase

File transfer uses Stop-and-Wait ARQ:

1. Sender sends a `DATA` packet with sequence number.
2. Receiver replies with `ACK`.
3. Sender waits for ACK before sending the next packet.
4. If timeout occurs, packet is retransmitted.

This guarantees:
- Ordered delivery
- No packet loss (via retransmission)
- No duplication (via sequence tracking)

---

### 3. Connection Termination

Graceful shutdown uses a FIN handshake:

Client:
1. Sends `FIN`
2. Waits for `FIN-ACK`
3. Sends final `ACK`
4. Closes socket

Server:
1. Receives `FIN`
2. Sends `FIN-ACK`
3. Waits for final ACK
4. Returns to `SERVER_LISTEN`

---
### 2.1 Swimlane Diagrams and Protocol Message Exchange Descriptions

This section illustrates the sequence of message exchanges between the Client and Server during different phases of the protocol. Time flows from top to bottom.

---

#### A. Connection Establishment
```
CLIENT                                     SERVER
  |                                           |
  |--- SYN ---------------------------------->|  
  |                                           |  
  |<-- SYN-ACK -------------------------------|
  |                                           |  
  |--- SYN ---------------------------------->| 
```
Client State: STATE_ESTABLISHED  
Server State: STATE_ESTABLISHED  

Description:

1. The Client initiates the connection by sending a SYN packet.
2. The Server responds with a SYN-ACK packet.
3. The Client transitions to STATE_ESTABLISHED after receiving SYN-ACK.
4. The Server transitions to STATE_ESTABLISHED after processing the final ACK.

---

#### B. File Download 
```
CLIENT                                     SERVER
  |                                           |
  |--- REQUEST(GET filename)----------------->|  
  |                                           |  
  |<-- DATA (seq=0)---------------------------|
  |                                           |  
  |--- ACK (0) ------------------------------>| 
  |                                           |  
  |<-- DATA (seq=1)---------------------------|
  |                                           |  
  |--- ACK (1) ------------------------------>| 
  |                                           |  
    ...
  |<-- DATA (seq=n)---------------------------|
  |                                           |  
  |--- ACK (n) ------------------------------>|  
```  
Description:

1. The Client sends a GET request specifying the filename.
2. The Server reads the file and sends DATA packets sequentially.
3. After each DATA packet, the Client sends an ACK.
4. Stop-and-Wait ARQ ensures only one unacknowledged packet exists at a time.
5. An empty DATA payload signals end-of-file (EOF).

---

#### B. File Upload 
```
CLIENT                                     SERVER
  |                                           |
  |--- REQUEST(PUT filename)----------------->|  
  |                                           |  
  |<-- DATA (seq=0)---------------------------|
  |                                           |  
  |--- ACK (0) ------------------------------>| 
  |                                           |  
  |<-- DATA (seq=1)---------------------------|
  |                                           |  
  |--- ACK (1) ------------------------------>| 
  |                                           |  
    ...
  |<-- DATA (seq=n, empty payload)------------|
  |                                           |  
  |--- ACK (n) ------------------------------>|  
```
Description:

1. The Client sends a PUT request with the filename.
2. The Client transmits file chunks as DATA packets.
3. The Server acknowledges each packet.
4. An empty DATA payload indicates EOF.
5. The Server finalizes the file after receiving the last packet.

---

#### D. Connection Termination 
```
CLIENT                                     SERVER
  |                                           |
  |--- FIN ---------------------------------->|  
  |                                           |  
  |<-- FIN-ACK -------------------------------|
  |                                           |  
  |--- ACK ---------------------------------->| 
```

Client State: STATE_CLOSED  
Server State: STATE_LISTEN  

Description:

1. The Client initiates termination by sending FIN.
2. The Server replies with an acknowledgment.
3. The Client sends a final ACK and closes the socket.
4. The Server returns to STATE_LISTEN and waits for new connections.

---

## c. Packet Message Formats

### Header Structure

Each packet contains:

| Field | Description |
|-------|------------|
| Type | Packet type identifier |
| Sequence Number | Integer identifying packet order |
| Payload Length | Length of data |
| Payload | File data (if applicable) |

---

### Message Types

| Type | Description |
|------|------------|
| SYN | Initiates connection |
| SYN-ACK | Acknowledges SYN |
| DATA | File data packet |
| ACK | Acknowledgment for DATA |
| FIN | Requests connection termination |
| FIN-ACK | Acknowledges FIN |
| ERROR | Indicates error (e.g., file not found) |

## d. State Machines (Transition Diagram)
This section describes the actual states implemented in the client and server code.

---
### Client State Machine

The client defines two states:

- `STATE_CLOSED`
- `STATE_ESTABLISHED`

#### State Transitions

1. **Initial State:** `STATE_CLOSED`

2. When user selects "Connect":
   - Client sends `SYN`
   - Waits for `SYN-ACK`
   - Sends final `ACK`
   - Transitions to `STATE_ESTABLISHED`

3. While in `STATE_ESTABLISHED`:
   - Client may send DOWNLOAD (`GET`) request
   - Client may send UPLOAD (`PUT`) request
   - Client may initiate connection termination

4. When user selects "Exit":
   - Client sends `FIN`
   - Waits for `FIN-ACK`
   - Sends final `ACK`
   - Returns to `STATE_CLOSED`
   - Socket closes

---

### Server State Machine

The server defines three states:

- `STATE_LISTEN`
- `STATE_SYN_RCVD`
- `STATE_ESTABLISHED`

#### State Descriptions

`STATE_LISTEN`
- Server waits for incoming `SYN` packet.
- Upon receiving `SYN`:
  - Sends `SYN-ACK`
  - Transitions to `STATE_SYN_RCVD`

`STATE_SYN_RCVD`
- Server waits for final `ACK` from client.
- Upon receiving `ACK`:
  - Handshake is complete
  - Transitions to `STATE_ESTABLISHED`

`STATE_ESTABLISHED`
- Server processes file requests (`REQUEST` packets):
  - `GET` → Calls `send_file()`
  - `PUT` → Calls `receive_file()`
- Upon receiving `FIN`:
  - Sends `FIN-ACK`
  - Transitions back to `STATE_LISTEN`

The server does not maintain a separate FIN_WAIT state.
It immediately returns to listening after acknowledging the FIN packet.

---

## e. Reliability Mechanisms

### 1. Stop-and-Wait ARQ

Only one packet is sent at a time.  
Sender waits for acknowledgment before sending the next packet.

---

### 2. Sequence Numbers

Each DATA packet includes a sequence number.

The receiver:
- Accepts only the expected sequence
- Ignores duplicates
- Sends ACK for received sequence

---

### 3. Timeout and Retransmission

If ACK is not received within a timeout period:

- Packet is retransmitted
- Retry counter increases
- Connection fails if max retries exceeded

---

### 4. Duplicate Handling

Duplicate packets are ignored using sequence tracking.

---

## f. Error Handling

The protocol handles the following errors:

### File Not Found
Server sends ERROR packet if requested file does not exist.

### Timeout
Sender retransmits packet if ACK not received.

### Unexpected Packet
Packets received in wrong state are ignored.

### Max Retries Exceeded
Connection is terminated if retransmissions fail.

---

## g. File Transfer Operations

### Download Operation

1. Client sends DOWNLOAD request.
2. Server reads file in chunks.
3. Server sends DATA packets sequentially.
4. Client acknowledges each packet.
5. EOF indicated by empty DATA payload.

---

### Upload Operation

1. Client sends UPLOAD request.
2. Client reads file in chunks.
3. Client sends DATA packets sequentially.
4. Server acknowledges each packet.
5. EOF indicated by empty DATA payload.

---

## h. End-of-File Signaling

End-of-file (EOF) is signaled by sending a `DATA` packet with:

- Valid sequence number
- Empty payload (length = 0)

Upon receiving this:

- Receiver finalizes file writing
- Transfer loop terminates
- Connection remains established unless FIN is sent

---
