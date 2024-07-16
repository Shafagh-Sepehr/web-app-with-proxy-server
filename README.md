## web server and http proxy server

three systems(e.g. virtual machine) should be nat together.
the web server will be deployed on a nginx server with wsgi gunicorn on vm 1.
http proxy will be run on vm 2.
put vm 1's ip address in http_proxy.py code.
set vm 2's ip and the port used in http_proxy.py into vm 1's browser proxy settings.
then search for vm 1's ip in vm 3's browser and the web page is shown.
the http proxy slightly changes the http packets so that the server could only see the http proxy server and not finding out about clients connected to the proxy server.
in case of more servers, the http proxy code could be modified to do a sort of load balancing.
