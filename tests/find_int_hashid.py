# Find the first hashid representation of an integer that is made up of all numbers

from multiprocessing import Pool, cpu_count
import hashids

procs = cpu_count()
chunk = 10_000_000

# Find first integer for tests.models.Record.id
# h = hashids.Hashids(salt="gg ez", min_length=7)
# Found int: encode(428697) == 3557953
# Found int: encode(20020397) == 3554757
# Found int: encode(90043009) == 3517767

# Find first integer for tests.models.Artist.id
h = hashids.Hashids(salt="gg ez", min_length=7, alphabet="1234567890abcdef")
# Found int: encode(161051) == 6966666

# Find the first integer for sandbox.library.models.Author.id
# h = hashids.Hashids(salt="j283wirlkajdf9823rlakdflashdf28y3klrjahskjfuzxcbvu", min_length=13, alphabet="0123456789abcdef")
# Found int: encode(1771710) == 6245755576243

# Find the first integer for sandbox.library.models.Book.reference_id
#h = hashids.Hashids(salt="alternative salt", min_length=7)
# Found int: encode(1789153) == 0226570


def find_int_hashid(c, start, end):
    print("Process {} starting, range {} to {}".format(c, start, end))
    for i in range(start, end):
        if i % 1_000_000 == 0:
            print("{}: {}".format(c, i))
        a = h.encode(i)
        try:
            b = int(a)
            print("{}: Found int: encode({}) == {}".format(c, i, a))
            break
        except ValueError:
            pass


if __name__ == '__main__':
    chunks = []
    for i in range(0, procs):
        chunks.append((i, chunk*i, chunk*(i+1)))
    print("Chunks")
    for i, start, end in chunks:
        print("  {}: {} - {}".format(i, start, end))

    with Pool(procs) as p:
        p.starmap(find_int_hashid, chunks)
