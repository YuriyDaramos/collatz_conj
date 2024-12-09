import time
from multiprocessing import Queue, Process

BLACK = "\033[30m"
BG_YELLOW = "\033[43m"
RESET = "\033[0m"
BOLD = "\033[1m"


def collatz_test(start, end, search_step, result_queue):
    start_time = time.time()
    for number in range(start, end + 1, search_step):
        while number != 1:
            if number % 2:
                number = 3 * number + 1
            else:
                number = number // 2

    end_time = time.time()
    result_queue.put(end_time - start_time)


if __name__ == "__main__":
    result_queue = Queue()
    search_range = 1_000_000_000
    num_processes = 6
    processes = []

    for i in range(1, num_processes + 1):
        start = i
        end = search_range
        search_step = num_processes
        process = Process(target=collatz_test, args=(start, end, search_step, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    while not result_queue.empty():
        result = result_queue.get()
        print(f"Last loop duration: {result} seconds")

    print(f"\n{BLACK}{BG_YELLOW}{BOLD} COMPLETE! {RESET}")
