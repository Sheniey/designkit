
from validators import domain as validate_domain, hostname as validate_hostname

validate_domain()
validate_hostname()

class Hostname:
    def __init__(self, hostname: str):
        self.hostname = hostname

    def __str__(self):
        return self.hostname
