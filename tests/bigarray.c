/* 600 global words: over rvm's 512-word window, but still valid RIR2.  csc and
 * rcc must accept the image; rvm must name the limit and point at csc -> rcc
 * instead of running a truncated global array. */
int a[300];
int b[300];

int main() {
    a[0] = 1;
    b[0] = 2;
    print(a[0] + b[0]);
    return 0;
}
