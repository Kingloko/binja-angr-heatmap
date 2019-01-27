import angr
import socket

HOST = '127.0.0.1'
PORT = 31337

class HeatMapExplorer(angr.exploration_techniques.ExplorationTechnique):
   
    def setup(self, simgr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    def __del__(self):
        print("HME closed")
        self.socket.shutdown(1)
        self.socket.close()

    def filter(self, simgr,state, **kwargs):
        for addr in state.block().instruction_addrs:
            str_addr = '{:-08X}'.format(addr)
            self.socket.sendall(str_addr.encode())

        return simgr.filter(state, **kwargs) 
