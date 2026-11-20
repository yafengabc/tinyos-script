struct P { int x; int y; };
struct P gs[3];
int main() {
    struct P ps[4];
    struct P a;
    struct P q;
    int i;
    for (i = 0; i < 4; i = i + 1) {
        ps[i].x = i;
        ps[i].y = i * 2;
    }
    a.x = 2;
    a.y = 4;
    q = a;
    printf("q=%d\n", q.x + q.y);
    gs[1].x = 7;
    gs[1].y = 8;
    ps[3].x = 10;
    printf("p3=%d\n", ps[3].x + ps[3].y);
    printf("gs=%d\n", gs[1].x + gs[1].y);
    printf("f=%.2f\n", 3.14159);
    printf("f0=%.0f\n", 2.5);
    return q.y;
}
