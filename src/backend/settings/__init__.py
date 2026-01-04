from .base import *
from .security import *
from .apps_config import *
from .logging_config import *

if DEBUG:
    import socket

    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
            "127.0.0.1",
            "10.0.2.2",
        ]
    except Exception:
        INTERNAL_IPS = ["127.0.0.1"]

from pytz import timezone as global_timezone

global_timezone(TIME_ZONE)
