import requests
from bs4 import BeautifulSoup
import openpyxl

wikiUrl = "https://en.wikipedia.org"

class InfoBox():
    def __init__(self, soup):
        self.portrait = None
        self.titles = []
        for row in soup.find_all("tr"):
            if self.portrait is None:
                image = row.find('a', class_="image")
                if image is not None:
                    self.portrait = image.get('href')
            th = row.find('th')
            if th is not None:
                links = th.find_all('a')

                if len(links) > 0:
                    if "lavender" in str(th):
                        print row.text
                        print [a.text for a in links]
        pass


class FoundingFather():
    def __init__(self, row, header):
        if type(row) == list:
            record = row[0]
        else:
            record = row
        global wikiUrl
        cells = record.find_all('td')
        self.name = cells[0].text
        self.link = wikiUrl + cells[0].find('a').get('href')
        self.state = cells[1].text
        self.documents = self._makeDocDict(record, header)
        if type(row) == list:
            self.updateFromList(row[1:], header)
        self._getPageInfo()
        self._getInfoBox()

    def _getInfoBox(self):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.text, 'html.parser')


    def _getPageInfo(self):
        def isNum(n):
            try:
                float(n)
                return True
            except:
                return False

        def splitDate(text):
            lst = []
            date = ""
            for c in text:
                try:
                    date += str(c)
                except UnicodeEncodeError:
                    if date != "":
                        lst.append(date)
                    date = ""
            if date != "":
                lst.append(date)
            return lst

        def datesFromText(text):
            dates = ""
            isDate = False
            wasDate = False
            exclude = False
            for c in text:
                if c == ")":
                    if wasDate:
                        return dates
                    else:
                        dates = ""
                        isDate = False
                if isDate and c == '[':
                    exclude = True
                if isDate and not exclude:
                    if isNum(c):
                        wasDate = True
                    dates += c
                if isDate and c == ']':
                    exclude = False
                if c == "(":
                    isDate = True
            return dates
        r = requests.get(self.link)
        soup = BeautifulSoup(r.text, 'html.parser')
        main = soup.find(class_="mw-content-ltr")
        firstParagraph = main.find('p')
        self.dates = splitDate(datesFromText(firstParagraph.text))
        infobox = soup.find(class_="infobox")
        if infobox is not None:
            self.infobox = InfoBox(infobox)

    def updateFromList(self, row, header):
        headerCells = header.find_all('th')
        for part in row:
            rowCells = part.find_all('td')
            self.state += "," + rowCells[0].text
            for i in xrange(len(headerCells)):
                abbr = headerCells[i].find('abbr')
                if abbr:
                    if self.documents.has_key(abbr.get('title')):
                        existing = self.documents[abbr.get('title')]
                    else:
                        existing = False
                    self.documents[abbr.get('title')] = existing or bool(len(rowCells[i-1].text))

    def _makeDocDict(self, row, header):
        headerCells = header.find_all('th')
        rowCells = row.find_all('td')
        docDict = {}
        for i in xrange(len(headerCells)):
            abbr = headerCells[i].find('abbr')
            if abbr:
                docDict[abbr.get('title')] = bool(len(rowCells[i].text))
        return docDict


def GetTable():
    global wikiUrl
    url = wikiUrl + "/wiki/Founding_Fathers_of_the_United_States"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    ffSection = soup.find(id="Founding_Fathers")
    current = ffSection
    while True:
        if current.name == 'table':
            return current
        current = current.next_element


def flattenRows(rows):
    # change this so it only looks at the first row for indication
    newList = []
    i = 0
    while i < len(rows):
        row = rows[i]
        cells = row.find_all('td')
        rowspan = cells[0].get('rowspan')

        if not rowspan:
            newList.append(row)
            i += 1
        else:
            newList.append(rows[i:i+int(rowspan)])
            i += int(rowspan)
    return newList


def main():
    table = GetTable()
    allRows = table.find_all('tr')
    header = allRows[0]
    ffList = [FoundingFather(row, header) for row in flattenRows(allRows[1:])]
    print len(ffList)

if __name__ == '__main__':
    main()