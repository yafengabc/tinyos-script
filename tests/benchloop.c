int main() {
    int t0;
    int t1;
    int i;
    int s;

    t0 = uptime();
    i = 0;
    s = 0;
    while (i < 10000000) {
        s = s + i;
        i = i + 1;
    }
    t1 = uptime();
    print(t1 - t0);
    print(s);
    return 0;
}
