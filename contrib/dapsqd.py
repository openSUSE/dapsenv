import job
import const
import logging
import logging.config
import socketserver
import json

logging.getLogger().addHandler(logging.NullHandler())
logging.config.dictConfig(const.DEFAULT_LOGGING_DICT)
log = logging.getLogger('test')


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = json.loads(self.request.recv(1024).strip())
        success = jq.push(job.Build(self.data['repo'],
                                    self.data['ref'],
                                    self.data['cmd']),
                          self.data['priority'])
        if success is not False:
            self.request.sendall('OK'.encode('utf-8'))
        else:
            self.request.sendall('NOT OK'.encode('utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    jq = job.JobQueue(7)

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.timeout = 1
        while True:
            server.handle_request()
            jq.run()
            jq.log_info()
