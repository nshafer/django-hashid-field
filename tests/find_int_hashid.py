# Find the first hashid representation of an integer that is made up of all numbers

import hashids

# Find first integer for tests.models.Record.id
# h = hashids.Hashids(salt="gg ez", min_length=7)
# Found int: encode(428697) == 3557953

# Find the first integer for sandbox.library.models.Author.id
# h = hashids.Hashids(salt="j283wirlkajdf9823rlakdflashdf28y3klrjahskjfuzxcbvu", min_length=13, alphabet="0123456789abcdef")
# Found int: encode(1771710) == 6245755576243

# Find the first integer for sandbox.library.models.Book.reference_id
h = hashids.Hashids(salt="alternative salt", min_length=7)
# Found int: encode(1789153) == 0226570

for i in range(1, 1_000_000_000):
    a = h.encode(i)
    try:
        b = int(a)
        print("Found int: encode({}) == {}".format(i, a))
        break
    except ValueError:
        pass
