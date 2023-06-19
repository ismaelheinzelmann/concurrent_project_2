from classes.SudokuParser import SudokuParser
from multiprocessing import Process, Queue
from threading import Thread, Lock
import sys
# 9 linhas
# 9 colunas
# 9 subgrids
# 27 verificações por table
# n = numero de tabelas

def verify_line(line)-> bool:
    for value in line:
        if value < 1 or value > 9:
            return False
    return len(line) == 9 and sum(line) == sum(set(line))
    
def verify_column(column)-> bool:
    # transpose the column into line and verify it
    return verify_line([value for (value,) in zip(*[column])])
    
def verify_subgrid(subgrid)-> bool:
    # flatten the subgrid into line and verify it
    return verify_line([value for row in subgrid for value in row])




def process(threads, request_queue, response_queue, id):
    responses = {}

    running_table = -1
    response = ""
    while not request_queue.empty():
        request = request_queue.get().split("|")
        if running_table != int(request[0]):
            running_table = int(request[0])
            responses[f"T{running_table}"] = []
            response_queue.put(f"Processo {id}: resolvendo quebra-cabeças {running_table}")
        valid = bool()
        if request[1] == "line":
            response = f"L{request[2]}"
            valid = verify_line(TABLES[running_table - 1].getLine(int(request[2])))
        elif request[1] == "column":
            response = f"C{request[2]}"
            valid = verify_column(TABLES[running_table - 1].getColumn(int(request[2])))
        elif request[1] == "subgrid":
            response = f"R{request[2]}"
            valid = verify_subgrid(TABLES[running_table - 1].getBlock(int(request[2])))
        if not valid:      
            responses[f"T{running_table}"].append(response)


    final = f"Processo {id}: "
    for k, v in responses.items():
        print(k, v)
        if v.length() == 0:
            del responses[k]
            continue
    if len(responses.keys()) == 0:
        final += "0 erros encontrados."
        response_queue.put(final)
        return
    else:
        #summ all errors and plot them.
        pass
    
    response_queue.put("END")



TABLES = SudokuParser(sys.argv[1]).getTables()
NUM_PROCESS = int(sys.argv[2])
THREADS_PER_PROCESS = int(sys.argv[3])
N_TABLES = len(TABLES)

request_queue = Queue()
response_queue = Queue()
processes = [Process(target=process, args = [THREADS_PER_PROCESS, request_queue, response_queue, i]) for i in range(1, NUM_PROCESS + 1)]
# request model: "table|line or column or subgrid|number"
for table in range(1, N_TABLES + 1):
    for line in range(1, 10):
        request_queue.put(f"{table}|line|{line}")
    for column in range(1, 10):
        request_queue.put(f"{table}|column|{column}")
    for subgrid in range(1, 10):
        request_queue.put(f"{table}|subgrid|{subgrid}")
# print(request_queue.get())
for p in processes:
    p.start()

end = 0
while end < NUM_PROCESS:
    response = response_queue.get()
    if response == "END":
        end += 1
    else:
        print(response)


for p in processes:
    p.join()
