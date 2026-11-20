struct P { int x; int y; };

int main() {
    struct P p;
    struct P ps[2];
    int a[4];
    int i;

    p.x = 1;
    p.x += 2;
    p.x++;
    ++p.x;

    a[1] = 10;
    a[1] += 5;
    a[1]--;
    ++a[1];

    ps[0].x = 3;
    ps[0].x += 4;
    ps[0].x++;
    ++ps[0].x;

    i = 1;
    a[i] *= 2;

    print(p.x);
    print(a[1]);
    print(ps[0].x);
    return p.x + a[1] + ps[0].x;
}
