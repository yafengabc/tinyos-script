int add8(int a, int b, int c, int d, int e, int f, int g, int h) {
    return a + b + c + d + e + f + g + h;
}

int fact(int n) {
    if (n < 2)
        return 1;
    return n * fact(n - 1);
}

int main() {
    print(add8(1, 2, 3, 4, 5, 6, 7, 8));
    print(fact(6));
    print(fact(0));
    return add8(1, 1, 1, 1, 1, 1, 1, 1);
}
