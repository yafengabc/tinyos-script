int main() {
    char buf[64];
    int n;

    n = capture("/bin/hello", buf, 63);
    if (n < 0)
        n = 0;
    buf[n] = 0;
    print(n > 0);
    print(buf);
    return 0;
}
