import re
import socketserver
import sqlite3
import struct

from openote import settings

REBIND_CACHE = settings.REBIND_CACHE
ROOT_DOMAIN = settings.ROOT_DOMAIN
LOCAL_IP = settings.LOCAL_IP
DB = settings.DATABASES['default']["NAME"]


def is_ip(ip):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return ip
    else:
        return '3.3.3.3'


class DNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author,
         self.addition) = struct.unpack('>HHHHHH', data[0:12])
        self.query_type, self.query_name, self.query_bytes = self._get_query(
            data[12:])
        self.answer_bytes = None

    def _get_query(self, data):
        i = 1
        name = ''
        while True:
            d = data[i]
            if d == 0:
                break
            if d < 32:
                name = name + '.'
            else:
                name = name + chr(d)
            i = i + 1
        query_bytes = data[0:i + 1]
        (_type, classify) = struct.unpack('>HH', data[i + 1:i + 5])
        query_bytes += struct.pack('>HH', _type, classify)
        return _type, name, query_bytes

    def _get_answer_getbytes(self, ip):
        ttl = 0
        answer_bytes = struct.pack('>HHHLH', 49164, 1, 1, ttl, 4)
        s = ip.split('.')
        answer_bytes = answer_bytes + struct.pack('BBBB', int(s[0]), int(s[1]),
                                                  int(s[2]), int(s[3]))
        return answer_bytes

    def get_query_domain(self):
        return self.query_name

    def setip(self, ip):
        self.answer_bytes = self._get_answer_getbytes(ip)

    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, 33152, self.quests, 1,
                          self.author, self.addition)
        res += self.query_bytes + self.answer_bytes
        return res


class SQLiteDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB, check_same_thread=False)

    def exec_sql(self, sql, *arg):
        result = []
        cursor = self.conn.cursor()
        rows = cursor.execute(sql, arg)
        for v in rows:
            result.append(v)
        cursor.close()
        self.conn.commit()


class DNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        dns = DNSFrame(data)
        socket_u = self.request[1]
        a_map = DNSServer.A_map
        if dns.query_type == 1:
            domain = dns.get_query_domain()

            ip = '1.1.1.1'  # 默认解析结果是1.1.1.1
            pre_data = domain.replace('.' + ROOT_DOMAIN, '')

            if pre_data in a_map:
                # 自定义的dns记录，保留着
                ip = a_map[pre_data]
            elif pre_data.count('.') == 3:
                # 10.11.11.11.test.com 即解析为 10.11.11.11
                ip = is_ip(pre_data)
            elif pre_data.count('.') == 7:
                # 114.114.114.114.10.11.11.11.test.com 循环解析，例如第一次解析结果为114.114.114.114，第二次解析结果为10.11.11.11
                tmp = pre_data.split('.')
                ip_1 = '.'.join(tmp[0:4])
                ip_2 = '.'.join(tmp[4:])
                if tmp in REBIND_CACHE:
                    ip = is_ip(ip_2)
                    REBIND_CACHE.remove(tmp)
                else:
                    REBIND_CACHE.append(tmp)
                    ip = is_ip(ip_1)

            if ROOT_DOMAIN in domain:
                # name = domain.replace('.' + ROOT_DOMAIN, '')
                # log = DNSLog(count=domain, source=ip)
                # log.save()
                sql = "INSERT INTO home_dnslog (content, source, time) \
                                                        VALUES(?, ?, datetime(CURRENT_TIMESTAMP, 'UTC'))"
                sqlite_db = SQLiteDB()
                sqlite_db.exec_sql(sql, pre_data, self.client_address[0])
            dns.setip(ip)
            print('[DNS] %s: %s-->%s' % (self.client_address[0], pre_data, ip))
            socket_u.sendto(dns.getbytes(), self.client_address)
        else:
            socket_u.sendto(data, self.client_address)


class DNSServer:
    def __init__(self):
        DNSServer.A_map = {}

    @staticmethod
    def add_record(name, ip):
        DNSServer.A_map[name] = ip

    @staticmethod
    def start():
        server = socketserver.UDPServer(("0.0.0.0", 53), DNSUDPHandler)
        server.serve_forever()


def start_dns():
    server = DNSServer()
    try:
        server.start()
        print("[+] Dns server started.")
    except OSError:
        print("[!] Port has been used.")

# if __name__ == "__main__":
#
#     """
#     standalone
#     """
#     ROOT_DOMAIN = "dns.example.com"
#     LOCAL_IP = "123.123.123.123"
#
#     if LOCAL_IP == '':
#         sock = socket.create_connection(('ns1.dnspod.net', 6666), 20)
#         ip = sock.recv(16)
#         sock.close()
#         LOCAL_IP = ip
#     d = DNSServer()
#     d.start()
