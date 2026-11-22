int main() {
    int x = 1;
    {
        int x = 2;
        print(x);
    }
    print(x);
    return 0;
}
