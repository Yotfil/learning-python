"""
Aterrizaje de Python - Bloque 3
Clases, dataclasses, excepciones, modulos y async/await.

Ejecutalo desde la raiz del repo:
    python3 aterrizaje/bloque3.py
"""

# Los imports van siempre al inicio del archivo, en tres grupos separados por una
# linea en blanco: libreria estandar, paquetes de terceros, modulos propios.
import asyncio
import time
from dataclasses import dataclass, field

import dice  # modulo propio: el archivo aterrizaje/dice.py


# =====================================================================
# 1. CLASES
# =====================================================================
# Una clase agrupa datos (atributos) y comportamiento (metodos) en un mismo
# objeto. En el bloque 2 el personaje era un diccionario; ahora es una clase
# que SABE recibir dano, curarse, etc. No hay `new`: se llama la clase.


class Character:
    """Un personaje jugador con puntos de vida."""

    # Atributo de CLASE: compartido por todas las instancias.
    max_level = 20

    def __init__(self, name: str, hp_max: int, level: int = 1) -> None:
        # __init__ es el inicializador (lo mas cercano al constructor).
        # `self` es la instancia que se esta creando. Todo lo que cuelgues de
        # self es un atributo de INSTANCIA, propio de cada personaje.
        self.name = name
        self.hp_max = hp_max
        self.hp_current = hp_max
        self.level = level

    # Todo metodo recibe `self` como primer parametro. Python convierte
    # hero.take_damage(5) en Character.take_damage(hero, 5). Por eso nunca hay
    # confusion sobre que es `self` (a diferencia de `this` en JS).
    def take_damage(self, damage: int) -> None:
        self.hp_current = max(self.hp_current - damage, 0)

    def heal(self, amount: int) -> None:
        self.hp_current = min(self.hp_current + amount, self.hp_max)

    # @property convierte un metodo en un atributo calculado: se lee como
    # hero.is_alive, SIN parentesis. Equivale a un getter de JS.
    @property
    def is_alive(self) -> bool:
        return self.hp_current > 0

    @property
    def status(self) -> str:
        if self.hp_current <= 0:
            return "Inconsciente"
        if self.hp_current < self.hp_max / 2:
            return "Herido"
        return "Sano"

    # Metodos "dunder" (double underscore): protocolos que conectan tu clase
    # con el lenguaje. __repr__ define que muestra print() y la consola.
    def __repr__(self) -> str:
        return f"Character(name={self.name!r}, hp={self.hp_current}/{self.hp_max})"

    # __eq__ define el operador ==. Sin el, dos personajes solo son iguales si
    # son EL MISMO objeto en memoria.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return NotImplemented
        return self.name == other.name


hero = Character("Yotfil", hp_max=28, level=4)
hero.take_damage(20)
print(hero)  # usa __repr__
print(hero.status, hero.is_alive)
print(hero == Character("Yotfil", 10))  # True: __eq__ compara por nombre
print(Character.max_level, hero.max_level)  # el atributo de clase se ve desde ambos


# --- Herencia ---------------------------------------------------------
# class Hija(Padre). super() da acceso a la implementacion del padre.


class Warlock(Character):
    """Un personaje con puntos de pacto (spell slots simplificados)."""

    def __init__(self, name: str, hp_max: int, level: int = 1) -> None:
        super().__init__(name, hp_max, level)  # inicializa la parte "Character"
        self.pact_slots = 2

    def cast(self, spell: str) -> str:
        if self.pact_slots == 0:
            return f"{self.name} no tiene espacios de conjuro"
        self.pact_slots -= 1
        return f"{self.name} lanza {spell} (quedan {self.pact_slots})"

    # Sobrescribir un metodo: misma firma, nueva implementacion.
    def __repr__(self) -> str:
        return f"Warlock(name={self.name!r}, slots={self.pact_slots})"


yotfil = Warlock("Yotfil", hp_max=28, level=4)
print(yotfil.cast("Eldritch Blast"))
print(yotfil.cast("Hex"))
print(yotfil.cast("Hex"))
print(yotfil, yotfil.is_alive)  # hereda is_alive, take_damage, etc.
print(isinstance(yotfil, Character))  # True: un Warlock ES un Character


# =====================================================================
# 2. DATACLASSES
# =====================================================================
# Cuando una clase es principalmente "datos con nombre", escribir __init__,
# __repr__ y __eq__ a mano es repetitivo. @dataclass los genera a partir de
# los type hints. Pydantic (que usaremos en FastAPI) funciona igual, pero
# ademas VALIDA los tipos en tiempo de ejecucion.


@dataclass
class Monster:
    index: str  # campos obligatorios primero...
    name: str
    challenge_rating: float
    hp: int
    # ...y los opcionales despues. Para valores por defecto MUTABLES (listas,
    # dicts) se usa field(default_factory=...) y no `= []`, por el bug de los
    # defaults compartidos (notas, seccion 3).
    tags: list[str] = field(default_factory=list)

    # Puedes agregar metodos y properties igual que en una clase normal.
    @property
    def is_boss(self) -> bool:
        return self.challenge_rating >= 5


goblin = Monster("goblin", "Goblin", challenge_rating=0.25, hp=7, tags=["humanoid"])
dragon = Monster("young-red-dragon", "Young Red Dragon", 10.0, 178)

print(goblin)  # __repr__ generado
print(goblin == Monster("goblin", "Goblin", 0.25, 7, ["humanoid"]))  # __eq__ generado
print(dragon.is_boss, goblin.is_boss)


# frozen=True hace la instancia inmutable: asignar un atributo lanza error.
# Util para valores que no deberian cambiar (coordenadas, configuracion).
@dataclass(frozen=True)
class Position:
    x: int
    y: int


start = Position(0, 0)
# start.x = 5   -> dataclasses.FrozenInstanceError


# =====================================================================
# 3. EXCEPCIONES
# =====================================================================
# En Python las excepciones son el mecanismo normal para senalar errores.
# Se lanzan con `raise` y se capturan con `try/except`.


def parse_level(text: str) -> int:
    """Convierte texto a nivel (1..20). Lanza ValueError si no es valido."""
    level = int(text)  # int("abc") lanza ValueError por si solo
    if not 1 <= level <= 20:
        raise ValueError(f"nivel fuera de rango: {level}")
    return level


# Estructura completa. Captura SIEMPRE tipos concretos, nunca `except:` pelado.
for raw in ["4", "abc", "99"]:
    try:
        level = parse_level(raw)
    except ValueError as error:  # `as` guarda la excepcion en una variable
        print(f"'{raw}' invalido -> {error}")
    else:  # solo si NO hubo excepcion
        print(f"'{raw}' ok -> nivel {level}")
    finally:  # siempre, haya o no error
        pass  # aqui se cierran recursos, etc.


# Excepciones propias: una clase que hereda de Exception. Permiten a quien
# llama distinguir TUS errores de los del sistema. En FastAPI se mapean a
# codigos HTTP (404, 409...).
class NotEnoughSlotsError(Exception):
    """Se lanza al intentar conjurar sin espacios disponibles."""


def cast_or_raise(caster: Warlock, spell: str) -> str:
    if caster.pact_slots == 0:
        raise NotEnoughSlotsError(f"{caster.name} no tiene espacios para {spell}")
    caster.pact_slots -= 1
    return f"{caster.name} lanza {spell}"


try:
    cast_or_raise(yotfil, "Hex")  # yotfil ya gasto sus 2 slots arriba
except NotEnoughSlotsError as error:
    print("Error controlado:", error)


# EAFP (Easier to Ask Forgiveness than Permission): intenta y maneja el error,
# en vez de verificar antes. Es el estilo preferido en Python.
inventory = {"espada": 1}
try:
    inventory["pocion"] -= 1
except KeyError:
    print("No tienes pociones")


# =====================================================================
# 4. MODULOS E IMPORTS
# =====================================================================
# Arriba hicimos `import dice`. Python busco un archivo dice.py en la carpeta
# del script (aterrizaje/) y en sys.path, lo EJECUTO una vez, y guardo el
# modulo. Sus nombres se usan con el prefijo `dice.`:

print("d20:", dice.roll())
print("d20 con ventaja:", dice.roll_with_advantage())
print("dados estandar:", dice.STANDARD_DICE)

# `from dice import roll` traeria el nombre directo (sin prefijo). Es comodo,
# pero con prefijo queda claro de donde viene cada cosa. Evita `import *`.
#
# Observa que el `if __name__ == "__main__":` de dice.py NO se ejecuto al
# importarlo. Pruebalo: `python3 aterrizaje/dice.py` si lo corre.


# =====================================================================
# 5. ASYNC / AWAIT
# =====================================================================
# Python es sincrono por defecto: no hay event loop corriendo. Lo arrancas
# tu con asyncio.run() y decides que funciones son `async def` (corrutinas).
#
# Regla de oro: dentro de `async def` NUNCA uses funciones bloqueantes
# (time.sleep, requests.get, consultas sincronas a BD). Congelan TODO el loop.
# Usa sus versiones async (asyncio.sleep, httpx, SQLAlchemy async).


async def fetch_monster(index: str, delay: float) -> dict:
    """Simula una peticion HTTP a la API de D&D que tarda `delay` segundos."""
    await asyncio.sleep(delay)  # cede el control al loop mientras "espera"
    return {"index": index, "name": index.replace("-", " ").title()}


async def sequential() -> list[dict]:
    """Una peticion tras otra: el tiempo total es la SUMA."""
    goblin = await fetch_monster("goblin", 0.3)
    orc = await fetch_monster("orc", 0.3)
    return [goblin, orc]


async def concurrent() -> list[dict]:
    """Las dos a la vez con gather (como Promise.all): el tiempo es el MAXIMO."""
    return await asyncio.gather(
        fetch_monster("goblin", 0.3),
        fetch_monster("orc", 0.3),
    )


async def main() -> None:
    start = time.perf_counter()
    await sequential()
    print(f"secuencial: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    monsters = await concurrent()
    print(f"concurrente: {time.perf_counter() - start:.2f}s -> {monsters}")

    # Llamar una corrutina NO la ejecuta: devuelve un objeto corrutina.
    # (En JS, llamar una funcion async si la arranca.) Hay que await-earla.
    pending = fetch_monster("kobold", 0)
    print(type(pending).__name__)  # 'coroutine', todavia no corrio
    print(await pending)  # ahora si


# asyncio.run arranca el event loop, ejecuta main() hasta terminar y lo cierra.
# Solo se llama UNA vez, en el punto de entrada. En FastAPI esto lo hace
# Uvicorn por ti: tu solo escribes `async def` en los endpoints.
asyncio.run(main())


# =====================================================================
# EJERCICIOS
# =====================================================================

# Ejercicio 1 - Clase Party
# Crea una clase `Party` que reciba en __init__ un nombre y empiece con una
# lista vacia de miembros (Character). Dale:
#   - un metodo `add(character)` que agregue un personaje,
#   - una property `average_level` que devuelva el nivel promedio (float),
#   - una property `alive` que devuelva la lista de miembros con is_alive True,
#   - __len__ para que len(party) devuelva la cantidad de miembros,
#   - __repr__ con el nombre y la cantidad de miembros.
# Crea un grupo con 3 personajes, deja a uno en 0 PV y prueba todo.


# Ejercicio 2 - Dataclass Encounter
# Crea una dataclass `Encounter` con `name: str`, `monsters: list[Monster]`
# (default_factory) y `difficulty: str = "medium"`.
# Agregale una property `total_hp` que sume los hp de todos los monstruos y un
# metodo `bosses()` que devuelva solo los monstruos con is_boss True.
# Pruebala con goblin y dragon.


# Ejercicio 3 - Excepcion propia
# Define `class CharacterDeadError(Exception)`. Modifica `Character.heal` (o
# crea una subclase) para que lance CharacterDeadError si hp_current es 0:
# un personaje inconsciente no se cura con una pocion normal.
# Captura la excepcion con try/except y muestra el mensaje.
# Despues llama heal sobre un personaje vivo y confirma que funciona.


# Ejercicio 4 - Modulo
# En aterrizaje/dice.py escribe `roll_many(count: int, sides: int) -> list[int]`
# que devuelva una lista con `count` tiradas. Importala aqui y usala para
# simular los 4 PV iniciales de un grupo con 4d8. Imprime las tiradas y la suma.
# Pista: list comprehension con range(count).


# Ejercicio 5 (reto) - Async con gather
# Escribe `async def fetch_party_monsters(indexes: list[str]) -> list[dict]`
# que lance fetch_monster para cada index (delay 0.2) de forma CONCURRENTE
# con asyncio.gather y devuelva la lista. Ejecutala con asyncio.run para
# ["goblin", "orc", "kobold", "bugbear"] y mide con time.perf_counter que
# tarda ~0.2s y no ~0.8s.
# Pista: gather recibe las corrutinas separadas por coma; para pasarle una
# lista usa el operador * para "esparcirla": asyncio.gather(*corrutinas).
