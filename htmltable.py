#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import codecs
import xml.etree.cElementTree as etree
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, *args, **kwargs):
        # ignore args and kwargs
        print(text)

def maketable(infilename, **kwargs):
    settings = { "writeheader": True, "delimiter": "\t", "colorrows": False, "shadecolor": "dddddd" }
    for param in kwargs:
        if param in settings:
            settings[param] = kwargs[param]

    infile = codecs.open(infilename, "r", encoding="utf-8")
    lines = infile.readlines()
    table = etree.Element("table")

    if settings["writeheader"]:
        row = etree.SubElement(table, "tr")
        columns = lines[0].split(settings["delimiter"])
        for col in columns:
            th = etree.SubElement(row, "th")
            th.text = col
        startindex = 1
    else:
        startindex = 0
    
    shadenext = settings["colorrows"]
    for line in lines[startindex:]:
        row = etree.SubElement(table, "tr")
        if settings["colorrows"]:
            if shadenext:
                row.set("style", "background-color: #%s;" % settings["shadecolor"])
                shadenext = False
            else:
                shadenext = True
        columns = line.split(settings["delimiter"])
        for col in columns:
            td = etree.SubElement(row, "td")
            td.text = col
    
    tree = etree.ElementTree(table)
    outfilename = os.path.splitext(infilename)[0] + ".html"
    tree.write(outfilename, encoding="utf-8")
    cprint("Wrote table to '%s'" % outfilename, "green", attrs=["bold"])

if __name__ == "__main__":
    def showhelp():
        print("Usage: %s [option] ... [file] ..." % sys.argv[0])
        print("Options:")
        print("-h       : show help")
        print("-n       : don't write a table header")
        print("-d arg   : use arg as column delimiter")
        print("-c [col] : color alternating rows, optionally using hex value col (defaults to dddddd)")
        print("Example: %s file1.txt" % sys.argv[0])
        print("Example: %s -n -d , -c c1c2c3 file1.txt file2.txt" % sys.argv[0])

    settings = {}
    filenames = []
    expecting_delimiter = False
    expecting_color = False
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            filenames.append(arg)
        elif arg == "-d":
            expecting_delimiter = True
        elif arg == "-n":
            settings["writeheader"] = False
        elif arg == "-c":
            settings["colorrows"] = True
            expecting_color = True
        elif arg == "-h":
            showhelp()
            exit()
        elif expecting_delimiter:
            settings["delimiter"] = arg
            expecting_delimiter = False
        elif expecting_color:
            try:
                if len(arg) != 6:
                    raise ValueError("please use a 6-digit hex string, e.g. 'a1b2c3'")
                int(arg, base=16) # check that arg is a valid hex value
                settings["shadecolor"] = arg
                expecting_color = False
            except ValueError as e:
                cprint("Invalid color value: %s" % e, "red")
                exit(1)
        elif arg.startswith("-") or arg.startswith("--"):
            cprint("Invalid option: %s" % arg, "red")
            showhelp()
            exit(1)
        else:
            filenames.append(arg)

    if expecting_delimiter:
        cprint("Error: No delimiter specified following -d flag", "red")
        showhelp()
        exit(1)

    if len(filenames) == 0:
        cprint("Please enter at least 1 input file", "red")
        showhelp()
        exit(1)

    for filename in filenames:
        try:
            maketable(filename, **settings)
        except IOError as e:
            cprint(e, "red")