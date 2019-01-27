import socket 
import binaryninja as binja

class RGB(object):
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue 

class InstructionHeatMap(object):
    
    def __init__(self):
        self.instr_dict = {}
    
    def increment_instruction(self, inst_addr):
        try:
            self.instr_dict[inst_addr] += 1
        except KeyError:
            self.instr_dict[inst_addr] = 1 

    def get_normalized_value(self, inst_addr):
        try: 
            inst_value = self.instr_dict[inst_addr]
        except KeyError:
            return 0
        min_val = min(self.instr_dict.values())
        max_val = max(self.instr_dict.values())
        if min_val == max_val:
            return 1
        return ( (inst_value - min_val) / (max_val - min_val) )


RED =RGB(255, 0, 0)
YELLOW = RGB(255, 211, 0)
GREEN = RGB(0, 255, 0)
CYAN = RGB(0, 255, 255)
BLUE = RGB(0, 0, 255)



def get_color_for_normalized_value(value):
    #placed in order of gradient
    colors = [BLUE, CYAN, GREEN, YELLOW, RED]
    if value == 1:
        return colors[-1]
    elif value == 0:
        return colors[0]
    value = (value * len(colors)) -1
    
    idx1 = int(value)
    idx2 = idx1+1
    fractBetween = value - idx1 

    

    r_value = colors[idx2].red - colors[idx1].red * fractBetween + colors[idx1].red
    g_value = colors[idx2].green - colors[idx1].green * fractBetween + colors[idx1].green
    b_value = colors[idx2].blue - colors[idx1].blue * fractBetween + colors[idx1].blue

    return RGB(r_value, g_value, b_value)


class ColoringThread(binja.plugin.BackgroundTaskThread):
    def __init__(self, bv):
        binja.plugin.BackgroundTaskThread.__init__(self, "Making a heat map!", True)
        self.bv = bv

    def run(self):
        ihm = InstructionHeatMap()
        self.ihm = ihm
        HOST = '127.0.0.1'
        PORT = 31337
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(8)
                    if not data:
                       break 
                    data.decode()
                    try:
                        data = int(data, 16)
                    except ValueError:
                        continue
                    print(">>>{}".format(hex(data)))
                    ihm.increment_instruction(data)
                    for addr in ihm.instr_dict.keys():
                        highlight_color = get_color_for_normalized_value(ihm.get_normalized_value(addr))
                        bv_highlight = binja.highlight.HighlightColor(red=int(highlight_color.red),
                                                                      green = int(highlight_color.green), 
                                                                      blue = int(highlight_color.blue))
                        self.set_highlight(addr, bv_highlight) 
        print("Connection Closed")


    def set_highlight(self, addr, bv_highlight):
        fncs = self.bv.get_functions_containing(addr)
        if not fncs:
            return 
        for fnc in fncs:
            fnc.set_auto_instr_highlight(addr, bv_highlight)

    def clear_highlights(self):
        clear_highlight = binja.highlight.HighlightColor(None)
        for addr in self.ihm.instr_dict.keys():
            self.set_highlight(addr, clear_highlight)


def kickoff_coloring_thread(bv):
    ct = ColoringThread(bv)
    coloring_threads.append(ct)
    ct.start()

def clear_binja_highlights(bv):
    ct = coloring_threads[-1]
    ct.clear_highlights()

coloring_threads = []        
binja.PluginCommand.register("binja heat map", "heatmap for binja instructions",
        kickoff_coloring_thread)

binja.PluginCommand.register("Clear Heat Map", "heatmap cleared", clear_binja_highlights)
