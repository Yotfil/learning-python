# Cómo funciona Python (para alguien que viene de JavaScript)

Notas del aterrizaje. Cada sección explica un detalle del lenguaje que cambia la forma
de escribir código, con la comparación a JavaScript cuando ayuda. Los ejemplos corren tal
cual en la consola interactiva: escribe `python3` en la terminal y pégalos.

---

## 1. Modelo de ejecución: intérprete, bytecode y "el módulo se ejecuta"

Python no se compila aparte como TypeScript. Cuando ejecutas `python3 archivo.py`:

1. CPython (el intérprete oficial, escrito en C) compila el archivo a **bytecode**.
2. Ese bytecode se guarda en `__pycache__/archivo.cpython-314.pyc` para no recompilar la
   próxima vez (por eso `__pycache__/` y `*.pyc` están en el `.gitignore`).
3. Una máquina virtual ejecuta el bytecode **de arriba hacia abajo**.

Lo importante: **un archivo `.py` no es una lista de declaraciones, es un script que se
ejecuta**. Un `def` no "declara" una función, es una sentencia que, al ejecutarse, crea un
objeto función y lo asigna a un nombre. Un `class` igual. Un `import` también ejecuta el
archivo importado (una sola vez; después queda cacheado en `sys.modules`).

De ahí sale este patrón que verás en todos lados:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

`__name__` vale `"__main__"` solo cuando el archivo se ejecuta directamente. Cuando otro
archivo lo importa, `__name__` es el nombre del módulo y ese bloque no corre. Es la forma de
tener código "ejecutable" y "importable" en el mismo archivo.

---

## 2. No hay hoisting

En JS, `function` y `var` se elevan. En Python, **un nombre existe desde la línea en que se
ejecuta su asignación**. Esto falla:

```python
saludar()          # NameError: name 'saludar' is not defined

def saludar():
    print("hola")
```

Pero esto funciona, y confunde al principio:

```python
def a():
    return b()     # b no existe todavía cuando se DEFINE a...

def b():
    return 42

print(a())         # ...pero sí existe cuando se LLAMA a. Imprime 42.
```

La regla: el cuerpo de una función se evalúa cuando se llama, no cuando se define. Los
nombres se buscan en ese momento.

---

## 3. Variables son etiquetas, no cajas

Una variable en Python es un **nombre que apunta a un objeto**. `x = 5` no mete un 5 en
una caja llamada x; crea el objeto `5` y le pega la etiqueta `x`. Esto es igual que las
referencias en JS, pero en Python aplica a *todo*, incluidos los números.

Consecuencias:

```python
a = [1, 2, 3]
b = a              # b es OTRA etiqueta del MISMO objeto
b.append(4)
print(a)           # [1, 2, 3, 4]   <- a también cambió

c = list(a)        # copia superficial (también: a[:] o a.copy())
c.append(5)
print(a)           # [1, 2, 3, 4]   <- a no cambió
```

Para copiar estructuras anidadas (listas de diccionarios, etc.) usa `copy.deepcopy()`.

### `==` vs `is`

- `==` compara **valor** (¿son iguales?). Solo hay uno, no existe `===`.
- `is` compara **identidad** (¿son el mismo objeto en memoria?).

```python
a = [1, 2]
b = [1, 2]
a == b    # True
a is b    # False
```

Usa `is` solo para `None`, `True`, `False`: `if x is None:`. Nunca `if x == None`.

### Inmutables vs mutables

| Inmutables (no se pueden cambiar; cualquier "cambio" crea un objeto nuevo) | Mutables |
|---|---|
| `int`, `float`, `bool`, `str`, `tuple`, `None`, `frozenset` | `list`, `dict`, `set`, objetos de tus clases |

```python
s = "hola"
s.upper()        # devuelve "HOLA" pero s sigue siendo "hola"
s = s.upper()    # hay que reasignar
```

Esto explica el bug más famoso de Python: **argumentos por defecto mutables**. El valor
por defecto se crea **una sola vez**, cuando se ejecuta el `def`, y se comparte entre
todas las llamadas:

```python
def add_item(item, inventory=[]):      # MAL
    inventory.append(item)
    return inventory

add_item("espada")       # ['espada']
add_item("escudo")       # ['espada', 'escudo']   <- ¡la misma lista!

def add_item(item, inventory=None):    # BIEN
    if inventory is None:
        inventory = []
    inventory.append(item)
    return inventory
```

### Paso de argumentos

No es "por valor" ni "por referencia": se pasa la **etiqueta**. Si dentro de la función
mutas el objeto (`lista.append`), el que llamó lo ve. Si reasignas el nombre
(`lista = []`), solo cambias la etiqueta local. Exactamente igual que los objetos en JS.

---

## 4. Alcance (scope): no hay alcance de bloque

Esto sorprende mucho viniendo de `let`/`const`. En Python **`if`, `for`, `while`, `try` NO
crean un alcance nuevo**. Solo lo crean las funciones, las clases y los módulos.

```python
for i in range(3):
    last = i

print(i)      # 2    <- la variable del for sigue viva
print(last)   # 2
```

Es como si todo fuera `var`. La regla de búsqueda de nombres se llama **LEGB**:

1. **L**ocal: dentro de la función actual.
2. **E**nclosing: funciones que envuelven a la actual (closures).
3. **G**lobal: el módulo (archivo).
4. **B**uilt-in: `print`, `len`, `range`...

### Leer vs asignar

Puedes **leer** una variable global desde una función sin hacer nada especial. Pero si la
**asignas**, Python la trata como local nueva. Este es el segundo tropiezo clásico:

```python
counter = 0

def increment():
    counter += 1        # UnboundLocalError

def increment():
    global counter      # ahora sí modifica la global (evítalo; mejor pasar y devolver valores)
    counter += 1
```

Para closures existe `nonlocal`, que es lo mismo pero apunta al scope de la función
envolvente.

### Closures: existen y funcionan igual que en JS

```python
def make_counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc

c = make_counter()
c(); c(); print(c())    # 3
```

Y tienen el mismo pitfall de *late binding* que tenía `var` en JS:

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])        # [2, 2, 2]  <- todas ven el i final

funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])        # [0, 1, 2]  <- se captura el valor con el default
```

---

## 5. La indentación ES la sintaxis

No hay llaves. El bloque es lo que está indentado después de los dos puntos `:`.
La convención (PEP 8) son **4 espacios**, nunca tabs. Si un bloque debe quedar vacío,
se usa `pass`.

```python
if condicion:
    pass          # "no hacer nada", pero sintácticamente válido
```

No hay `;` al final de línea. Las líneas largas se partan dentro de paréntesis, corchetes
o llaves (ahí Python ignora los saltos de línea), que es mejor que usar `\`.

---

## 6. Verdad, nulos y comparaciones

### Solo existe `None`

No hay `undefined`. Una función sin `return` devuelve `None`. `None` es un objeto único
(singleton), por eso se compara con `is`.

### Truthiness

Son *falsy*: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`. Todo lo demás es
*truthy*, incluidos objetos de tus clases por defecto.

```python
if inventory:          # idiomático: "si la lista no está vacía"
    ...
if not name:           # "si el string está vacío o es None"
    ...
```

### `and`, `or`, `not` devuelven operandos, como `&&` y `||`

```python
name = user_input or "Anónimo"      # igual que JS
```

### Comparaciones encadenadas (esto no existe en JS)

```python
if 1 <= level <= 5:           # equivale a 1 <= level and level <= 5
    tier = "Novato"
```

### Nada de coerción rara

`"5" + 3` lanza `TypeError`. `"5" == 5` es `False`. Python prefiere fallar a adivinar.
Conviertes explícitamente: `int("5")`, `str(5)`, `float("2.5")`.

---

## 7. Números

- Los `int` son de **precisión arbitraria**: `2 ** 200` funciona sin perder dígitos.
  No hay `Number.MAX_SAFE_INTEGER`.
- `/` **siempre devuelve float** (`7 / 2 == 3.5`). `//` es división entera hacia abajo
  (`7 // 2 == 3`, `-7 // 2 == -4`).
- `%` toma el signo del **divisor**: `-7 % 3 == 2` (en JS da `-1`). Útil para rotaciones,
  por ejemplo turnos de iniciativa.
- `**` es potencia. `round(2.5) == 2` (redondeo bancario, al par más cercano).
- `float` es IEEE 754 igual que JS: `0.1 + 0.2 != 0.3`. Para dinero usa `decimal.Decimal`.
- `is` con enteros es una trampa: CPython cachea los enteros de -5 a 256, así que en la
  consola `a = 256` y `b = 256` da `a is b == True`, pero con 257 da `False` (y dentro de un
  mismo archivo puede dar `True` porque el compilador comparte la constante). El resultado
  depende de detalles internos: por eso `is` solo para `None`.

---

## 8. Strings

- `'simple'` y `"doble"` son idénticos. `"""triple"""` permite varias líneas.
- Son **inmutables** e **iterables**: `for ch in "abc"` recorre caracteres.
- f-strings `f"{x}"` son la forma moderna; dentro de `{}` va cualquier expresión y después
  de `:` va el formato: `{pct:.0%}`, `{n:+d}`, `{name:>10}`, `{x!r}`.
- No hay método `.length`: `len(s)`. Indexado y slicing como las listas: `s[0]`, `s[-1]`,
  `s[2:5]`, `s[::-1]` (invierte).
- Unir listas de strings: `", ".join(items)` (el separador va primero, al revés que JS).
- Cadenas de bytes (`b"..."`) son otro tipo distinto; lo verás al leer archivos binarios
  o respuestas HTTP crudas.

---

## 9. Iteración: el corazón del lenguaje

El `for` de Python no cuenta: **pide elementos uno a uno** a cualquier objeto *iterable*.
Internamente llama `iter(obj)` para obtener un iterador y luego `next()` hasta que recibe
la excepción `StopIteration`. Listas, tuplas, strings, diccionarios, archivos, `range`,
generadores... todos son iterables.

### Herramientas que vas a usar a diario

```python
for i, item in enumerate(items):          # índice + elemento
for name, score in abilities.items():     # clave + valor de un dict
for a, b in zip(list_a, list_b):          # recorrer dos listas en paralelo
for x in reversed(items):
for x in sorted(items, key=len):
```

### Desempaquetado (como destructuring)

```python
x, y = 1, 2
x, y = y, x                       # swap sin variable temporal
first, *rest = [1, 2, 3, 4]       # first=1, rest=[2, 3, 4]
head, *_, tail = range(10)        # _ es convención para "no me importa"
```

Y en llamadas: `f(*lista)` esparce posicionales, `f(**dict)` esparce keyword arguments.
`def f(*args, **kwargs)` recibe cantidades variables.

### Comprehensions: la forma idiomática de map/filter

```python
levels = [c["level"] for c in party]                     # map
alive  = [c for c in party if c["hp"] > 0]               # filter
by_name = {c["name"]: c for c in party}                  # dict comprehension
unique_classes = {c["class"] for c in party}             # set comprehension
```

Si te encuentras escribiendo `list(map(lambda ...))`, casi siempre una comprehension
es más clara.

### Generadores: iteración perezosa

`range(10**9)` no crea mil millones de números; produce cada uno cuando se le pide. Puedes
escribir tus propios iterables perezosos con `yield`:

```python
def roll_forever(sides):
    import random
    while True:
        yield random.randint(1, sides)

dice = roll_forever(20)
print(next(dice), next(dice))
```

Una función con `yield` no se ejecuta al llamarla: devuelve un generador que avanza hasta
el siguiente `yield` cada vez que se le pide un valor. Con paréntesis en vez de corchetes,
una comprehension también es perezosa: `sum(c["level"] for c in party)`.

---

## 10. Excepciones son flujo de control normal

En Python no es mala práctica usar excepciones; el propio lenguaje las usa para terminar
bucles (`StopIteration`) o buscar claves (`KeyError`). La filosofía se llama **EAFP**
(*easier to ask forgiveness than permission*): intenta y maneja el error, en lugar de
preguntar antes.

```python
# LBYL (estilo JS típico)
if "race" in character:
    race = character["race"]
else:
    race = "Humano"

# EAFP (estilo Python)
try:
    race = character["race"]
except KeyError:
    race = "Humano"

# ...aunque aquí lo idiomático es: race = character.get("race", "Humano")
```

Estructura completa:

```python
try:
    value = int(text)
except ValueError as e:        # captura un tipo concreto; nunca `except:` pelado
    print(f"No es número: {e}")
else:                          # corre solo si NO hubo excepción
    print("ok")
finally:                       # corre siempre
    print("fin")
```

Lanzar: `raise ValueError("nivel fuera de rango")`. Encadenar causa: `raise X from e`.
Las excepciones son clases; defines las tuyas heredando de `Exception`. En FastAPI,
`raise HTTPException(status_code=404)` es exactamente esto.

---

## 11. Concurrencia: el GIL y el event loop explícito

Aquí está la diferencia más grande con JS.

### Python es síncrono por defecto

JS tiene un event loop siempre corriendo y todo I/O es asíncrono. Python **no**: una
llamada a `requests.get(url)` bloquea el hilo hasta que llega la respuesta. El programa
corre de arriba a abajo, punto.

### El GIL

CPython tiene el **Global Interpreter Lock**: solo un hilo ejecuta bytecode de Python a
la vez. Los hilos (`threading`) sirven para I/O (mientras un hilo espera a la red, otro
corre), pero **no** aceleran cálculo puro. Para usar varios núcleos en CPU se usa
`multiprocessing` (procesos separados, cada uno con su GIL). Python 3.13+ tiene una
variante experimental sin GIL, pero no es la que usas por defecto.

### asyncio: el event loop opcional

Python tiene un event loop, pero **tú lo arrancas** y **tú eliges** qué código es asíncrono:

```python
import asyncio

async def fetch_monster(index: str) -> dict:
    await asyncio.sleep(0.1)          # simula I/O; cede el control al loop
    return {"index": index}

async def main():
    results = await asyncio.gather(   # como Promise.all
        fetch_monster("goblin"),
        fetch_monster("orc"),
    )
    print(results)

asyncio.run(main())                    # arranca el loop, ejecuta, lo cierra
```

Reglas que debes grabarte:

- `async def` define una **corrutina**. Llamarla **no la ejecuta**: devuelve un objeto
  corrutina que hay que `await`-ear o programar en el loop. (En JS llamar a una función
  async sí la ejecuta hasta el primer await.)
- `await` solo se puede usar dentro de `async def`.
- **Una función bloqueante dentro de `async def` congela TODO el loop**. Si dentro de un
  endpoint async usas `time.sleep(5)` o `requests.get()`, ningún otro request se atiende
  durante esos 5 segundos. Hay que usar librerías async (`httpx`, `asyncpg`, SQLAlchemy
  async) o `await asyncio.to_thread(func_bloqueante)`.
- FastAPI corre sobre Uvicorn, que es quien arranca el loop. Si declaras un endpoint con
  `def` normal, FastAPI lo ejecuta en un hilo aparte para no bloquear; si lo declaras con
  `async def`, corre en el loop y es tu responsabilidad no bloquear. Esto lo vas a vivir
  en la Fase 1.

---

## 12. Clases y objetos

Todo en Python es un objeto, incluidos los números, las funciones y las clases mismas.

```python
class Character:
    species = "humanoid"                     # atributo de clase (compartido)

    def __init__(self, name: str, level: int = 1) -> None:
        self.name = name                     # atributos de instancia
        self.level = level

    def level_up(self) -> None:
        self.level += 1

    def __repr__(self) -> str:               # representación para debugging
        return f"Character(name={self.name!r}, level={self.level})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Character) and self.name == other.name

hero = Character("Yotfil", 4)   # no hay `new`
hero.level_up()
print(hero)                     # Character(name='Yotfil', level=5)
```

Detalles que marcan la diferencia:

- **`self` es explícito.** El primer parámetro de cada método es la instancia. Python
  convierte `hero.level_up()` en `Character.level_up(hero)`. Esto elimina los dolores de
  cabeza de `this` en JS: `self` siempre es lo que parece.
- **`__init__`** es el inicializador (lo más parecido al constructor). Los métodos con
  doble guion bajo a cada lado se llaman *dunder* y son **protocolos**: `__len__` hace que
  `len(obj)` funcione, `__iter__` lo hace recorrible con `for`, `__eq__` define `==`,
  `__str__` define `print(obj)`, `__getitem__` permite `obj[key]`. Así se integran tus
  clases con el lenguaje.
- **No hay `private`.** Convención: `_nombre` significa "interno, no lo toques" (pero
  puedes). `__nombre` activa *name mangling* (se renombra a `_Clase__nombre`), se usa poco.
- **`@property`** convierte un método en atributo calculado, como los getters de JS.
- **`@dataclass`** genera `__init__`, `__repr__` y `__eq__` automáticamente a partir de los
  type hints. Pydantic hace algo parecido pero con validación; lo usaremos para los
  esquemas de la API.

```python
from dataclasses import dataclass

@dataclass
class Monster:
    index: str
    name: str
    challenge_rating: float
```

- **Duck typing.** Python no pregunta "¿eres un Pato?" sino "¿sabes hacer `quack()`?".
  Cualquier objeto con los métodos adecuados sirve. Los `Protocol` de `typing` formalizan
  esto para los type hints, parecido a las interfaces estructurales de TypeScript.
- Herencia: `class Warlock(Character):`. Hay herencia múltiple con un orden de resolución
  definido (MRO). `super().__init__(...)` llama al padre.

---

## 13. Módulos, paquetes e imports

- **Cada archivo `.py` es un módulo.** Importarlo lo **ejecuta una vez** y lo cachea.
- **Una carpeta con `__init__.py` es un paquete.** El `__init__.py` puede estar vacío.
- `import math` trae el módulo; usas `math.sqrt`. `from math import sqrt` trae el nombre
  directo. Evita `from x import *`: ensucia el namespace y rompe el autocompletado.
- Los imports van arriba del archivo, ordenados: librería estándar, terceros, propios.
- **Imports circulares** (`a` importa `b` y `b` importa `a`) fallan de formas confusas.
  La solución suele ser mover código a un tercer módulo o importar dentro de la función.
- La "raíz" para los imports es el directorio desde donde ejecutas o lo que esté en
  `sys.path`. En el proyecto siempre ejecutaremos desde la raíz del repo para que
  `from app.models import User` funcione.

---

## 14. Decoradores: funciones que envuelven funciones

Un decorador recibe una función y devuelve otra (normalmente una versión envuelta). La
sintaxis `@` es solo azúcar:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Llamando {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def attack(target):
    return f"Atacas a {target}"

# equivale a:  attack = log_calls(attack)
attack("goblin")
```

Esto es exactamente lo que hace FastAPI con `@app.get("/monsters")`: registra tu función
como handler de esa ruta. Y `@dataclass`, `@property`, `@pytest.fixture` son lo mismo.

---

## 15. `with`: context managers

Para recursos que hay que abrir y cerrar (archivos, conexiones, transacciones) Python
usa `with`, que garantiza la limpieza aunque haya excepción. Es el `try/finally`
empaquetado:

```python
with open("notas.txt") as f:        # f.close() se llama solo al salir del bloque
    content = f.read()
```

Lo verás con sesiones de base de datos: `async with SessionLocal() as session:`.
Puedes crear los tuyos con `__enter__`/`__exit__` o con `@contextmanager`.

---

## 16. Hashables, tuplas, sets y claves de diccionario

- **Tupla** `(1, 2)`: lista inmutable. Se usa para "registros" pequeños y para devolver
  varios valores: `return hp, status`.
- **Set** `{1, 2, 3}`: colección sin orden ni duplicados, con operaciones de conjuntos
  (`|`, `&`, `-`). Pertenencia `x in s` es O(1).
- Las **claves de un dict deben ser hashables** (inmutables): strings, números, tuplas.
  Una lista como clave lanza `TypeError`.
- Los dicts **mantienen orden de inserción** desde Python 3.7.

---

## 17. Gestión de memoria

CPython usa **conteo de referencias**: cada objeto sabe cuántas etiquetas lo apuntan y se
libera al llegar a cero. Un recolector adicional rompe ciclos (a→b→a). No lo controlas tú
ni deberías pensar en ello, salvo para saber que `del x` borra la etiqueta, no el objeto.

---

## 18. Novedades que conviene conocer (3.8 a 3.12)

```python
# walrus: asigna dentro de una expresión
if (n := len(items)) > 10:
    print(f"{n} elementos")

# match (3.10): pattern matching estructural, más potente que switch
match command.split():
    case ["attack", target]:
        ...
    case ["heal", target, amount]:
        ...
    case _:
        print("comando desconocido")

# type hints modernos sin importar nada de typing
def f(items: list[dict[str, int]] | None = None) -> tuple[int, str]: ...
```

---

## 19. Herramientas de introspección

Python se explora desde dentro. En la consola interactiva:

```python
type(x)          # tipo del objeto
dir(x)           # todos los atributos y métodos
help(str.split)  # documentación de cualquier cosa
x.__dict__       # atributos de una instancia
breakpoint()     # pausa el programa y abre el debugger (pdb) en esa línea
```

`python3 -i archivo.py` ejecuta el archivo y te deja en la consola con todas sus variables
cargadas. Perfecto para probar funciones de los ejercicios.

---

## 20. Estilo: PEP 8 y el Zen

- `snake_case` para variables y funciones, `PascalCase` para clases, `MAYUSCULAS` para
  constantes. 4 espacios. Líneas de ≤ 88 caracteres (con el formateador `ruff`).
- Prefiere lo explícito, lo plano y lo legible. Escribe `import this` en la consola para
  leer el Zen de Python; resume la filosofía del lenguaje en 19 líneas.
- "Pythonic" significa usar las herramientas del lenguaje como están pensadas: iterar
  directamente, comprehensions, `with`, EAFP, desempaquetado, dunder methods. Código que
  parece JS traducido línea por línea funciona, pero no es pythonic.

---

## Chuleta: JS → Python

| JavaScript | Python |
|---|---|
| `let`/`const` con alcance de bloque | nombres sin alcance de bloque (solo función/módulo) |
| hoisting | no existe |
| `undefined` y `null` | solo `None` |
| `===` | `==` (valor) e `is` (identidad, solo para `None`) |
| `this` implícito y confuso | `self` explícito |
| `new Clase()` | `Clase()` |
| `arr.length` | `len(arr)` |
| `arr.map(f)` / `.filter(f)` | `[f(x) for x in arr]` / `[x for x in arr if ...]` |
| `arr.includes(x)` | `x in arr` |
| `obj.key` | `obj["key"]` o `obj.get("key")` |
| `Object.entries(obj)` | `obj.items()` |
| `` `hola ${x}` `` | `f"hola {x}"` |
| `arr.join(", ")` | `", ".join(arr)` |
| `try/catch/finally` | `try/except/else/finally` |
| `async` por defecto, event loop siempre activo | síncrono por defecto; `asyncio` opcional y explícito |
| `Promise.all` | `asyncio.gather` |
| llamar función async la ejecuta | llamar `async def` devuelve una corrutina sin ejecutar |
| `npm i` / `package.json` | `pip install` / `requirements.txt` o `uv` / `pyproject.toml` |
