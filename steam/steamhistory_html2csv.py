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

    def toCSV(self, separator):
        list = []
        list.append(self.name)
        list.append(self.date)
        list.append(str(self.price))
        list.append(self.currency)
        list.append(self.event)

        return separator.join(list)


def soupParse(soup):
    games = []
    reprice = re.compile("([^\d]*)([\d,\.]*)(.*)")
    reyears = re.compile("\d{1,2} \w{3} (\d{4})")
    # locale.setlocale(locale.LC_TIME, "en_US")
    for attr in ["transactions", "hidden_transactions"]:
        transactions = soup.find("div", attr, )
        gamestransactions = transactions.find_all("div", "transactionRow")
        for gt in gamestransactions:
            g = SteamAccountGame()
            # g.date = datetime.strptime("%d %b %Y", gt.find("div", "transactionRowDate").get_text())
            g.date = gt.find("div", "transactionRowDate").get_text()
            g.year = str(reyears.match(g.date).group(1))
            g.name = gt.find("div", "transactionRowTitle").get_text()
            g.event = gt.find("div", "transactionRowEvent").get_text()
            price = gt.find("div", "transactionRowPrice").get_text()
            if price == "Free":
                g.price = 0.0
            else:
                matchprice = reprice.match(price)
                g.price = float(matchprice.group(2).replace(",", "."))
                g.currency = matchprice.group(1) + matchprice.group(3)
                g.currency = g.currency.strip()
            games.append(g)
    # locale.resetlocale(locale.LC_TIME)
    return games


def gamesListToCSV(games):
    csv = []
    for g in games:
        csv.append(g.toCSV(";").encode("UTF-8"))
    return csv


def html2csv(inputfile, outputfile):
    inf = open(inputfile, "r")
    steamhtml = inf.read()

    soup = BeautifulSoup(steamhtml)
    gameslist = soupParse(soup)

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
            output.append("\t\t%.2f %s" % (monies[m], m.encode("UTF-8")))
    return output


def html2stats(inputfile, outputfile):
    inf = open(inputfile, "r")
    steamhtml = inf.read()

    soup = BeautifulSoup(steamhtml)
    gameslist = soupParse(soup)

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

    html2csv(options.input, options.output)
    html2stats(options.input, options.statoutput)
