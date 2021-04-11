import random as rnd
import rs


encode_msg   = []
received_msg = []
decode_msg   = ''
output       = ''


# Кодирование
def encode(text):
    global encode_msg
    encode_msg = []

    for i in range(len(text)):
        encode_msg.append(rs.encode_16b(text[i]))


# Отправка сообщения
def send():
    global output
    global received_msg
    received_msg = []

    output = 'Передатчик  | Сообщение отправлено\n'
    for i in range(len(encode_msg)):
        if rnd.randint(0, 100) == 0:

            # Передача последовательности с помехой
            noise = list('0'*42)
            noise_pos = rnd.randint(0, 41)
            noise[noise_pos] = '1'
            received_msg.append(format(int(encode_msg[i], 2) ^ int(''.join(noise), 2), '042b'))
            noise_pos //= 3
            output += ('\nКанал связи | Образовалась помеха \'' + ''.join(noise[noise_pos*3:noise_pos*3+3]) +
                       '\' в символе ' + str(i+1) + ' в позиции ' + str(noise_pos+1))

        else:

            # Передача последовательности без помех
            received_msg.append(encode_msg[i])


# Декодирование
def decode():
    global output
    global decode_msg
    decode_msg = ''

    for i in range(len(received_msg)):
        decode_symbol, out = rs.decode_42b(i, received_msg[i])
        decode_msg += decode_symbol
        output += out

    output += '\n\nПриемник    | Сообщение получено'


# Инициализатор отправки сообщения
def start_transfer(text):
    rs.gf_init()

    encode(text)
    send()
    decode()

    return decode_msg, output
