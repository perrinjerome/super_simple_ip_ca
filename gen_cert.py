#!/bin/python
from __future__ import print_function
import subprocess
import glob
import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Generate a x509 certificate for this ip")
parser.add_argument("CN", help="Common Name")
parser.add_argument("IP", help="IP Address")

sub_dict = {}
args = parser.parse_args()


def openssl(*args):
    try:
        subprocess.check_call(["openssl"] + list(args))
    except subprocess.CalledProcessError as e:
        print('Command "openssl %s" failed' % " ".join(args))
        sys.exit(e.returncode)


if not os.path.exists("myCA.key"):
    print("Initializing")
    openssl("genrsa", "-out", "myCA.key", "2048")
    openssl(
        "req", "-new", "-x509", "-days", "3650", "-key", "myCA.key", "-out", "myCA.pem"
    )
    open("index.txt", "w").close()
    with open("serial", "w") as serial:
        serial.write("01\n")
    os.mkdir("newcerts")
    try:
        # try to prompt to import CA
        subprocess.check_call(["open", "myCA.pem"])
    except:
        pass


def substitute_template(src):
    for k, v in vars(args).items():
        src = src.replace("%%{}%%".format(k), v)
    return src


for template in glob.glob("templates/*"):
    # print template, substitute_template(template, vars(args))
    with open(template, "r") as f:
        src = f.read()
        open(os.path.basename(substitute_template(template)), "w").write(
            substitute_template(src)
        )

openssl(
    "req",
    "-new",
    "-out",
    substitute_template("%%CN%%.csr"),
    "-config",
    substitute_template("%%CN%%.csr.conf"),
)

openssl(
    "ca",
    "-config",
    "ca.conf",
    "-extfile",
    substitute_template("%%CN%%.csr.extensions.conf"),
    "-in",
    substitute_template("%%CN%%.csr"),
    "-out",
    substitute_template("%%CN%%.crt"),
)
