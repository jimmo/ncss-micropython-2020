import struct

from gc1 import Heap

# Allocator that can return memory to the heap.

class HeapWithFree(Heap):
    def __init__(self, size):
        super().__init__(size)

    def alloc(self, size):
        # Add 4 bytes to make room for 32-bit size.
        size += 4

        # Round up to four bytes.
        if size % 4 != 0:
            size += 4 - (size % 4)

        # Set to true after we wrap once (if we wrap twice, fail).
        repeat = False

        # Keep searching until we find something (or wrap twice).
        while True:
            # How many we've found this time.
            avail = 0

            # If we're too close to the end, start from the beginning.
            if self.next + size >= len(self.data):
                if repeat:
                    raise MemoryError()
                self.next = 0
                repeat = True
                continue

            # See if the next `size` bytes are zero (i.e. free).
            # If there was a used region, it would have a non-zero size recorded.
            for i in range(0, size, 4):
                if self.read32(self.next + i) > 0:
                    # Nope, something was here, assume it's a size.
                    self.next = self.next + i + self.read32(self.next + i)
                    break
                else:
                    # Four more free bytes.
                    avail += 4

            # Found enough free bytes.
            if avail == size:
                result = self.next
                self.next += size
                self.used += size
                self.write32(result, size)
                return result + 4

    def free(self, addr):
        # Go back four bytes and grab the size.
        addr -= 4
        size = self.read32(addr)
        # Zero out that many bytes.
        self.data[addr:addr+size] = bytes(size)
        self.used -= size

