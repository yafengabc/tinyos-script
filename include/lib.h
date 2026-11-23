#ifndef TINYOS_SCRIPT_HOST_LIB_H
#define TINYOS_SCRIPT_HOST_LIB_H

/* Host shim for the TinyOS user API used by csc3 and rirvm.  The shipped
 * target build uses user/lib.h; this file only exists so the compiler and VM
 * can be built and tested on a desktop. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <time.h>
#if defined(_WIN32)
#include <io.h>
#else
#include <unistd.h>
#endif

#define TOS_STACK(bytes)
#define TOS_HEAP(bytes)
#define sbrk(n) host_sbrk(n)
void *host_sbrk(intptr_t bytes);

/* Minimal TinyOS stat(): py only checks regular file and size.
 *
 * The type is `tos_stat_t`, not `struct stat`: glibc's <fcntl.h> already owns
 * that tag.  The target build gets the same typedef from TinyOS user/lib.h
 * (over include/tos_abi.h's struct stat), so src/rvm.c compiles in both
 * trees.  Keep the two typedefs in sync - tools/test.py cannot see the target
 * one; tools/check_target_build.py does. */
#define TOS_FTYPE_REG 0
#define TOS_FTYPE_DIR 1
#define TOS_FTYPE_CHR 2
typedef struct tos_stat {
    uint32_t size;
    uint8_t type;
} tos_stat_t;
int host_stat(const char *path, tos_stat_t *st);
#define stat(p, st) host_stat((p), (st))

#if defined(_WIN32)
#define open(p)        _open((p), _O_RDONLY | _O_BINARY)
#define create(p)      _open((p), _O_CREAT | _O_TRUNC | _O_WRONLY | _O_BINARY, 0644)
#define read(fd,b,n)   _read((fd), (b), (n))
#define write(fd,b,n)  _write((fd), (b), (n))
#define lseek(fd,o,w)  _lseek((fd), (o), (w))
#define close(fd)      _close(fd)
#else
/* POSIX open() takes flags, but the TinyOS user API calls open(path).  The
 * inner open is not re-expanded (the preprocessor suppresses recursion), so
 * this forwards to the real function with O_RDONLY. */
#define open(p)        open((p), O_RDONLY)
#define create(p)      (open)((p), O_CREAT | O_TRUNC | O_WRONLY, 0644)
#endif

/* TinyOS puts() writes bytes only; stdio puts() appends a newline. */
#define puts(s)        fputs((s), stdout)

static inline int putint(int v)
{
    return printf("%d", v);
}

static inline int uptime(void)
{
    return (int)(clock() * 1000 / CLOCKS_PER_SEC);
}

/* Peripheral stubs: the host has no GPIO/ADC/PWM, but scripts must link and
 * exercise the same native calls. */
static int host_gpio[64];
static inline int gpio_count(void) { return 8; }
static inline int gpio_mode(int pin, int mode) { (void)pin; (void)mode; return 0; }
static inline int gpio_write(int pin, int value)
{
    if (pin >= 0 && pin < 64) host_gpio[pin] = value ? 1 : 0;
    return 0;
}
static inline int gpio_read(int pin) { return (pin >= 0 && pin < 64) ? host_gpio[pin] : 0; }
static inline int adc_count(void) { return 1; }
static inline int adc_read(int chan) { (void)chan; return 2048; }
static inline int pwm_count(void) { return 4; }
static inline int pwm_set(int gpio, int hz, int duty) { (void)gpio; (void)hz; (void)duty; return 0; }
static inline int pwm_off(int gpio) { (void)gpio; return 0; }
/* Host stubs for the two new script natives. */
#define POLLIN 0x001
struct pollfd { int fd; short events; short revents; };
static inline int poll(struct pollfd *p, int n, int t) { (void)p; (void)n; (void)t; return 0; }
static inline int yield(void) { return 0; }

static inline int tos_sleep_ms(int ms) { (void)ms; return 0; }
/* Native NAT_SLEEP: the host shim never really sleeps.  A macro avoids the
 * POSIX sleep(unsigned seconds) signature clash. */
#define sleep(ms) tos_sleep_ms(ms)

static inline int write_all(int fd, const void *buf, int len)
{
    int done = 0;
    while (done < len) {
        int n = write(fd, (const char *)buf + done, len - done);
        if (n <= 0)
            return -1;
        done += n;
    }
    return done;
}

#endif /* TINYOS_SCRIPT_HOST_LIB_H */
