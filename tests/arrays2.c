int main() {
    int a[5];
    int i;
    int s;
    int t;

    for (i = 0; i < 5; i = i + 1)
        a[i] = i * i;
    s = 0;
    for (i = 0; i < 5; i = i + 1)
        s = s + a[i];
    print(s);
    print(a[2]);

    a[2] = a[2] + a[3];
    print(a[2]);
    t = a[4];
    return t;
}
