struct P {
    int x;
    int y;
};

int total;
int table[6];
char name[16];

int clamp(int v, int lo, int hi) {
    if (v < lo)
        return lo;
    if (v > hi)
        return hi;
    return v;
}

int sq(int v) {
    return v * v;
}

int dist(struct P a, struct P b) {
    int dx;
    int dy;

    dx = a.x - b.x;
    dy = a.y - b.y;
    return sq(dx) + sq(dy);
}

int fill(int base) {
    int i;

    for (i = 0; i < 6; i = i + 1)
        table[i] = clamp(base + i * i, 0, 50);
    return i;
}

int sumtab() {
    int i;
    int s;

    s = 0;
    for (i = 0; i < 6; i = i + 1)
        s = s + table[i];
    return s;
}

int scale(int v, float f) {
    if (f > 1.0)
        return v * 4;
    return v * 2;
}

int main() {
    struct P a;
    struct P b;
    int n;
    float f;

    a.x = 1;
    a.y = 2;
    b.x = 4;
    b.y = 6;
    total = dist(a, b);
    print(total);

    n = fill(7);
    print(n);
    print(sumtab());
    print(table[0]);
    print(table[5]);

    strlcpy(name, "mixbig", 16);
    print(name);
    printf("\n");
    print(strlen(name));
    printf("\n");

    f = 1.25;
    print(scale(3, f));
    total = total + sumtab() + scale(3, f);
    print(total);
    return total % 100;
}
