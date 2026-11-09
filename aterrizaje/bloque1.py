name = "Yotfil"
class_name = "Warlock"
pv_current = 12
pv_max = 28
lvl = 4
percentage = pv_current / pv_max

if lvl <= 5:
    experience = "Novato"
elif lvl <= 10:
    experience = "Aprendiz"
else:
    experience = "Veterano"

if pv_current <= 0:
    status = "Inconsciente"
elif pv_current < pv_max / 2:
    status = "Herido"
else:
    status = "Sano"


greeting = f"Hola {name}, veo que eres {experience}, bienvenido a la aventura!"

to_print = f"""
=========={name}==========
Clase: {class_name}
Nivel: {lvl}
PV: {pv_current}/{pv_max}
"""

to_print_status = f"Estado: {status} y tu porcentaje de vida es: {percentage:.0%}"

print(to_print)
print(greeting)
print(to_print_status)
