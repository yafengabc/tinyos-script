int main() {
    int a = 17;
    int b = 5;
    int c;
    int arr[2];

    c = a % b;
    a %= b;
    arr[0] = 17;
    arr[0] %= 5;

    print(c);
    print(a);
    print(arr[0]);
    print(17 % 5);
    return c + a + arr[0];
}
