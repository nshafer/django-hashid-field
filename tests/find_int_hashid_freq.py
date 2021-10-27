# Find the frequency of all-number hashids within 1_000_000 encodes for default settings

from multiprocessing import Pool, cpu_count
import hashids
import hashlib

procs = cpu_count()
num_tests = 1_000
num_iterations = 1_000_000


def find_frequency(i):
    salt = hashlib.md5(bytes(i)).hexdigest()
    print("Finding frequency for salt {}".format(salt))
    h = hashids.Hashids(salt=salt, min_length=7)

    count = 0
    for i in range(1, num_iterations):
        a = h.encode(i)
        try:
            b = int(a)
            count += 1
        except ValueError:
            pass
    print("Frequency for salt {}: {}".format(salt, count))

    return count

if __name__ == '__main__':
    with Pool(procs) as p:
        frequencies = p.map(find_frequency, range(0, num_tests))
        # print("Frequencies: {}".format(frequencies))
        print("Average frequency: {:2f}".format(sum(frequencies) / len(frequencies)))

