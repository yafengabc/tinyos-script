/* Division semantics shared by csc, rvm and rcc (issue #2). */
int main() {
    int min = 0 - 2147483647 - 1;
    print(min / (0 - 1));        /* -2147483648, no overflow trap */
    print(min % (0 - 1));        /* 0 */
    print(7 / 0);                /* 0 */
    print(7 % 0);                /* 0 */
    return 0;
}
