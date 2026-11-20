#ifndef TINYOS_SCRIPT_HOST_TYPES_H
#define TINYOS_SCRIPT_HOST_TYPES_H

/* TinyOS user code includes "types.h"; on the host we lean on stdint/stddef
 * and only keep the small helpers the interpreter expects. */
#include <stdint.h>
#include <stddef.h>

#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))

/* The target's lib.h provides sbrk(); the host shim routes it to one arena. */
void *host_sbrk(int bytes);
#define sbrk(n) host_sbrk(n)

#endif /* TINYOS_SCRIPT_HOST_TYPES_H */
