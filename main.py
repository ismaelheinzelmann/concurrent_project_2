from classes.SudokuParser import SudokuParser
import sys

def verify_line(line)-> bool:
    for value in line:
        if value < 1 or value > 9:
            return False
    return len(line) == 9 and sum(line) == sum(set(line)) and sum(line) == 45
    
def verify_column(column)-> bool:
    # transpose the column into line and verify it
    return verify_line([value for (value,) in zip(*[column])])
    
def verify_subgrid(subgrid)-> bool:
    # flatten the subgrid into line and verify it
    return verify_line([value for row in subgrid for value in row])


for filename in sys.argv[1:]:
    tables = SudokuParser(filename).getTables()
    for table in tables:
        for row in range(1,10):
            print(verify_line(table.getLine(row)))
        for column in range(1,10):
            print(verify_column(table.getColumn(column)))
        for subgrid in range(1,10):
            print(verify_subgrid(table.getBlock(subgrid)))