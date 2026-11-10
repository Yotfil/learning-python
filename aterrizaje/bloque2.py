"""
Aterrizaje de Python - Bloque 2
Listas, diccionarios, bucles y funciones.

Como leerlo: cada seccion tiene ejemplos que corren tal cual.
Al final hay ejercicios para que los resuelvas tu. Ejecuta el archivo con:
    python3 aterrizaje/bloque2.py
"""

# =====================================================================
# 1. LISTAS  (equivalente al Array de JS)
# =====================================================================
# Una lista es una coleccion ordenada y mutable. Se escribe con [].

inventory = ["Espada corta", "Pocion de curacion", "Cuerda (15 m)"]

print(inventory[0])  # "Espada corta"  -> los indices empiezan en 0
print(inventory[-1])  # "Cuerda (15 m)" -> indice negativo cuenta desde el final
print(len(inventory))  # 3               -> len() es una funcion, no un .length

inventory.append("Antorcha")  # agrega al final (como push)
inventory.remove("Cuerda (15 m)")  # elimina la primera coincidencia
print("Antorcha" in inventory)  # True -> 'in' revisa si un elemento existe

# Slicing: lista[inicio:fin] devuelve una sub-lista (fin NO se incluye)
print(inventory[0:2])  # los dos primeros elementos


# =====================================================================
# 2. DICCIONARIOS  (equivalente al objeto literal de JS / JSON)
# =====================================================================
# Pares clave -> valor. Las claves suelen ser strings.
# Esto es clave para el proyecto: la API de D&D responde JSON, y en Python
# un JSON se convierte en diccionarios y listas anidados.

character = {
    "name": "Yotfil",
    "class_name": "Warlock",
    "level": 4,
    "hp_current": 12,
    "hp_max": 28,
    "abilities": {  # un diccionario dentro de otro
        "str": 8,
        "dex": 14,
        "con": 12,
        "int": 10,
        "wis": 11,
        "cha": 17,
    },
}

print(character["name"])  # acceso por clave (NO character.name)
print(character["abilities"]["cha"])  # acceso anidado -> 17

# Si la clave no existe, character["race"] lanza un error (KeyError).
# .get() devuelve None (o un valor por defecto) en lugar de fallar:
print(character.get("race"))  # None
print(character.get("race", "Humano"))  # "Humano"

character["race"] = "Tiefling"  # agregar o modificar una clave
print(character.keys())  # todas las claves
print(character.values())  # todos los valores


# =====================================================================
# 3. BUCLES
# =====================================================================
# En Python casi siempre se usa 'for ... in' directamente sobre la coleccion.
# No hay el for clasico con contador (for i = 0; i < n; i++).

print("\n--- Inventario ---")
for item in inventory:
    print(f"- {item}")

# enumerate() te da el indice y el elemento a la vez
for position, item in enumerate(inventory, start=1):
    print(f"{position}. {item}")

# range(n) genera los numeros de 0 a n-1 (util cuando si necesitas contar)
for i in range(3):
    print(f"Tirada {i + 1}")

# Para recorrer un diccionario se usa .items(), que devuelve (clave, valor)
print("\n--- Atributos ---")
for ability, score in character["abilities"].items():
    print(f"{ability.upper()}: {score}")

# while: repite mientras la condicion sea verdadera
hp = 10
rounds = 0
while hp > 0:
    hp -= 4  # hp = hp - 4
    rounds += 1
print(f"\nEl personaje cae inconsciente tras {rounds} rondas")


# =====================================================================
# 4. FUNCIONES
# =====================================================================
# Se definen con 'def'. Los type hints (nombre: tipo) -> tipo_retorno son
# opcionales para Python, pero en el proyecto los usaremos siempre:
# documentan el codigo y FastAPI/Pydantic los aprovechan.


def ability_modifier(score: int) -> int:
    """Calcula el modificador de un atributo segun las reglas de D&D 5e.

    Regla: (puntuacion - 10) dividido entre 2, redondeando hacia abajo.
    El operador // es division entera (redondea hacia abajo).
    """
    return (score - 10) // 2


print(ability_modifier(17))  # 3
print(ability_modifier(8))  # -1


# Parametros con valor por defecto
def heal(hp_current: int, hp_max: int, amount: int = 5) -> int:
    """Cura 'amount' puntos sin pasar del maximo."""
    return min(hp_current + amount, hp_max)


print(heal(12, 28))  # 17  -> usa amount=5 por defecto
print(heal(12, 28, 20))  # 28  -> no supera hp_max
print(heal(12, 28, amount=3))  # 15 -> argumento con nombre, mas legible


# Una funcion puede recibir y devolver diccionarios (muy comun en backend)
def describe(character: dict) -> str:
    """Devuelve una linea con el resumen del personaje."""
    return f"{character['name']} - {character['class_name']} nivel {character['level']}"


print(describe(character))


# =====================================================================
# EJERCICIOS  (escribe tu codigo debajo de cada enunciado)
# =====================================================================

# Ejercicio 1 - Inventario con peso
# Crea una lista llamada `loot` con al menos 4 diccionarios, cada uno con
# las claves "name" (str) y "weight" (float, en kg).
# Luego recorre la lista con un for e imprime cada objeto como:
#     "Espada larga (1.5 kg)"
# Finalmente imprime el peso total del inventario.
loot = [
    {"name": "Two hands Sword", "weight": 5.5},
    {"name": "Rope", "weight": 2.8},
    {"name": "dagger", "weight": 0.8},
    {"name": "bow", "weight": 3.8},
]

total_weight = sum(item["weight"] for item in loot)
# total_weight = 0
for item in loot:
    print(f"{item['name']} ({item['weight']} kg)")

print(f"Peso total: {total_weight} kg")

# Ejercicio 2 - Modificadores del personaje
# Usando el diccionario `character` y la funcion `ability_modifier`,
# recorre character["abilities"] e imprime cada atributo con su modificador,
# mostrando el signo siempre, por ejemplo:
#     "CHA 17 (+3)"   y   "STR 8 (-1)"
# Pista: en un f-string, {valor:+d} imprime el numero con signo.


def show_abilities_with_modifiers(abilities: dict[str, int]) -> None:
    """Imprime cada atributo con su puntuacion y modificador, ej. "CHA 17 (+3)".

    Decisiones:
    - Devuelve None (solo imprime). Una funcion que imprime no deberia tambien
      devolver datos: hace una sola cosa, y el type hint `-> None` lo documenta.
    - No muta `abilities`. La funcion recibe el diccionario para leerlo; si lo
      cambiara, quien la llama veria su personaje alterado sin esperarlo.
    - El signo se resuelve con el format spec `:+d` ("entero, siempre con signo"),
      no concatenando strings. Es la herramienta del lenguaje para eso.
    """
    for ability, score in abilities.items():
        modifier = ability_modifier(score)
        print(f"{ability.upper()} {score} ({modifier:+d})")


show_abilities_with_modifiers(character["abilities"])


# Variante: si lo que quieres es el DATO (no imprimirlo), lo idiomatico es devolver
# un diccionario NUEVO y dejar el original intacto. Esto es una dict comprehension:
#     {CLAVE: VALOR for CLAVE, VALOR_ORIGINAL in ...}
def ability_modifiers(abilities: dict[str, int]) -> dict[str, int]:
    """Devuelve {atributo: modificador} sin tocar el diccionario recibido."""
    return {ability: ability_modifier(score) for ability, score in abilities.items()}


print(ability_modifiers(character["abilities"]))  # {'str': -1, 'dex': 2, ...}


# Ejercicio 3 - Nivel del grupo
# Crea una lista `party` con 3 o 4 diccionarios de personajes (al menos
# "name" y "level"). Escribe una funcion
#     def average_level(party: list[dict]) -> float
# que devuelva el nivel promedio del grupo. Imprime el resultado con un
# decimal. (Esto es exactamente lo que necesitara la sugerencia de
# encuentros en la Fase 2.)
party = [
    {"name": "Zandir", "level": 5},
    {"name": "Marnul", "level": 8},
    {"name": "Irda", "level": 7},
    {"name": "Melkor", "level": 5},
]


def average_level(party: list[dict]) -> float:
    total_level = 0
    for player in party:
        total_level += player["level"]

    return total_level / len(party)


print(f"{average_level(party):.1f}")


# Ejercicio 4 - Recibir dano
# Escribe una funcion
#     def take_damage(character: dict, damage: int) -> dict
# que reste `damage` a "hp_current" sin bajar de 0, y ademas agregue una
# clave "status" con "Sano", "Herido" o "Inconsciente" reutilizando la logica
# del bloque 1. Debe devolver el diccionario modificado.
# Pruebala con el personaje de arriba: take_damage(character, 15).


def take_damage(character: dict, damage: int) -> dict:
    """Aplica `damage` al personaje, actualiza su estado y lo devuelve.

    Decisiones:
    - `max(x, 0)` es la forma idiomatica de "restar sin bajar de cero": devuelve
      el mayor entre la resta y 0. Reemplaza cualquier if/else para acotar.
    - Esta funcion SI muta el diccionario que recibe, y eso esta bien aqui porque
      el nombre (`take_damage`) y el enunciado lo dejan claro: el personaje cambia.
      Devolverlo ademas permite encadenar, ej. print(take_damage(c, 5)).
    - La logica de estado esta en su propia funcion (`hp_status`) para poder
      reutilizarla (hoja de personaje, curaciones, etc.) y probarla por separado.
    """
    character["hp_current"] = max(character["hp_current"] - damage, 0)
    character["status"] = hp_status(character["hp_current"], character["hp_max"])
    return character


def hp_status(hp_current: int, hp_max: int) -> str:
    """Clasifica los PV en "Sano", "Herido" o "Inconsciente" (logica del bloque 1).

    Usa "early return": cada `if` devuelve y sale. Al no haber `else`, el codigo
    queda plano y se lee de arriba a abajo como una tabla de casos.
    Recibe numeros, no el diccionario: asi la funcion no depende de la forma del
    personaje y sirve para cualquier criatura.
    """
    if hp_current <= 0:
        return "Inconsciente"
    if hp_current < hp_max / 2:
        return "Herido"
    return "Sano"


# Nota: `hp_status` se define DESPUES de `take_damage` y aun asi funciona, porque el
# cuerpo de una funcion se evalua al LLAMARLA, no al definirla (notas, seccion 2).
# La llamada de abajo ocurre cuando ambas ya existen.
print(take_damage(character, 15))  # hp_current: 0, status: 'Inconsciente'


# Ejercicio 5 (reto) - Buscar en el inventario
# Escribe una funcion
#     def find_item(loot: list[dict], name: str) -> dict | None
# que devuelva el diccionario cuyo "name" coincida (sin importar mayusculas)
# o None si no existe. Pista: str.lower() y return dentro del for.


def find_item(loot: list[dict], name: str) -> dict | None:
    """Devuelve el primer objeto cuyo "name" coincide (ignorando mayusculas), o None.

    Decisiones:
    - `return` dentro del for: en cuanto hay coincidencia la funcion termina. No
      recorre el resto de la lista ni necesita una variable auxiliar.
    - El `return None` final solo se alcanza si el bucle termino sin coincidir.
      Es la forma explicita de decir "no encontrado"; sin el, la funcion devolveria
      None igual, pero escribirlo documenta la intencion y cuadra con `-> dict | None`.
    - `name.lower()` se calcula una sola vez antes del bucle, no en cada vuelta.
    """
    target = name.lower()
    for item in loot:
        if item["name"].lower() == target:
            return item
    return None


print(find_item(loot, "rope"))     # {'name': 'Rope', 'weight': 2.8}  <- ignora mayusculas
print(find_item(loot, "Sword"))    # None  <- coincidencia exacta, no por subcadena
