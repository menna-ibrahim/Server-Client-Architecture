<h1 align="center" id="title">Server-Client Architecture</h1>

## Description
Python program that acts as server that can accept http requests and send responses using
socket programming and multithreaded techniques and support concurrent, persistent
and non-persistent connection for HTTP 1.0 and HTTP 1.1 format.

## Web Server
Can accept multiple requests and handle them in parallel by using Threading library, the
request can be POST or GET where the client request file stored locally or want to
post/upload file to the server, for simplicity the mandatory fields of the Response are
implemented, the server also decide the timeout dynamically for the connection to be alive
without responding any requests from that client.

## Client
For testing the server-client architecture of the program, simple client module has been
implemented to communicate with the server starting from connection establishing,
requesting/uploading files and connection closing.
It starts by reading some operation/commands from text file and after parsing input text,
perform connection establishing and start communication with the server.

## HTTP 1.1
The server also can handle HTTP requests that supports persistent connections where the
server leave the connection open for a while before closing it, that timeout the server
compute it dynamically based on the congestion and number of active connections, also the
server can support pipelining where the client can send multiple requests for data or files
upload and the server handle it in order on the same connection.

## Cache
Simple cache technique has been implemented to reduce the load over the server side,
where on the client side there is a cache file to record the requests done by that client so
any repeated requests at the same runtime the program just skip it and assume the that
request has been done already.

