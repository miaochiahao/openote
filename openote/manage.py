#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import socket
import sys
import threading

sys.path.append(os.path.curdir)
from dns_server import start_dns


# Django会开启两个线程执行 因此这里增加的dns server会启动两次，为了避免这一情况
# 这里添加了端口判断 如果端口未占用再开启新线程，保证dns服务器只启动一次 其中的函数也执行一次
def is_port_used():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", 53))
        return False
    except OSError:
        return True
    finally:
        s.close()


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openote.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        t = threading.Thread(target=start_dns, args=())
        t.start()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
