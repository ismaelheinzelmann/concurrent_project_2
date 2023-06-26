from math import ceil

from classes.SudokuParser import SudokuParser
from multiprocessing import Process, Queue
from threading import Thread, Lock, Semaphore
from funcs import verify_line, verify_column, verify_subgrid
import sys
import time


def clear_errors(errors):
    for table in errors:
        for thread in table:
            thread.clear()

def thread_process(id, id_thread,start, threads_queue, errors, tables, tables_n, semaphores, lock, already_lock, already):
    while True:
        request = threads_queue.get()
        if request == (-1, -1, -1):
            break
        (table, req, index) = request
        with already_lock[table]:
            if not already[table]:
                print(f"Processo {id + 1}: resolvendo quebra-cabeças {int((start/10)+table) + 1}")
                already[table] = True
        response = ""
        valid = bool()
        if req == "line":
            response = f"L{index}"
            valid = verify_line(tables[table].get_line(int(index)))
        elif req == "column":
            response = f"C{index}"
            valid = verify_column(tables[table].get_column(int(index)))
        elif req == "subgrid":
            response = f"R{index}"
            valid = verify_subgrid(tables[table].get_block(int(index)))
        if not valid:
            with lock:
                errors[table][id_thread].append(response)
        semaphores[table].release()


def process_worker(id, start, filename, tables_n, threads_n):
    tables = SudokuParser(filename, start, start + tables_n * 10).getTables()
    errors = [[[] for _ in range(threads_n)] for _ in range(len(tables))]
    already = [False for _ in range(tables_n)]
    already_lock = [Lock() for _ in range(tables_n)]
    for i in range(1, tables_n):
        already_lock[i].acquire()
    lock = Lock()
    threads_queue = Queue()
    for table in range(len(tables)):
        for line in range(1, 10):
            threads_queue.put((table, "line", line))
        for column in range(1, 10):
            threads_queue.put((table, "column", column))
        for subgrid in range(1, 10):
            threads_queue.put((table, "subgrid", subgrid))
    for _ in range(threads_n):
        threads_queue.put((-1, -1, -1))

    semaphores = [Semaphore(0) for _ in range(tables_n)]
    threads = [Thread(target=thread_process,
                      args=(id, i,start, threads_queue, errors, tables, len(tables), semaphores, lock, already_lock, already))
               for i in
               range(threads_n)]
    for thread in threads:
        thread.start()
    for table in range(len(tables)):
        for _ in range(27):
            semaphores[table].acquire()
        total_errors = 0
        for table_e in errors[table]:
            total_errors += len(table_e)
        if total_errors == 0:
            print(f"Processo {id + 1}: 0 erros encontrados.")
        else:
            print(f"Processo {id + 1}: {total_errors} erros encontrados (", end="")
            final_append = [f"T{i + 1}: {', '.join(e)}" for i, e in enumerate(errors[table]) if len(e) > 0]
            print("; ".join(final_append) + ")")
        if table != tables_n - 1:
            clear_errors(errors)
            already_lock[table + 1].release()

    for thread in threads:
        thread.join()
if __name__ == "__main__":
    # start_time = time.time()
    N_LINES = 0
    with open(sys.argv[1], 'r') as file:
        N_LINES = len(file.readlines())
    NUM_PROCESS = int(sys.argv[2])
    THREADS_PER_PROCESS = int(sys.argv[3])
    N_TABLES = ceil(N_LINES / 10)
    if NUM_PROCESS > N_TABLES:
        NUM_PROCESS = N_TABLES
    dist = [N_TABLES // NUM_PROCESS for _ in range(NUM_PROCESS)]
    next_start = 0
    for i in range(N_TABLES % NUM_PROCESS):
        dist[i] += 1
    requests = Queue()
    processes = []
    for i in range(NUM_PROCESS):
        processes.append(
            Process(target=process_worker, args=(i, next_start, sys.argv[1], dist[i], THREADS_PER_PROCESS)))
        next_start += dist[i] * 10
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    # print(f"Tempo de execução: {time.time() - start_time} segundos.")
