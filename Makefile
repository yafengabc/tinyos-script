CC ?= gcc
CFLAGS ?= -std=gnu11 -O2 -fwrapv -Wall -Iinclude
BUILD := build

.PHONY: all test clean

all: $(BUILD)/csc $(BUILD)/rvm $(BUILD)/rcc

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/csc: src/csc.c include/lib.h | $(BUILD)
	$(CC) $(CFLAGS) src/csc.c -o $@

$(BUILD)/rvm: src/rvm.c include/lib.h | $(BUILD)
	$(CC) $(CFLAGS) src/rvm.c -o $@

$(BUILD)/rcc: src/rcc/rcc.c src/rcc/rv32.inc include/lib.h | $(BUILD)
	$(CC) $(CFLAGS) -DRCC_ARCH_RV32 src/rcc/rcc.c -o $@

test: all
	python tools/test.py

clean:
	rm -rf $(BUILD)
