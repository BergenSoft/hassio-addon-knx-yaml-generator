import csv
import re
from typing import List
from settings import Settings
from csvItem import CsvItem


class CsvReader:
    __instance = None

    @staticmethod
    def instance() -> "CsvReader":
        if CsvReader.__instance is None:
            CsvReader.__instance = CsvReader()

        return CsvReader.__instance

    def __init__(self) -> None:
        if CsvReader.__instance is not None:
            raise Exception("Sorry, call CsvReader.instance()")

        # singleton
        CsvReader.__instance = self

        self.__items: List[CsvItem] = []
        self.__mainNames = {}
        self.__middleNames = {}

        with open(Settings.instance().path_csv_grp, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t", quotechar="\"")

            # Skip the header of the file
            next(reader, None)

            for row in reader:
                if row[1].find("/-/-") != -1:
                    self.__mainNames[row[1][:-4]] = row[0]
                elif row[1].find("/-") != -1:
                    self.__middleNames[row[1][:-2]] = row[0]
                else:
                    self.__items.append(CsvItem(
                        self.__mainNames[row[1][0:row[1].find("/")]],
                        self.__middleNames[row[1][0:row[1].rfind("/")]],
                        row[0],
                        row[1]
                    ))

    def query(self, grp: str | None, regex: str, regexIgnore: str) -> List["CsvItem"]:
        # This happens if a key is not set
        if regex is None:
            return []

        if grp is None or grp == "":
            # No address filter, take all
            sublist = self.__items
        else:
            # first filter by address
            sublist = [i for i in self.__items if i.address.startswith(grp)]

        # second filter: regex has to match, regexIgnore is not allowed to match
        sublist = [i for i in sublist
                   if re.search("^" + regex + "$", i.name) is not None and
                   (
                       regexIgnore is None or
                       re.search("^" + regexIgnore + "$", i.name) is None
                   )
                   ]

        # set matchname for current regex
        for item in sublist:
            findResult = re.findall("^" + regex + "$", item.name)
            if len(findResult) > 0:
                item.matchName = findResult[0]
            else:
                item.matchName = None

        return sublist
