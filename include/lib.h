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
#include <io.h>
#include <fcntl.h>
#include <time.h>

#define TOS_STACK(bytes)

#define open(p)        _open((p), _O_RDONLY | _O_BINARY)
#define create(p)      _open((p), _O_CREAT | _O_TRUNC | _O_WRONLY | _O_BINARY, 0644)
#define read(fd,b,n)   _read((fd), (b), (n))
#define write(fd,b,n)  _write((fd), (b), (n))
#define lseek(fd,o,w)  _lseek((fd), (o), (w))
#define close(fd)      _close(fd)

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
static inline int sleep(int ms) { (void)ms; return 0; }

static inline int write_all(int fd, const void *buf, int len)
{
    int done = 0;
    while (done < len) {
        int n = _write(fd, (const char *)buf + done, len - done);
        if (n <= 0)
            return -1;
        done += n;
    }
    return done;
}

#endif /* TINYOS_SCRIPT_HOST_LIB_H */
