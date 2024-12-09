import time
import multiprocessing
import traceback

BLACK = "\033[30m"
BG_YELLOW = "\033[43m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_calc(number, step, operation, result=0):
    operations = {"new": lambda: f"Calculation for ⌞{number}⌝",
                  "odd": lambda: f"\t{step}: 3 * {number} + 1 = {result}",
                  "even": lambda: f"\t{step}: {number} / 2 = {result}",
                  "finish": lambda: f"\t--Confirmed! Total steps: {step-1}.\n"}
    if operation in operations:
        print(operations[operation]())


def is_new_max_step(step, max_steps):
    if step > max_steps[-1][-1]:
        return True


def print_progress(number, step, max_step, search_range, multi_set):
    progress = (number / search_range) * 100
    sets_num = len(multi_set[1:])
    set_len = len(multi_set[-1])

    print(f"\r Number: ⌞{number:13,}⌝ "
          f"| Steps: ⌞{step:5}⌝ "
          f"| MaxStep: ⌞{max_step[-1][-1]:8,}⌝ for ⌞{max_step[-1][0]:12,}⌝ "
          f"| Progress: {progress:3.3f}% "
          f"| Set: ⌞{sets_num:03}⌝ "
          f"| Set length: ⌞{set_len:11,}⌝ ", end="")


def is_confirmed(number, result, multi_set):
    if result <= number-1 or not result % 2 or contain_in_multi_set(multi_set, result):
        return True


def add_to_multi_set(number, multi_set, confirmed_set):
    def set_overflow(multiset):
        return len(multiset[-1]) >= multiset[0].get("max_set_size")

    if set_overflow(multi_set):
        try:
            for num in range(multi_set[0].get("last_cut"), number):
                multi_set[-1].discard(num)
        except MemoryError:
            print(f"\nAn error occurred.")
            traceback.print_exc()
            print(f"Can't create range started in {multi_set[0].get('last_cut')} and ended {number}")
            print(f"Range: {multi_set[0].get('last_cut') - number}")
        multi_set[0]["last_cut"] = number

        if set_overflow(multi_set):
            multi_set.append(set())

    multi_set[-1].update(confirmed_set)


def contain_in_multi_set(multi_set, number):
    if any(number in subset for subset in multi_set[1:]):
        return True


def worker(start, step, end):
    collatz_test(start, end, step)


def collatz_test(start, end, search_step, track_max_step=False, show_calc=False, show_progress=False):
    max_steps = [(1, 0)]
    multi_set = [{"last_cut": 0, "max_set_size": 5_000_000}, set()]
    confirmed_set = set()

    for number in range(start, end + 1, search_step):
        step = 1
        result = number
        if show_calc:
            print_calc(number, step, "new")
        while result != 1:
            if is_confirmed(number, result, multi_set):
                break
            if result % 2:
                new_result = 3 * result + 1
                operation = "odd"
            else:
                new_result = result // 2
                operation = "even"
            if show_calc:
                print_calc(number, step, operation, result=new_result)
            result = new_result
            confirmed_set.add(result)
            step += 1
        add_to_multi_set(number, multi_set, confirmed_set)
        confirmed_set.clear()

        if show_calc:
            print_calc(number, step, "finish")
        if track_max_step and is_new_max_step(step, max_steps):
            max_steps.append((number, step))
        if show_progress and not number % 1000 and not show_calc:
            print_progress(number, step, max_steps, end, multi_set)


if __name__ == "__main__":
    range_list = [100_000, 1_000_000, 10_000_000, 100_000_000, 1_000_000_000]
    for search_range in range_list:
        print(f"\nRange {search_range:3,}")
        num_processes = 12
        chunk_size = search_range // num_processes

        start_time = time.time()

        pool = multiprocessing.Pool(processes=num_processes)

        for i in range(1, num_processes + 1):
            start = i
            search_step = num_processes
            pool.apply_async(worker, (start, search_step, search_range))

        pool.close()
        pool.join()

        end_time = time.time()

        execution_time = end_time - start_time
        print(f"\n{BLACK}{BG_YELLOW}{BOLD} COMPLETE! {RESET}")
        print(f"Execution time: {execution_time:.3f} seconds")
