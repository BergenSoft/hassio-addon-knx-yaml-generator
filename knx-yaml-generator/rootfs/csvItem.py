

class CsvItem:
    # This is used to temporary store the regex results
    matchName: str | None = None

    def __init__(self, mainName: str, middleName: str, name: str, address: str) -> None:
        self.mainName = mainName
        self.middleName = middleName
        self.name = name
        self.address = address
