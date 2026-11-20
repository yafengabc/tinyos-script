struct Inner {
    int x;
    int y;
};

struct Outer {
    struct Inner in;
    int z;
};

struct Item {
    struct Inner p;
    int tag;
};

struct Outer g;

int sum(struct Inner v) {
    return v.x + v.y;
}

int main() {
    struct Outer o;
    struct Outer q;
    struct Item arr[2];
    struct Inner t;

    o.in.x = 3;
    o.in.y = 4;
    o.z = 5;
    print(o.in.x);
    print(o.in.y);
    print(o.z);
    print(sum(o.in));

    arr[0].p.x = 7;
    arr[0].p.y = 8;
    arr[0].tag = 9;
    arr[1].p.x = 10;
    arr[1].p.y = 11;
    arr[1].tag = 12;
    print(arr[0].p.x);
    print(arr[1].p.y);
    print(arr[1].tag);
    print(sum(arr[1].p));

    t.x = 20;
    t.y = 21;
    q.in.x = t.x;
    q.in.y = t.y;
    q.z = 22;
    o = q;
    print(o.in.x);
    print(o.in.y);
    print(o.z);

    g.in.x = 30;
    g.in.y = 31;
    g.z = 32;
    print(g.in.x + g.z);
    return o.in.y;
}
