"""ЛР № 12, вариант 7: расписание на 2 машинах (минимизация времени завершения Cmax).
Точный метод — полный перебор; эвристика — наибольшая длительность первой (LPT); локальный поиск — перенос работы; М7."""
import math
import os
import random
import statistics
import time

DIR = os.path.dirname(os.path.abspath(__file__))


def makespan(t, assign):                         # Cmax = нагрузка самой загруженной из двух машин
    s1 = sum(x for x, a in zip(t, assign) if a)
    return max(s1, sum(t) - s1)


def brute_force(t):                              # полный перебор 2^(n−1) назначений (работа 0 — на машине 0)
    n, total, best = len(t), sum(t), float("inf")
    for mask in range(1 << (n - 1)):
        s1 = sum(t[i + 1] for i in range(n - 1) if mask >> i & 1)
        best = min(best, max(s1, total - s1))
    return best


def list_schedule(t, order):                     # каждая следующая работа — на менее загруженную машину
    load, assign = [0, 0], [0] * len(t)
    for i in order:
        m = 0 if load[0] <= load[1] else 1
        assign[i], load[m] = m, load[m] + t[i]
    return assign


def lpt(t):                                      # наибольшая длительность первой
    return list_schedule(t, sorted(range(len(t)), key=lambda i: -t[i]))


def move_search(t, assign):                      # локальный поиск: переносим работу, пока Cmax уменьшается
    assign, improved = assign[:], True
    while improved:
        improved = False
        for i in range(len(t)):
            old = makespan(t, assign)
            assign[i] ^= 1
            if makespan(t, assign) < old:
                improved = True
            else:
                assign[i] ^= 1
    return assign


def main():
    print(f"{'n':>3}{'вариантов':>11}{'перебор, с':>12}")      # 1. рост времени полного перебора
    rows, n = [], 10
    while True:
        t = [random.Random(n).randint(1, 100) for _ in range(n)]
        t0 = time.perf_counter(); brute_force(t); dt = time.perf_counter() - t0
        rows.append((n, dt))
        print(f"{n:>3}{2 ** (n - 1):>11}{dt:>12.4f}")
        if dt > 10:
            break
        n += 1
    ok = [r[0] for r in rows if r[1] <= 10]
    print("Предельное n при ограничении 10 с:", max(ok))

    print(f"\n{'n':>3}{'LPT, %':>9}{'LPT+перенос, %':>16}{'случ.+перенос, %':>18}{'оптимум достигнут (LPT+пер.)':>31}")
    for n in (10, 12, 14, 16, 18):               # 2. качество на 30 наборах данных
        d1, d2, d3, hits = [], [], [], 0
        for s in range(30):
            rng = random.Random(1000 * n + s)
            t = [rng.randint(1, 100) for _ in range(n)]
            opt = brute_force(t)
            a = lpt(t)
            c1 = makespan(t, a)
            c2 = makespan(t, move_search(t, a))
            c3 = makespan(t, move_search(t, [rng.randint(0, 1) for _ in t]))
            d1.append((c1 - opt) / opt * 100); d2.append((c2 - opt) / opt * 100); d3.append((c3 - opt) / opt * 100)
            hits += c2 == opt
        print(f"{n:>3}{statistics.mean(d1):>9.2f}{statistics.mean(d2):>16.2f}{statistics.mean(d3):>18.2f}{hits / 30 * 100:>30.0f}%")

    N = 300                                      # 3. большая размерность
    rng = random.Random(7)
    t = [rng.randint(1, 100) for _ in range(N)]
    lb = max(math.ceil(sum(t) / 2), max(t))      # нижняя оценка оптимума
    rnd = [rng.randint(0, 1) for _ in t]
    print(f"\nN = {N}, сумма длительностей {sum(t)}, нижняя оценка оптимума {lb}")
    res = {}
    for name, f in (("Случайное назначение", lambda: rnd), ("По порядку (без сортировки)", lambda: list_schedule(t, range(N))),
                    ("LPT", lambda: lpt(t)), ("LPT + перенос", lambda: move_search(t, lpt(t))),
                    ("Случайное + перенос", lambda: move_search(t, rnd))):
        t0 = time.perf_counter(); a = f(); dt = time.perf_counter() - t0
        res[name] = makespan(t, a)
        print(f"  {name:<28} Cmax {res[name]:>5}  ({(res[name] - lb) / lb * 100:5.2f} % над нижней оценкой), время {dt:.4f} с")

    # М7: прикладная постановка — распределение заказов между двумя станками (длительности в часах), 250 смен в год
    cost, days = 1500, 250                       # условная стоимость машино-часа, руб.; рабочих дней в году
    for base in ("Случайное назначение", "По порядку (без сортировки)"):
        gain = res[base] - res["LPT + перенос"]
        print(f"М7: замена «{base}» на LPT + перенос: выигрыш {gain} ч за цикл, за год {gain * days} ч ≈ "
              f"{format(gain * days * cost, ',').replace(',', ' ')} руб.")

    try:
        import matplotlib.pyplot as plt
        plt.semilogy([r[0] for r in rows], [r[1] for r in rows], "o-")
        plt.xlabel("n"); plt.ylabel("Время перебора, с"); plt.title("Полный перебор (лог. шкала)"); plt.grid(True, which="both")
        plt.savefig(os.path.join(DIR, "brute_time.png"), dpi=150)
        print("График сохранён в:", DIR)
        plt.show()
    except ImportError:
        print("Установите matplotlib: pip install matplotlib")


if __name__ == "__main__":
    main()
