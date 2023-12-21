def float_to_string(number: float) -> str:
    counter = 1

    while True:
        new_number = number * 10
        print(new_number)
        round_number = round(number * 10)
        number = new_number
        if not new_number - round_number:
            break
        counter += 1

    res: list[str] = []
    while True:
        res.insert(0, chr(ord("0") + int(number % 10)))
        number = number // 10
        if not number:
            break
    res.insert(-counter, ".")
    return "".join(res)


def float_to_string_1(number):
    if number < 0:
        sign = "-"
        number = -number
    else:
        sign = ""

    # Получаем целую и десятичную части числа
    integer_part = int(number)
    decimal_part = number - integer_part

    # Конвертируем целую часть в строку
    integer_str = ""
    if integer_part == 0:
        integer_str = "0"
    while integer_part > 0:
        digit = integer_part % 10
        integer_str = chr(ord("0") + digit) + integer_str
        integer_part //= 10

    # Конвертируем десятичную часть в строку
    decimal_str = ""
    precision = 6  # Количество знаков после запятой
    while precision > 0:
        decimal_part *= 10
        digit = int(decimal_part)
        decimal_str += chr(ord("0") + digit)
        decimal_part -= digit
        precision -= 1

    # Собираем конечную строку
    result = sign + integer_str
    if decimal_str:
        result += "." + decimal_str

    return result


# Пример использования
float_number = 123.457
string_number = float_to_string(float_number)
print(string_number)
