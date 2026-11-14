"""
Modulo de dados para el bloque 3.

Este archivo existe para practicar imports: `bloque3.py` lo importa con `import dice`.
Un archivo .py es un modulo; importarlo lo ejecuta UNA vez y deja disponibles
sus nombres (funciones, constantes, clases).
"""

import random

# Constante del modulo (MAYUSCULAS por convencion). Se accede como dice.STANDARD_DICE
STANDARD_DICE = (4, 6, 8, 10, 12, 20, 100)


def roll(sides: int = 20) -> int:
    """Tira un dado de `sides` caras y devuelve el resultado (1..sides)."""
    return random.randint(1, sides)


def roll_with_advantage(sides: int = 20) -> int:
    """Tira dos veces y se queda con el mayor (regla de ventaja de 5e)."""
    return max(roll(sides), roll(sides))


# Ejercicio 4 del bloque 3: implementa aqui `roll_many(count, sides)`.


# Este bloque corre SOLO si ejecutas `python3 aterrizaje/dice.py` directamente.
# Cuando bloque3.py hace `import dice`, __name__ vale "dice" y esto NO corre.
if __name__ == "__main__":
    print("Probando el modulo dice:", roll(), roll_with_advantage())
