#include "lib.h"

/* Host arena behind sbrk() for the legacy py interpreter.  The target gives
 * the process a TOS_HEAP note; the desktop just reserves a fixed region. */
static unsigned char host_heap[2 * 1024 * 1024];
static size_t host_brk;

void *host_sbrk(intptr_t bytes)
{
    size_t need;
    void *p;

    if (bytes < 0)
        return (void *)-1;
    need = ((size_t)bytes + 7u) & ~(size_t)7u;
    if (host_brk + need > sizeof host_heap)
        return (void *)-1;
    p = host_heap + host_brk;
    host_brk += need;
    return p;
}

int host_stat(const char *path, struct tos_stat *st)
{
    FILE *f = fopen(path, "rb");
    long n;

    if (!f)
        return -1;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return -1;
    }
    n = ftell(f);
    fclose(f);
    if (n < 0)
        return -1;
    st->size = (uint32_t)n;
    st->type = TOS_FTYPE_REG;
    return 0;
}
