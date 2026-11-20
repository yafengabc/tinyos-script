CC ?= gcc
CFLAGS ?= -std=gnu11 -O2 -Wall -Iinclude
BUILD := build

.PHONY: all test clean

all: $(BUILD)/csc3 $(BUILD)/rirvm

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/csc3: src/csc3.c include/lib.h | $(BUILD)
	$(CC) $(CFLAGS) src/csc3.c -o $@

$(BUILD)/rirvm: src/rirvm.c include/lib.h | $(BUILD)
	$(CC) $(CFLAGS) src/rirvm.c -o $@

test: all
	python tools/test.py

clean:
	rm -rf $(BUILD)
