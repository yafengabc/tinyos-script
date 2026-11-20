int sum(int n) {
    if (n == 0)
        return 0;
    return n + sum(n - 1);
}

int main() {
    print(sum(25));
    return sum(10);
}
