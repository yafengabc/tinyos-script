int main() {
    int x;
    int y;
    int unused;

    x = 2 + 3 * 4;
    y = (10 - 2) / 4;
    unused = 100 + 200;
    if (x == 14)
        y = y + 1;
    print(x);
    print(y);
    return x + y;
}
