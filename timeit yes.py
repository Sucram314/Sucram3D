import timeit

setup = """
mylist = ["234","123","91","53","2"]
"""

code1 = """
mylist = list(map(lambda x:(float(x)/255),mylist))
"""

code2 = """
mylist = [float(_)/255 for _ in mylist]
"""

print(timeit.timeit(stmt=code1,setup=setup))
print(timeit.timeit(stmt=code2,setup=setup))

