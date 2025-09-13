
# 4. Subsistema de Adquisición de Conocimiento

**Qué:**  
Agregar nuevo conocimiento al sistema.

**Para qué:**  
Permitir que el sistema evolucione con nuevas reglas.

**Cómo:**  
Se verifican y se incluyen en la base de conocimiento.

```python
def agregar_regla(nombre, sintomas):
    base_conocimiento[nombre] = sintomas

agregar_regla("alergia", ["estornudos", "ojos_rojos"])
```

# 5. Control de Coherencia

**Qué:**  
Verifica la consistencia de la base de conocimiento.

**Para qué:**  
Evita contradicciones o reglas incompletas.

**Cómo:**  
Se revisan reglas y restricciones.

```python
def verificar_coherencia():
    for enfermedad, sintomas in base_conocimiento.items():
        if len(sintomas) == 0:
            print(f"⚠ La regla de {enfermedad} no tiene síntomas definidos")

verificar_coherencia()
```

# 6. Motor de Inferencia

**Qué:**  
El corazón del sistema experto.

**Para qué:**  
Aplica reglas a los hechos y saca conclusiones.

**Cómo:**  
Usa métodos deterministas o probabilísticos.

```python
def inferir(hechos):
    posibles = []
    for enfermedad, sintomas in base_conocimiento.items():
        if all(hechos.get(s, False) for s in sintomas):
            posibles.append(enfermedad)
    return posibles

print("Diagnóstico:", inferir(hechos))
```

# 7. Interfaz de Usuario

**Qué:**  
Comunicación entre el usuario y el sistema.

**Para qué:**  
Entrada de datos y presentación de resultados.

**Cómo:**  
Usando formularios, CLI o GUI.

```python
sintoma = input("¿El paciente tiene fiebre? (s/n): ")
hechos["fiebre"] = (sintoma.lower() == "s")
```

# 8. Subsistema de Ejecución de Órdenes

**Qué:**  
Permite al sistema actuar sobre el entorno.

**Para qué:**  
Implementar acciones derivadas de conclusiones.

**Cómo:**  
Ejecutando funciones según el diagnóstico.

```python
def ejecutar_orden(diagnostico):
    if "gripe" in diagnostico:
        print("Acción: Recomendar reposo y líquidos.")
    elif "resfriado" in diagnostico:
        print("Acción: Recomendar vitamina C.")

ejecutar_orden(inferir(hechos))
```

# 9. Subsistema de Explicación

**Qué:**  
Justifica las conclusiones y acciones del sistema.

**Para qué:**  
Generar confianza y transparencia.

**Cómo:**  
Mostrando las reglas y hechos usados.

```python
def explicar(enfermedad):
    print(f"Se diagnosticó {enfermedad} porque se cumplieron los síntomas: {base_conocimiento[enfermedad]}")

explicar("gripe")
```

# 10. Subsistema de Aprendizaje

**Qué:**  
Capacidad de mejorar con la experiencia.

**Para qué:**  
Evolucionar la base de conocimiento con casos nuevos.

**Cómo:**  
Guardando experiencias y ajustando reglas.

```python
experiencias = []

def aprender(caso, resultado):
    experiencias.append({"caso": caso, "resultado": resultado})

aprender(hechos, "gripe")
print("Experiencias almacenadas:", experiencias)
```
