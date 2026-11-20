int side;

int bump() {
    side = side + 1;
    return 1;
}

int main() {
    int a;
    int b;

    a = 3;
    b = 5;
    print(a <= 3);
    print(a >= 4);
    print(a != b);
    print(!a);
    print(!0);
    print((a < b) && (b < 10));
    print((a > b) || (b == 5));
    print(!(a == b));

    side = 0;
    if (0 && bump())
        print(999);
    print(side);
    if (1 || bump())
        print(7);
    print(side);
    return 0;
}
