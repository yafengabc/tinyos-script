struct P {
    int x;
    int y;
};

struct P mk(int x, int y) {
    struct P p;
    p.x = x;
    p.y = y;
    return p;
}

int main() {
    struct P p;
    char b[8];
    string s;
    int i;
    float f;

    p = mk(3, 4);
    strlcpy(b, "n=", 8);
    print(b);
    print(p.x + p.y);

    f = 0.5;
    for (i = 0; i < 3; i = i + 1)
        f = f + 0.5;
    print(f);

    s = "ok";
    print(s);
    printf("\n");
    return p.y;
}
