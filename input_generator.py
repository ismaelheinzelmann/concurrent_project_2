import random

n = int(input())
symbol = "123456789"
# create a file with the name "input_n.txt"
with open(f"input_{n}.txt", "w") as f:
    # write 9 lines containing 9 random symbols
    for _ in range(n):
        for _ in range(9):
            f.write("".join(random.choices(symbol, k=9)))
            f.write("\n")
        f.write("\n")
