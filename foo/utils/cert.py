# -*- encoding: utf-8 -*-
#@File    :   cert.py
#@Time    :   2024/09/04 21:38:40
#@Author  :   Jianping Zhang 
#@Version :   1.0
#@Contact :   Jianping.zhang_2@nxp.com
#@Brief   :   


"""
    This file depend on the the offical SPSDK lib, please install the SPSDK first!
"""

import contextlib
import datetime
import logging
import os
import struct
import sys
from dataclasses import dataclass
from time import sleep
from typing import Callable, Iterator, List, Optional


from OpenSSL.crypto import X509
from OpenSSL.crypto import (FILETYPE_ASN1,FILETYPE_PEM)
from OpenSSL import crypto

# from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
import yaml,json
import struct
from cryptography.hazmat.primitives.hashes import *



def export_pub_from_der(der_cert):

    assert os.path.exists(der_cert)
    with open(der_cert, "rb") as der:
        der_data = der.read()
    logging.info(der_cert)

    x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, der_data)
    # pem_cert = der_cert[0: -4] + "_.pem"
    # logging.info(pem_cert)
    pem_cert_data = crypto.dump_certificate(crypto.FILETYPE_PEM,x509)
    # with open(pem_cert, "wb") as pem:
    #     pem.write(pem_cert_data)

    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, pem_cert_data)
    pub_key = der_cert[0: -4] + "_.pub"
    
    logging.info(pub_key)
    pubkey_data = crypto.dump_publickey(crypto.FILETYPE_PEM, x509.get_pubkey()).decode("utf-8")
    with open(pub_key, "w") as pub:
        pub.write(pubkey_data)
    return pub_key

def export_pem_from_cryptpem(crypt_pem, passoword=b'my_pass_phrase'):
    assert os.path.exists(crypt_pem)
    with open(crypt_pem, "rb") as cryptpem:
        cryptpem_data = cryptpem.read()
    logging.info(crypt_pem)

    pkey  = crypto.load_privatekey(crypto.FILETYPE_PEM, cryptpem_data, passphrase=passoword)
    prv_key_data = crypto.dump_privatekey(crypto.FILETYPE_PEM,pkey)

    prv_key = crypt_pem[0: -4] + "_.key"
    logging.info(prv_key)
    with open(prv_key, "wb") as prv:
        prv.write(prv_key_data)
    
    return prv_key



if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format='\n%(asctime)s - %(filename)s - %(levelname)s [Line %(lineno)d]\n%(message)s'
    )

    # WORKSPACE = os.path.join(os.path.dirname(__file__), "../../../rom_utils/keys_certs/ahab_certs/secp256r1/")

    # files = [os.path.join(WORKSPACE, file) for file in os.listdir(WORKSPACE)]
    # for file in files:
    #     if os.path.splitext(os.path.split(file)[1])[1] == ".der":
    #         export_pub_from_der(file)
    #     elif os.path.splitext(os.path.split(file)[1])[1] == ".pem":
    #         export_pem_from_cryptpem(file)



