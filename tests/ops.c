int hits;

int bump() {
    hits = hits + 1;
    return 1;
}

int comparisons() {
    int a;
    int b;
    int x;

    a = 3;
    b = 5;

    print(a != b);
    print(a != 3);
    print(a <= 3);
    print(b >= a);
    print(a >= b);
    print(!a);
    print(!0);

    x = -5;
    print(x);
    print(-x);
    x = -(2 + 3);
    print(x);
    return 0;
}

int conditions() {
    int a;
    int b;
    float f;

    a = 3;
    b = 5;
    if (a < b && b < 10)
        print(111);
    if (a > b || b == 5)
        print(222);
    if (!(a == b))
        print(333);
    f = 0.5;
    if (f && (f <= 1.0))
        print(555);
    return 0;
}

int logical() {
    int a;
    int b;
    int x;

    a = 3;
    b = 5;
    x = a && b;
    print(x);
    x = 0 && b;
    print(x);
    x = 0 || b;
    print(x);
    x = (a <= b) && (b != a) && !0;
    print(x);
    return 0;
}

int shortcircuit() {
    hits = 0;
    if (0 && bump())
        print(999);
    print(hits);
    if (1 || bump())
        print(444);
    print(hits);
    return 0;
}

int main() {
    int a;
    int b;

    a = 3;
    b = 5;
    comparisons();
    conditions();
    logical();
    shortcircuit();
    return (a != b) + (a <= 3) + (b >= a);
}
