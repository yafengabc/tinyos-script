int fib(int n) {
    if (n < 2)
        return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int t0;
    int t1;
    int s;

    t0 = uptime();
    s = fib(24);
    t1 = uptime();
    print(t1 - t0);
    print(s);
    return 0;
}
