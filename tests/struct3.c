struct P {
    int x;
    int y;
};

struct Box {
    struct P a;
    struct P b;
    int tag;
};

struct P mk(int x, int y) {
    struct P p;
    p.x = x;
    p.y = y;
    return p;
}

int sum(struct P p) {
    return p.x + p.y;
}

int main() {
    struct Box b;
    struct P p;

    b.a = mk(1, 2);
    b.b = mk(3, 4);
    b.tag = 5;
    print(b.a.x);
    print(b.b.y);
    print(sum(b.a));

    p = b.a;
    print(p.x + p.y);
    return sum(b.b);
}
