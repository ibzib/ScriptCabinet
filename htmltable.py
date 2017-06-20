#!/usr/bin/env python
import sys
import os
import codecs
import xml.etree.cElementTree as etree

def maketable(infilename, **parameters):
    settings = { "writeheader": True, "delimiter": "\t", "shaderows": False, "shadecolor": "dddddd" }
    for param in parameters:
        if param in settings:
            settings[param] = parameters[param]

    try:
        infile = codecs.open(infilename, "r", encoding="utf-8")
    except IOError as e:
        print e
        return

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
    
    shadenext = settings["shaderows"]
    for line in lines[startindex:]:
        row = etree.SubElement(table, "tr")
        if settings["shaderows"]:
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
    print "Wrote table to '%s'" % outfilename

if __name__ == "__main__":
    def showhelp():
        print "Usage: %s [option] ... [file] ..." % sys.argv[0]
        print "Options:"
        print "-h       : show help"
        print "-n       : don't write a table header"
        print "-d arg   : use arg as column delimiter"
        print "-s [col] : shade alternating rows, using (optional) hex value col"
        print "Example: %s file1.txt" % sys.argv[0]
        print "Example: %s -n -d , -s c1c2c3 file1.txt file2.txt" % sys.argv[0]

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
        elif arg == "-s":
            settings["shaderows"] = True
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
                print "Invalid color value:", e
                exit(1)
        else:
            print "Invalid argument:", arg
            showhelp()
            exit(1)

    if expecting_delimiter:
        print "Error: No delimiter specified following -d flag"
        exit(1)

    if len(filenames) == 0:
        print "Please enter at least 1 input file"
    for filename in filenames:
        maketable(filename, **settings)