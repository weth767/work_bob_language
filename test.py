
dictionary = {'t': 2, 'h': 1, 'a': 5}

for i in dictionary.items():
    print(i)
print("\n")

dictionary['d'] = 8

for i in dictionary.items():
    print(i)
print("\n")

print(list(dictionary.items())[1])