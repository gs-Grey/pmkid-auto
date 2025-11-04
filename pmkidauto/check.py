#-*- coding: latin1 -*-
from pbkdf2 import PBKDF2
from hashlib import sha1
import binascii
import hmac

class Check:
    def __init__(self, hash_line):
        hcl = hash_line.split('*')
        self.pmkid = (hcl[2])
        self.mac_ap = (hcl[3])
        self.mac_cli = (hcl[4])
        self.essid = binascii.unhexlify((hcl[5]))
        # The data for HMAC is the string "PMK Name" followed by the two MAC addresses
        self._data = b"PMK Name" + binascii.a2b_hex(self.mac_ap) + binascii.a2b_hex(self.mac_cli)

    def check_pass(self, passwd):
        # 1. Calculate the 32-byte Pairwise Master Key (PMK) using PBKDF2
        pmk = PBKDF2(passwd.encode('latin1'), self.essid, iterations=4096).read(32)

        # 2. Calculate the PMKID using the standard HMAC-SHA1 method
        # The key is the PMK, and the data is self._data
        calculated_pmkid = hmac.new(pmk, self._data, sha1).hexdigest()

        # 3. Compare the result with the captured PMKID. The hash contains the first 16 bytes (32 hex chars).
        return self.pmkid == calculated_pmkid[:32]
