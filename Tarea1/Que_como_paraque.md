# 🧠 Arquitectura de un Sistema Experto

A continuación, se describen los componentes principales de un sistema experto con su **qué, para qué y cómo**.

---

## 1. Adquisición de Conocimiento

**Qué es:**  
Proceso mediante el cual se obtiene la información y experiencia de un experto humano o de fuentes externas (sensores, bases de datos).

**Para qué sirve:**  
Capturar el conocimiento especializado que luego será utilizado por el sistema experto para resolver problemas.

**Cómo funciona:**
- El **experto** proporciona sus conocimientos.  
- El **cognimático** (ingeniero del conocimiento) traduce ese conocimiento en reglas o representaciones computacionales.  
- También se integran datos de **sensores** o **bases de datos**.  
- Todo esto se organiza en el **módulo de adquisición de conocimiento**.

---

## 2. Representación del Conocimiento

**Qué es:**  
La forma en que se almacena y organiza el conocimiento adquirido.

**Para qué sirve:**  
Hacer que el conocimiento sea accesible y procesable por el sistema.

**Cómo funciona:**
- **Base de conocimiento:** Contiene las reglas, hechos, relaciones y heurísticas del dominio.  
- **Base de hechos:** Guarda la información específica del problema en curso (los datos del caso que se está resolviendo).

---

## 3. Tratamiento del Conocimiento

**Qué es:**  
El mecanismo que utiliza el sistema para razonar y aplicar el conocimiento almacenado.

**Para qué sirve:**  
Resolver problemas, deducir conclusiones y justificar resultados.

**Cómo funciona:**
- **Motor de inferencia:** Aplica las reglas de la base de conocimiento a los hechos almacenados en la base de hechos para llegar a conclusiones.  
- **Módulo de explicaciones:** Permite al sistema justificar sus razonamientos y explicar al usuario cómo se alcanzó una conclusión.

---

## 4. Utilización del Conocimiento

**Qué es:**  
La interacción del sistema experto con el usuario final.

**Para qué sirve:**  
Mostrar soluciones, recomendaciones o diagnósticos al usuario.

**Cómo funciona:**
- A través de una **interfaz** que traduce el lenguaje técnico del sistema a una forma comprensible para el usuario.  
- El **usuario** introduce datos y recibe respuestas o recomendaciones.
