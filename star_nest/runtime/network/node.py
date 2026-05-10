import socket
import json
import threading
import time

class JieDian:
    def __init__(self, duankou, jieduan_liebiao):
        self.duankou = duankou
        self.jieduan_liebiao = jieduan_liebiao
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', duankou))
        self.running = False
        self.thread = None
        self.xiaoxi_duilie = []

    def qidong(self):
        self.running = True
        self.thread = threading.Thread(target=self._jieshou_xunhuan, daemon=True)
        self.thread.start()

    def _jieshou_xunhuan(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(65535)
                xiaoxi = json.loads(data.decode('utf-8'))
                self.xiaoxi_duilie.append(xiaoxi)
            except:
                pass

    def jieshou_xiaoxi(self):
        if self.xiaoxi_duilie:
            return self.xiaoxi_duilie.pop(0)
        return None

    def guangbo(self, leixing, shuju):
        xiaoxi = {'leixing': leixing, 'shuju': shuju, 'laiyuan': self.duankou}
        data = json.dumps(xiaoxi).encode('utf-8')
        for dizhi in self.jieduan_liebiao:
            try:
                self.socket.sendto(data, (dizhi[0], dizhi[1]))
            except:
                pass

    def guangbo_gongju(self, shuju):
        self.guangbo('gongju', shuju)

    def guangbo_xiufu(self, shuju):
        self.guangbo('xiufu', shuju)

    def guangbo_zhongzi(self, shuju):
        self.guangbo('zhongzi', shuju)

    def tingzhi(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        self.socket.close()