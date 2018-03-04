#!/usr/bin/env python
# Steam account payment history HTML to CSV conversion

from bs4 import BeautifulSoup
from optparse import OptionParser
import re

# from datetime import datetime, date
# import locale

VERSION_PROGRAM = "1.0"
HELP_USAGE = """
Convert Steam account payment history HTML to CSV
%prog -i <HTML file path> -o <CSV file path>
"""


class SteamAccountGame:
    def __init__(self):
        self.date = ""
        self.year = ""
        self.name = ""
        self.event = ""
        self.price = 0.0
        self.currency = ""

    def __str__(self):
        return "| %s | %s | %s | %s %s |" % (self.date, self.event, self.name, self.price, self.currency )

    def toCSV(self, separator):
        list = []
        list.append(self.name)
        list.append(self.date)
        list.append(str(self.price).replace(".", ","))
        list.append(self.currency)
        list.append(self.event)

        return separator.join(list)


def gamesListToCSV(games):
    csv = []
    for g in games:
        print g
        csv.append(g.toCSV("|").decode("iso-8859-1").encode("UTF-8"))
    return csv


def txtParse(steamtxt):
    reyears = re.compile("^\d{1,2} \w{3}, (\d{4})$")
    reprice = re.compile("([^\d]*)([\d,\.]*)(...).*")
    games = []
    state = 0
    for line in steamtxt:
        line = line.strip()
        # Look for date
        if state == 0:
            m = reyears.match(line)
            if m:
                g = SteamAccountGame()
                g.date = m.group(0)
                g.year = m.group(1)
                g.name = []
                state = 1
            continue
        # Look for transaction type, store names
        if state == 1:
            if line == "Purchase":
                g.event = line
                g.name = ", ".join(g.name)
                state = 2
            elif line == "Gift Purchase":
                state = 0
            elif line == "Refund":
                g.event = line
                g.name = ", ".join(g.name)
                state = 4
            elif len(line) != 0:
                g.name.append(line)
            continue
        # Skip a line
        if state == 2:
            state = 3
            continue
        # Finalize recording with price
        if state == 3:
            matchprice = reprice.match(line)
            g.price = float(matchprice.group(2).replace(",", "."))
            if g.event == "Refund":
                g.price *= -1
            g.currency = matchprice.group(1) + matchprice.group(3)
            g.currency = g.currency.strip()

            games.append(g)
            #print g
            state = 0
            continue
        # Handle refunds
        if state == 4:
            if line == "Refund":
                state = 2
            continue

    return games

def txt2csv(inputfile, outputfile):
    inf = open(inputfile, "r")
    steamtxt = inf.readlines()
    gameslist = txtParse(steamtxt)
    steamcsv = gamesListToCSV(gameslist)
    # print steamcsv

    ouf = open(outputfile, "w")
    ouf.write("\n".join(steamcsv))


def printStats(output, gamestotalnum, nonsteamtotalnum, monies):
    output.append("\tNumber of games bought")
    output.append("\t\tSteam store: %d" % (gamestotalnum - nonsteamtotalnum))
    output.append("\t\tOther: %d" % nonsteamtotalnum)
    output.append("\t\tTotal: %d" % gamestotalnum)
    output.append("\tMoney spent")
    for m in monies.keys():
        if monies[m] != 0.0:
            output.append("\t\t%.2f %s" % (monies[m], m))
    return output


def getstats(inputfile, outputfile):
    inf = open(inputfile, "r")
    steamtxt = inf.readlines()
    gameslist = txtParse(steamtxt)

    years = set()
    currencies = set()
    for g in gameslist:
        years.add(g.year)
        if g.currency != "":
            currencies.add(g.currency)
    # print years
    # print currencies
    years.add("Total")
    yearscount = dict()
    for y in years:
        yearscount[y] = list()
    for g in gameslist:
        yearscount[g.year].append(g)
        yearscount["Total"].append(g)

    output = []
    for y in sorted(yearscount.keys(), reverse=True):
        monies = dict()
        nonsteamcount = 0
        for c in currencies:
            monies[c] = 0.0
        for g in yearscount[y]:
            if g.currency != "":
                monies[g.currency] += g.price
            else:
                nonsteamcount += 1
        # print "\t%s" % g.name
        output.append("Year %s" % y)
        printStats(output, len(yearscount[y]), nonsteamcount, monies)

    for l in output:
        print l

    ouf = open(outputfile, "w")
    ouf.write("\n".join(output))


if __name__ == '__main__':
    parser = OptionParser(HELP_USAGE, version="%prog " + VERSION_PROGRAM)
    parser.add_option("-i", "--input", dest="input", default="./steamaccounthistory.html",
                      help="Path of input HTML file")
    parser.add_option("-o", "--output", dest="output", default="./steamaccounthistory.csv",
                      help="Path of output CSV file")
    parser.add_option("-s", "--stat-output", dest="statoutput", default="./steamaccounthistorystats.txt",
                      help="Path of output stats file")

    (options, args) = parser.parse_args()

    #html2csv(options.input, options.output)
    txt2csv(options.input, options.output)
    getstats(options.input, options.statoutput)
