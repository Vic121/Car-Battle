#!/usr/bin/env python
"""
Simple client to get some stats from memcached.

Using some of the *undocumented* (and not guaranteed to remain
working) features you can get a list of keys.

memcached (127.0.0.1:11211): stats
STAT pid 3228
STAT uptime 45498
STAT time 1245270511
STAT version 1.2.2
...

memcached (127.0.0.1:11211): stats items
STAT items:6:number 1
STAT items:6:age 64
STAT items:19:number 1
STAT items:19:age 66
END

memcached (127.0.0.1:11211): stats slabs
STAT 6:chunk_size 252
STAT 6:chunks_per_page 4161
STAT 6:total_pages 1
...
STAT 19:chunk_size 4648
STAT 19:chunks_per_page 225
STAT 19:total_pages 1
...
STAT active_slabs 2
STAT total_malloced 2094372
END

memcached (127.0.0.1:11211): stats cachedump 6 50
ITEM paste|searchreplace|table|safari|fullscreen|directionality|en|advanced [116 b; 1245270494 s]
END

memcached (127.0.0.1:11211): stats cachedump 19 50
ITEM contentmanager:9:1:content [3940 b; 1245270492 s]
END

"""

import memcache

PROMPT = "memcached (%s): "

MESSAGE_ENDINGS = ["END", "ERROR", "SERVER_ERROR", "CLIENT_ERROR", "OK", "DELETED", "NOT FOUND"]

# These (can) return binary data. Use a proper client to get those ;-)
UNSUPPORTED_COMMANDS = ["get", "gets", "set", "add", "replace",
                        "append", "prepend", "cas", "incr", "decr"]


def message_ends(command, output):
    if command == "version" and output != "":
        return True
    else:
        if output == "":
            return False
        return output.split()[0] in MESSAGE_ENDINGS


def repl(cache_host):
    h = memcache._Host(cache_host)
    h.connect()

    while True:
        try:
            command = str(raw_input(PROMPT % cache_host))
        except EOFError:
            print "bye"
            break
        if not command:
            continue
        if command.split()[0] in UNSUPPORTED_COMMANDS:
            print "Not supported"
            continue
        if command == "quit":
            break
        h.send_cmd(command)
        l = "";
        while not message_ends(command, l):
            l = h.readline()
            print l

    h.close_socket()


if __name__ == "__main__":
    import sys
    import re

    try:
        # Use with django project
        from settings import CACHE_BACKEND

        if not CACHE_BACKEND.startswith("memcached://"):
            print "You have not configured memcached as your django cache backend"
            sys.exit(1)
        else:
            m = re.search(r"//(.+:\d+)", CACHE_BACKEND)
            cache_host = m.group(1)
            repl(cache_host)
    except (ImportError, KeyError):
        # Try to use the first argument as cache_host
        try:
            repl(sys.argv[1])
        except IndexError:
            print
            print "Usage: %s host:port" % sys.argv[0]
            sys.exit(1)
