from classes.SudokuParser import SudokuParser
from multiprocessing import Process, Queue
from threading import Thread, Lock, Semaphore
from funcs import (
    verify_line,
    verify_column,
    verify_subgrid,
    clear_errors,
    print_results,
)
import sys
import time


def thread_process(i, threads_queue, errors, tables, lock, sem):
    while True:
        request = threads_queue.get()
        if request == (-1, -1, -1):
            sem.release()
            return
        (table, req, index) = request
        response = ""
        valid = bool()
        if req == "line":
            response = f"L{index}"
            valid = verify_line(tables[table - 1].get_line(int(index)))
        elif req == "column":
            response = f"C{index}"
            valid = verify_column(tables[table - 1].get_column(int(index)))
        elif req == "subgrid":
            response = f"R{index}"
            valid = verify_subgrid(tables[table - 1].get_block(int(index)))
        if not valid:
            with lock:
                errors[i].append(response)
        sem.release()


def process_worker(id, requests_queue, threads_n, tables):
    errors = [[] for _ in range(threads_n)]
    lock = Lock()
    threads_queue = Queue()
    sem_done = Semaphore(0)
    threads = [
        Thread(
            target=thread_process,
            args=(i, threads_queue, errors, tables, lock, sem_done),
        )
        for i in range(threads_n)
    ]
    for thread in threads:
        thread.start()
    working_job = None
    counter = 0
    while True:
        request = requests_queue.get()
        if request == (-1, -1, -1):
            for _ in range(threads_n):
                threads_queue.put((-1, -1, -1))
            for _ in range(counter):
                sem_done.acquire()
                counter -= 1
            print_results(errors, id)
            for thread in threads:
                thread.join()
            return
        if working_job is None:
            working_job = request[0]
            print(f"Processo {id + 1}: resolvendo quebra-cabeças {working_job}")
        if working_job != request[0]:
            for _ in range(counter):
                sem_done.acquire()
                counter -= 1
            print_results(errors, id)
            clear_errors(errors)
            working_job = request[0]
            print(f"Processo {id + 1}: resolvendo quebra-cabeças {working_job}")
            counter = 0
        threads_queue.put(request)
        counter += 1


if __name__ == "__main__":
    TABLES = SudokuParser(sys.argv[1]).getTables()
    NUM_PROCESS = int(sys.argv[2])
    THREADS_PER_PROCESS = int(sys.argv[3])
    N_TABLES = len(TABLES)
    requests = Queue()
    processes = [
        Process(target=process_worker, args=(i, requests, THREADS_PER_PROCESS, TABLES))
        for i in range(NUM_PROCESS)
    ]
    for p in processes:
        p.start()
    for table in range(1, N_TABLES + 1):
        for line in range(1, 10):
            requests.put((table, "line", line))
        for column in range(1, 10):
            requests.put((table, "column", column))
        for subgrid in range(1, 10):
            requests.put((table, "subgrid", subgrid))
    for _ in range(NUM_PROCESS):
        requests.put((-1, -1, -1))
    for p in processes:
        p.join()
