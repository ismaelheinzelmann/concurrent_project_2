from classes.Table import Table
class SudokuParser:
    def __init__(self, filename: str):
        self.tables = []
        with(open(filename, 'r')) as file:
            tableLines = []
            lines = file.readlines()
            lines = list(filter(lambda x: x != '\n', lines))
            lines = [x.replace('\n','') for x in lines]

            for line in lines:
                tableLines.append([int(x) for x in line])
            for _ in range(len(tableLines) // 9):
                self.tables.append(Table(tableLines[:9]))
                tableLines = tableLines[9:]

    def getTables(self):
        return self.tables