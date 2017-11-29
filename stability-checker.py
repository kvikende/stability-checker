#!/usr/bin/env python

"""stability-checker.py: Checks whether the Internet connection is up, and logs any failures."""

__license__ = "GPL v3"

import datetime
import time
import socket
import signal
import random

OUTPUT_FILENAME = "output.log"
SUCCESS_SLEEP_PERIOD = 2  # in seconds
FAIL_SLEEP_PERIOD = 2  # in seconds


# List of (ip, port) to shuffle through when testing connectivity.
SERVERS = [
    ("8.8.8.8", 53),  # Google DNS.
    ("8.8.4.4", 53),   # Alt. Google DNS.
    ("91.239.100.100", 53),  # https://blog.uncensoreddns.org/
    ("89.233.43.71", 53),  # https://blog.uncensoreddns.org/
    ("84.200.69.80", 53),  # https://dns.watch/index
    ("84.200.70.40", 53),  # https://dns.watch/index
    ("208.67.222.222", 53),  # OpenDNS
    ("208.67.220.220", 53),  # OpenDNS
    ("199.85.126.10", 53),  # Norton Connectsafe
    ("199.85.127.10", 53),  # Norton Connectsafe
    ("199.85.126.20", 53),  # Norton Connectsafe
    ("199.85.127.20", 53),  # Norton Connectsafe
    ("199.85.126.30", 53),  # Norton Connectsafe
    ("199.85.127.30", 53),  # Norton Connectsafe
]


class ShutdownHandler:
    gotten_shutdown_signal = False

    def __init__(self):
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

    def _shutdown_handler(self, _, __):
        self.gotten_shutdown_signal = True


def is_internet_up_random_server(max_retries=2):
    previous_server = None
    tries = 0

    while tries < max_retries:
        server = random.choice(SERVERS)

        while server == previous_server:
            server = random.choice(SERVERS)

        host = server[0]
        port = server[1]

        is_connected = test_connection(host=host, port=port)

        if is_connected:
            return True
        else:
            print("Connection didn't work for host " + host)
            previous_server = server
            tries += 1

    return False


def test_connection(host="8.8.8.8", port=53, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(timeout)

    try:
        s.connect((host, port))
        return True
    except socket.error as ex:
        print("Socket error: %s" % ex)
        return False
    finally:
        s.close()


def write_logfile(line, print_to_console=True):
    """Append provided line to file. Optionally print to console.

    :param line: Line to append to file.
    :param print_to_console: Whether to also print to console.
    :return: None.
    """
    timestamp = datetime.datetime.utcnow().isoformat(" ") + "+00:00"  # Must add this because isoformat doesnt include timezone.
    txt = timestamp + ": " + line

    if print_to_console:
        print(txt)

    with open(OUTPUT_FILENAME, "a+") as f:
        f.write(txt + "\n")


def main():
    shutdown_handler = ShutdownHandler()
    write_logfile("Is started")
    last_faulty_connection = None

    while True:
        is_connected = is_internet_up_random_server()
        if is_connected:
            if last_faulty_connection is not None:
                write_logfile("Connection is up again.")
                current_time = datetime.datetime.now()
                diff = current_time - last_faulty_connection
                write_logfile("Was disconnected for " + str(diff))
                last_faulty_connection = None

            time.sleep(SUCCESS_SLEEP_PERIOD)
        else:
            if last_faulty_connection is None:
                write_logfile("Connection is down...")
                last_faulty_connection = datetime.datetime.now()
            time.sleep(FAIL_SLEEP_PERIOD)

        if shutdown_handler.gotten_shutdown_signal:
            break

    write_logfile("Is terminating")


if __name__ == '__main__':
    main()
