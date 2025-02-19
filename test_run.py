import multiprocessing

def multi_function(exec_function, data, use_ratio: float = 0.5):
    n_cpu = int(multiprocessing.cpu_count() * use_ratio)
    full_len = len(data) # data count
    process_index = int(full_len / n_cpu) # split counts
    rng_list = [(i + 1) * process_index for i in range(n_cpu)] # split indicies
    rng_list[-1] = full_len
    if rng_list[0] != 0:  # add 0 on first index
        rng_list.insert(0, 0)
    if rng_list[-1] < full_len: # last element of range list should equal to data length
        rng_list.append(full_len)
    print(rng_list)

    procs = []
    for i in range(len(rng_list) - 1):
        p = multiprocessing.Process(target = exec_function, args = (rng_list[i], rng_list[i + 1]))
        p.start()
        procs.append(p)
    
    for p in procs:
        p.join()

def test_func(start, end):
    print("test")
    print(start, end)

if __name__ == "__main__":
    test_list = [i for i in range(100)]
    multi_function(test_func, test_list, use_ratio = 0.5)