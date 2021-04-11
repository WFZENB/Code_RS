# линейно-блочный код (7, 3) или (21, 9) в битах

# правило понижения степени
# a^3 = a^1 + a^0

# элементы поля
#      4      2      1      6      3      7      5
#     a^0    a^1    a^2    a^3,   a^4    a^5    a^6
a = (0b100, 0b010, 0b001, 0b110, 0b011, 0b111, 0b101)

f     = []
f_inv = []
ht    = []
out   = ''


# ----------------------------------------
# Базовые операции


# Элемент по степени
def get_a(p):
    return a[p % len(a)]


# Степень по элементу
def get_pow(a1):
    return a.index(a1)


# Произведение
def gf_mul(a1, a2):
    if a1 == 0 or a2 == 0:
        return 0
    return get_a(a.index(a1) + a.index(a2))


# Деление на 7
def gf_div7(a1):
    return get_a(abs(a.index(a1) - 7))


# Произведение полинома на матрицу
def mul_pol_mat(pl, mx):
    pol = []

    for i in range(len(mx[0])):
        ls = 0
        for j in range(len(mx)):
            ls ^= gf_mul(pl[j], mx[j][i])
        pol.append(ls)
    return pol


# Сумма значений полинома
def poly_sum(pl):
    ls = 0
    for i in range(len(pl)):
        ls += pl[i]
    return ls


# ----------------------------------------
# Определеие матриц и операции над РС кодом


# Генерация квадратной порождающей матрицы
def gen_f():
    global f
    f = []
    d = 0

    for i in range(len(a)):
        line = [a[0]]
        for j in range(1, len(a), 1):
            line.append(gf_mul(line[j-1], a[d]))
        f.append(line)
        d += 1


# Генерация обратной порождающей матрицы
def gen_f_inv():
    global f_inv
    f_inv = list(map(list, zip(*f)))

    for i in range(len(a)):
        for j in range(len(a)):
            f_inv[i][j] = gf_div7(f_inv[i][j])


# Генерация проверочной транспонированной марицы
def gen_ht():
    global ht
    ht = []

    for i in range(len(a)):
        line = []
        for j in range(3, 7, 1):
            line.append(f_inv[i][j])
        ht.append(line)


# Инициализация матриц
def gf_init():
    gen_f()
    gen_f_inv()
    gen_ht()


# Вычисление информационного полинома
def mk_inf_poly(inf_vec):
    inf_vec += [0]*4
    return mul_pol_mat(inf_vec, f)


# Коррекция ошибки
def correct(bp, inf_poly, syndrome, err_pos):
    global out

    if err_pos <= 0:
        err_pos = abs(err_pos)
    else:
        err_pos = 7 - err_pos

    out += ' в позиции ' + str(bp + err_pos)
    corr = ht[err_pos]
    ma = corr[0]
    mc = syndrome[0]
    k = a[get_pow(mc) - get_pow(ma)]

    inf_poly[err_pos] ^= k

    msg = mul_pol_mat(inf_poly, f_inv)[:3]
    bits = format(msg[0], '03b') + format(msg[1], '03b') + format(msg[2], '03b')
    return bits


# ----------------------------------------
# Кидирование / декодирование


# Кодирование 9-битных последовательностей
def encode_9b(bits):
    inf_poly = mk_inf_poly([int(bits[:3], 2), int(bits[3:6], 2), int(bits[6:], 2)])
    bits = ''
    for i in range(len(inf_poly)):
        bits += format(inf_poly[i], '03b')
    return bits


# Разбивка символа на две последовательности по 9 бит (8 бит + '0')
def encode_16b(symbol):
    symbol = format(ord(symbol), '016b')
    return encode_9b(symbol[:8]+'0') + encode_9b(symbol[8:]+'0')


# Декодирование 21-битной последовательности
def decode_21b(id, bp, bits):
    global out

    # Формирование информационного полинома
    inf_poly = []
    for i in range(0, len(bits), 3):
        inf_poly.append(int(bits[i:i+3], 2))

    # Вычисление синдрома ошибок
    syndrome = mul_pol_mat(inf_poly, ht)

    if poly_sum(syndrome) == 0:

        # Декодирование
        msg_poly = mul_pol_mat(inf_poly, f_inv)[:3]
        msg_bits = ''
        for i in range(len(msg_poly)):
            msg_bits += format(msg_poly[i], '03b')
        return msg_bits

    else:

        # Определение и исправление ошибок
        mp = 7
        for i in range(len(syndrome) - 1):
            p = get_pow(syndrome[i + 1]) - get_pow(syndrome[i])
            if p > 0:
                p = -7 + p
            if mp == 7:
                mp = p
            elif p != mp:
                out += 'Обнаружена n-кратная ошибка'
                break
            elif i == (len(syndrome) - 2):
                out += '\nПриемник    | Обнаружена 1-кратная ошибка в символе ' + str(id+1)
                return correct(bp, inf_poly, syndrome, mp)


# Декодирование 42-битной последовательности
def decode_42b(id, bits):
    global out
    out = ''
    return chr(int((decode_21b(id, 1, bits[:21])[:-1] + decode_21b(id, 8, bits[21:])[:-1]), 2)), out