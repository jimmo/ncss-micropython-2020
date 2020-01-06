import struct

from gc1 import Heap

# Garbage-collecting allocator.

BLOCK_SIZE = 16

STATE_FREE = 0
STATE_HEAD = 1
STATE_TAIL = 2
STATE_MARK = 3

class HeapWithGC(Heap):
    def __init__(self, size):
        super().__init__(size)

        # Figure out size of block table.
        self.total_blocks = size // (BLOCK_SIZE + 1)
        self.reserved = self.total_blocks

        # Root pointers.
        self.roots = []

    def alloc(self, size):
        # Round up to sixteen bytes.
        if size % BLOCK_SIZE != 0:
            size += BLOCK_SIZE - (size % BLOCK_SIZE)

        n_blocks = size // BLOCK_SIZE

        # Set to true after we wrap once (if we wrap twice, fail).
        repeat = False
        collected = False

        # Keep searching until we find something (or wrap twice).
        while True:
            # How many we've found this time.
            avail = 0

            # If we're too close to the end, start from the beginning.
            if self.next + n_blocks >= self.total_blocks:
                if repeat:
                    if collected:
                        raise MemoryError()
                    self.collect()
                    repeat = False
                    collected = True
                else:
                    repeat = True
                self.next = 0
                continue

            # See if the next `n_blocks` blocks are free.
            # If there was a used region, it would have a non-zero size recorded.
            for i in range(n_blocks):
                if self.read(self.next + i) != STATE_FREE:
                    # Used block.
                    self.next += 1
                    break
                else:
                    # Four more free bytes.
                    avail += 1

            # Found enough free bytes.
            if avail == n_blocks:
                result = self.total_blocks + self.next * BLOCK_SIZE

                # Mark these blocks as Head,Tail,Tail...
                self.write(self.next, STATE_HEAD)
                self.next += 1
                for i in range(n_blocks - 1):
                    self.write(self.next, STATE_TAIL)
                    self.next += 1

                self.used += size
                return result

    def free(self, addr):
        pass

    def mark(self, stack):
        # Keep popping pointers off the stack...
        while stack:
            addr = stack.pop()
            block = (addr - self.total_blocks) // BLOCK_SIZE
            # Mark this head block (and therefore implicitly any subsequent blocks in this alloc).
            self.write(block, STATE_MARK)

            # Search for pointers in this block and any tail blocks following this head block.
            while True:
                for offset in range(BLOCK_SIZE // 4):
                    maybe_addr = self.read32(addr + offset * 4)
                    if maybe_addr >= self.total_blocks and maybe_addr <= len(self.data):
                        stack.append(maybe_addr)
                block += 1
                if self.read(block) != STATE_TAIL:
                    break


    def collect(self):
        # Search from all roots for any reachable blocks.
        self.mark(self.roots[:])

        # Find any unmarked blocks (and their tails) and free them.
        clear_tail = False
        for i in range(self.total_blocks):
            if self.read(i) == STATE_HEAD:
                # Found a head, free it.
                self.write(i, STATE_FREE)
                addr = self.total_blocks + (i * BLOCK_SIZE)
                self.data[addr:addr + BLOCK_SIZE] = bytes(BLOCK_SIZE)
                self.used -= BLOCK_SIZE
                # Remember to clear its tail.
                clear_tail = True
            elif clear_tail:
                # Keep freeing any subsequent tails.
                if self.read(i) == STATE_TAIL:
                    self.write(i, STATE_FREE)
                    addr = self.total_blocks + (i * BLOCK_SIZE)
                    self.data[addr:addr + BLOCK_SIZE] = bytes(BLOCK_SIZE)
                    self.used -= BLOCK_SIZE
                else:
                    # Stop searching for tails.
                    clear_tail = False

            # Revert marked blocks back to heads.
            if self.read(i) == STATE_MARK:
                self.write(i, STATE_HEAD)

