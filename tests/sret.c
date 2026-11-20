struct Point {
    int x;
    int y;
};

struct Line {
    struct Point a;
    struct Point b;
};

struct Point make(int x, int y) {
    struct Point p;
    p.x = x;
    p.y = y;
    return p;
}

struct Point shift(struct Point p, int d) {
    struct Point r;
    r.x = p.x + d;
    r.y = p.y + d;
    return r;
}

struct Point shift2(struct Point p, int d) {
    return shift(p, d);
}

struct Line line(struct Point a, struct Point b) {
    struct Line l;
    l.a = a;
    l.b = b;
    return l;
}

int main() {
    struct Point a;
    struct Point b;
    struct Point c;
    struct Line l;

    a = make(3, 4);
    print(a.x);
    print(a.y);

    b = shift(a, 10);
    print(b.x);
    print(b.y);

    c = shift2(a, 20);
    print(c.x);
    print(c.y);

    l = line(a, b);
    print(l.a.x);
    print(l.b.y);

    l.a = make(7, 8);
    print(l.a.x);
    print(l.a.y);

    return a.x + b.y;
}
