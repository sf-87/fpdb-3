from decimal import Decimal

SNG_STRUCTURES = {
    (Decimal('0.41'), Decimal('0.09'), 9): "Turbo",   # 9-max, 27 entries
    (Decimal('0.41'), Decimal('0.09'), 6): "Turbo",   # 6-max, 6 entries
    (Decimal('0.82'), Decimal('0.18'), 9): "Turbo",   # 9-max, 27 entries
    (Decimal('0.84'), Decimal('0.16'), 6): "Turbo",   # 6-max, 6 entries
    (Decimal('2.60'), Decimal('0.40'), 9): "Turbo",   # 9-max, 27 entries
    (Decimal('2.60'), Decimal('0.40'), 6): "Turbo",   # 6-max, 6 entries
    (Decimal('4.46'), Decimal('0.54'), 9): "Turbo",   # 9-max, 27 entries
    (Decimal('4.46'), Decimal('0.54'), 6): "Turbo",   # 6-max, 6 entries
    (Decimal('8.92'), Decimal('1.08'), 9): "Turbo",   # 9-max, 27 entries
    (Decimal('8.92'), Decimal('1.08'), 6): "Turbo",   # 6-max, 6 entries
    (Decimal('17.84'), Decimal('2.16'), 6): "Turbo",  # 6-max, 6 entries
    (Decimal('22.40'), Decimal('2.60'), 9): "Turbo",  # 9-max, 27 entries
    (Decimal('45.00'), Decimal('5.00'), 6): "Turbo"   # 6-max, 6 entries
}
