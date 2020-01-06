import random

from gc1 import Heap
from gc2 import HeapWithFree
from gc3 import HeapWithGC

HeapType = HeapWithGC


def random_allocs(h):
    s = set()
    for _ in range(1000):
        size = random.randrange(4, 32)
        addr = h.alloc(size)
        #print(addr)
        #s.add(addr)

        for i in range(size):
            h.write(addr + i, ord('a') + random.randrange(0, 26))

        if random.randrange(0, 40) == 0:
            h.roots.append(addr)

        # if len(s) > 30:
        #     for _ in range(5):
        #         addr = random.choice(list(s))
        #         s.remove(addr)
        #         h.free(addr)

def main():
    h = HeapType(1024)
    try:
        random_allocs(h)
    except MemoryError:
        print('Out of memory.')
    h.print()
    h.stats()

if __name__ == '__main__':
    main()



    # def demo():
    #     h = Heap(1024)
    #     h.stats()
    #     for i in range(10):
    #         p = h.alloc(30)
    #         h.write32(p, 0x01020304)
    #         h.free(p)
    #     h.print()
    #     h.stats()

    # if __name__ == '__main__':
    #     try:
    #         demo()
    #     except MemoryError as e:
    #         print('Out of memory.')




# def demo():
#     h = Heap(1024)
#     h.stats()
#     n = 0
#     for i in range(1000):
#         p = h.alloc(n + 4)
#         n = (n + 1) % 20
#         h.write32(p, 0x01020304)
#         h.free(p)
#     h.print()
#     h.stats()

# if __name__ == '__main__':
#     try:
#         demo()
#     except MemoryError as e:
#         print('Out of memory.')
