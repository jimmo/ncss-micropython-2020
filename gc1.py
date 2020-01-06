import struct

# Simple allocator that cannot free memory.

class Heap:
    def __init__(self, size):
        # Array of bytes (representing RAM).
        self.data = bytearray(size)
        # Keep track of how many bytes in use.
        self.used = 0
        self.reserved = 0

        # Where should the next allocation come from.
        self.next = 0

    def alloc(self, size):
        # Grab the next `size` bytes, starting at self.next.
        result = self.next
        self.next += size
        if self.next >= len(self.data):
            raise MemoryError()
        self.used += size
        return result

    def free(self, addr):
        # Not supported.
        pass

    def stats(self):
        # Print basic stats about the heap.
        print(f'Total: {len(self.data)}')
        print(f'Used:  {self.used}')
        print(f'Free:  {len(self.data) - self.used - self.reserved}')

    def print(self):
        # Print contents of the heap, 16 bytes at a time.
        for i in range(len(self.data)):
            if i % 16 == 0:
                if i:
                    print()
                print(f'0x{i:04x}: ', end='')
            if ord('a') <= self.data[i] <= ord('z'):
                print(f'{chr(self.data[i]):2s} ', end='')
            else:
                print(f'{self.data[i]:02x} ', end='')
        print()

    def write(self, addr, val):
        # Write single byte at addr.
        self.data[addr] = val

    def read(self, addr):
        # Read single byte at addr.
        return self.data[addr]

    def write32(self, addr, val):
        # Write 32-byte int at addr.
        self.data[addr:addr+4] = struct.pack('<I', val)

    def read32(self, addr):
        # Read 32-byte int at addr.
        return struct.unpack('<I', self.data[addr:addr+4])[0]
