#! /usr/bin/env python
# -*- coding: utf-8 -*-

# A simple script to make binary and source releases of Vesicle ImageJ plugin
#
#
# Usage: python make_release.py [NEW_VERSION]
#
# Updates version number to NEW_VERSION and date to current date in relevant
# files, runs 'mvn package' and packs binary and source distributions in the
# .\released\NEW_VERSION\ directory.
#

import fileinput
import os
import sys
import datetime


def update_version_and_date(new_ver):
    today = datetime.date.today()
    for line in fileinput.input("src//main//java//Vesicle_.java", inplace=1):
        if "version =" in line:
            old_ver = line.rsplit(" = ", 1)[1]
            sys.stdout.write(line.replace(old_ver, '"%s";\n' % new_ver))
        elif "year =" in line:
            old_year = line.rsplit(" = ", 1)[1]
            sys.stdout.write(line.replace(old_year, '"%s";\n'
                                          % today.strftime("%Y")))
        elif "month =" in line:
            old_month = line.rsplit(" = ", 1)[1]
            sys.stdout.write(line.replace(old_month, '"%s";\n'
                                          % today.strftime("%B")))
        elif "day =" in line:
            old_day = line.rsplit(" = ", 1)[1]
            sys.stdout.write(line.replace(old_day, '"%s";\n'
                                          % today.strftime("%d").lstrip('0')))
        else:
            sys.stdout.write(line)
    prevline = ""
    for line in fileinput.input("pom.xml", inplace=1):
        if ("<version>" in line
            and "<artifactId>Vesicle_</artifactId>" in prevline):
            old_ver = line.rsplit("<version>", )[1].split("</version>")[0]
            sys.stdout.write(line.replace(old_ver, new_ver))
        else:
            sys.stdout.write(line)
        prevline = line
    for line in fileinput.input("src//main//resources//plugins.config",
                                inplace=1):
        if "# Version:" in line:
            old_ver = line.rsplit("# Version: ", )[1]
            sys.stdout.write(line.replace(old_ver, new_ver))


def yes_no_prompt(query):
    while True:
        s = raw_input(query + ' (y/n): ')
        if s.lower() == 'y':
            return True
        elif s.lower() == 'n':
            return False

try:
    new_version = sys.argv[1]
except IndexError:
    sys.stdout.write("No new version number supplied. Cancelling.\n")
    sys.exit(1)
sys.stdout.write("Preparing Vesicle ImageJ plugin for release...\n")
# Don't bother checking if the new version is valid or larger
# than the previous version, but ask for confirmation
if not yes_no_prompt("Update Vesicle plugin to version %s?"
                     % new_version):
    sys.stdout.write("Cancelling release.\n")
    sys.exit(1)
update_version_and_date(new_version)
os.system("mvn package")
os.system("md released\\%s" % new_version)
os.system("zip -j released\\%s\\Vesicle.IJ-%s.zip target\\Vesicle_-%s.jar "
          "LICENSE changes.txt" %
          (new_version, new_version, new_version))
os.system("zip -j released\\%s\\Vesicle.IJ-%s.source.zip "
          "src\\main\\java\\Vesicle_.java "
          "src\\main\\resources\\plugin.config "
          "LICENSE changes.txt" % (new_version, new_version))