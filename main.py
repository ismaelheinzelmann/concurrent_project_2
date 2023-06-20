from classes.SudokuParser import SudokuParser
from multiprocessing import Process, Queue, Lock
from threading import Lock as tLock
from concurrent.futures import ThreadPoolExecutor
import sys

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

def thread_process(responses, response_lock, table, request, index)-> str:
    valid = bool()
    response = ""
    if request == "line":
        response = f"L{index}"
        valid = verify_line(TABLES[table - 1].getLine(int(index)))
    elif request == "column":
        response = f"C{index}"
        valid = verify_column(TABLES[table - 1].getColumn(int(index)))
    elif request == "subgrid":
        response = f"R{index}"
        valid = verify_subgrid(TABLES[table - 1].getBlock(int(index)))
    if not valid:
        response_lock.acquire()
        responses[f"T{table}"].append(response)
        response_lock.release()


def process(threads, request_queue, response_queue, id, pLock)-> bool:
    #process should create threads and wait for them to finish
    #lock for responses and lock for request
    responses = {}
    responses_lock = tLock()
    executor = ThreadPoolExecutor(max_workers=threads)

    running_table = -1
    while True:
        request = str()
        with pLock:
            if request_queue.empty():
                break
            request = request_queue.get().split("|")
        if running_table != int(request[0]):
            running_table = int(request[0])
            responses[f"T{running_table}"] = []
            response_queue.put(f"Processo {id}: resolvendo quebra-cabeças {running_table}")
        #submit
        executor.submit(thread_process, responses, responses_lock, int(request[0]), request[1], int(request[2]))

    executor.shutdown(wait=True)
    final = f"Processo {id}: "
    total_errors = sum([len(x) for x in responses.values() if len(x) > 0])
    if total_errors == 0:
        final += "0 erros encontrados."
        response_queue.put(final)
    else:
        final+= f"{total_errors} erros encontrados ("
        final_append = []
        for table, errors in responses.items():
            if len(errors) > 0:
                final_append.append(f"{table}: {', '.join(errors)}")
        final += "; ".join(final_append)
        final += ")"
        response_queue.put(final)
    response_queue.put("END")
    return

TABLES = SudokuParser(sys.argv[1]).getTables()
NUM_PROCESS = int(sys.argv[2])
THREADS_PER_PROCESS = int(sys.argv[3])
N_TABLES = len(TABLES)

request_queue = Queue()
request_queue_lock = Lock()
response_queue = Queue()
processes = [Process(target=process, args = [THREADS_PER_PROCESS, request_queue, response_queue, i, request_queue_lock]) for i in range(1, NUM_PROCESS + 1)]
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
