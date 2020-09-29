def hoge(vol):
    def a(i):
        return i * 10
    def b(i):
        return i * 100000

    return a if vol > 100 else b

print(hoge(101)(1))
