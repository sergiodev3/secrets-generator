# secrets-generator

[![Release](https://img.shields.io/github/v/release/sergiodev3/secrets-generator)](https://github.com/sergiodev3/secrets-generator/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

CLI para generar **secretos criptográficamente seguros** para aplicaciones en producción: claves JWT, secretos de sesión, API keys y cualquier valor que vaya en un archivo `.env`.

```text
$ secrets-gen JWT_SECRET SESSION_SECRET
JWT_SECRET=IyKqwgs3nElv2yD0LentMfMLUnT3YUmXsIKCuLRwFU4
SESSION_SECRET=mCFlccmPa0CD6V-AEN7WJE1a1gT-Oslj9BMwdSIOlPQ
```

> Los valores de este documento son solo ejemplos. Un secreto publicado deja de ser secreto: genera siempre los tuyos.

---

## Contenido

- [Inicio rápido](#inicio-rápido)
- [¿Por qué importa usar secretos seguros?](#por-qué-importa-usar-secretos-seguros)
- [¿Por qué rotar los secretos?](#por-qué-rotar-los-secretos)
- [Cómo te ayuda esta herramienta](#cómo-te-ayuda-esta-herramienta)
- [Instalación](#instalación)
- [Uso](#uso)
- [Buenas prácticas](#buenas-prácticas)
- [Desarrollo](#desarrollo)
- [Contribuir](#contribuir)

---

## Inicio rápido

1. Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) si aún no lo tienes.
2. Instala la herramienta desde GitHub:

   ```bash
   uv tool install git+https://github.com/sergiodev3/secrets-generator@v0.2.0
   ```

3. Abre una terminal nueva y ejecuta:

   ```bash
   secrets-gen
   ```

Verás el menú interactivo. Muévete con las flechas ↑/↓ y confirma con Enter.

---

## ¿Por qué importa usar secretos seguros?

Un **secreto** es un valor que solo tu aplicación debe conocer. Con él firma tokens, cifra cookies o se autentica ante otros servicios. Quien lo conozca puede hacerse pasar por tu aplicación.

### El riesgo: secretos débiles o predecibles

| Mala práctica | Qué puede pasar |
|---|---|
| `JWT_SECRET=mi-app-2024` | Con un solo token válido, un atacante puede probar millones de claves por segundo **sin conectarse a tu servidor** (con herramientas como hashcat). Si encuentra la clave, puede firmar tokens propios y hacerse pasar por cualquier usuario, incluido un administrador. |
| Secretos generados con `random` | El módulo `random` de Python no está diseñado para seguridad: observando suficientes valores generados se puede reconstruir su estado interno y predecir los siguientes. |
| El mismo secreto en desarrollo y producción | Una filtración del entorno de desarrollo (un portátil, un repositorio de pruebas) compromete producción. |
| Secretos cortos | Cada bit menos reduce a la mitad el esfuerzo necesario para adivinarlo. |

### La solución: entropía suficiente desde una fuente segura

La **entropía** mide cuán impredecible es un secreto y se expresa en bits. Un secreto de 256 bits tiene 2²⁵⁶ valores posibles, un número tan grande que probarlos todos es inviable con cualquier tecnología actual.

Por eso esta herramienta:

- Usa el módulo [`secrets`](https://docs.python.org/3/library/secrets.html) de Python, que obtiene los valores del generador criptográfico del sistema operativo (CSPRNG). **Nunca** usa `random`.
- Genera **256 bits por defecto**, que es el mínimo que exige el estándar JWT ([RFC 7518, §3.2](https://www.rfc-editor.org/rfc/rfc7518#section-3.2)) para claves HS256: la clave debe ser al menos tan larga como la salida del hash.
- Rechaza cualquier valor por debajo de 128 bits.

> **Importante:** la seguridad se mide en bits, no en caracteres. Un secreto de 32 caracteres hexadecimales tiene solo 128 bits; uno de 32 caracteres base64url tiene 192. Por eso esta herramienta se configura por **bytes de entropía** y no por longitud.

---

## ¿Por qué rotar los secretos?

**Rotar** un secreto significa reemplazarlo por uno nuevo de forma planificada. Aunque un secreto sea fuerte, con el tiempo aumenta la probabilidad de que se haya filtrado sin que lo sepas: un commit accidental, un log, una captura de pantalla, una copia de seguridad o una persona que ya no está en el equipo.

Rotar limita el daño: **un secreto filtrado deja de servir en cuanto lo reemplazas.**

### Cuándo rotar

| Situación | Urgencia |
|---|---|
| El secreto apareció en un repositorio, log, chat o ticket | Inmediata |
| Sospecha de incidente de seguridad | Inmediata |
| Una persona con acceso deja el equipo o el proyecto | Alta |
| Rotación periódica (por ejemplo, cada 90 días) | Planificada |

### Cómo rotar sin cortar el servicio

Cambiar un `JWT_SECRET` de golpe invalida todos los tokens emitidos y cierra la sesión de todos los usuarios. Una rotación ordenada se hace por etapas:

1. **Genera** el nuevo secreto:

   ```bash
   secrets-gen JWT_SECRET
   ```

2. **Convive:** configura tu aplicación para que firme con la clave nueva y siga aceptando la anterior durante un período de transición (por ejemplo, con `JWT_SECRET` y `JWT_SECRET_PREVIOUS`). Esto requiere que tu aplicación admita varias claves de verificación.
3. **Espera** a que expiren los tokens firmados con la clave anterior.
4. **Retira** la clave anterior de la configuración.

Si la rotación es por una filtración confirmada, omite el período de convivencia: es preferible cerrar todas las sesiones que mantener una clave comprometida.

---

## Cómo te ayuda esta herramienta

| Necesidad | Qué hace `secrets-gen` |
|---|---|
| Generar secretos impredecibles | Usa el CSPRNG del sistema operativo, nunca `random`. |
| Saber cuánta seguridad es suficiente | 256 bits por defecto y presets para JWT (HS256/HS512), sesiones y API keys. |
| Rotar rápido y sin errores | Un comando genera el nuevo valor listo para pegar: `secrets-gen JWT_SECRET`. |
| Separar entornos | Genera valores distintos en cada ejecución para desarrollo, staging y producción. |
| Integrarse en scripts y CI | Fuera de una terminal imprime solo el secreto, sin menú ni colores. |
| Copiar sin errores | Los secretos se imprimen sin saltos de línea ni formato adicional. |

---

## Instalación

Requisitos: [uv](https://docs.astral.sh/uv/getting-started/installation/). Si no tienes Python 3.12 o superior, uv lo instala automáticamente.

### Opción A: desde GitHub (recomendada)

No necesitas clonar el repositorio:

```bash
uv tool install git+https://github.com/sergiodev3/secrets-generator@v0.2.0
```

`@v0.2.0` fija la versión. Para instalar una versión posterior, repite el comando con el nuevo tag (consulta los [releases](https://github.com/sergiodev3/secrets-generator/releases)).

### Opción B: clonando el repositorio

Útil si quieres leer el código, modificarlo o contribuir:

```bash
git clone https://github.com/sergiodev3/secrets-generator.git
cd secrets-generator
uv tool install .
```

`uv tool install .` instala una **copia** del código. Si lo modificas, reinstala para ver los cambios:

```bash
uv tool install . --reinstall
```

### Verificar la instalación

```bash
secrets-gen --version
```

Si la terminal no encuentra el comando, agrega la carpeta de herramientas de uv al `PATH` y abre una terminal nueva:

```bash
uv tool update-shell
```

### Desinstalar

```bash
uv tool uninstall secrets-generator
```

---

## Uso

### Modo interactivo

Ejecuta `secrets-gen` sin argumentos. Verás el logo, la versión y un menú que se recorre con las flechas ↑/↓ y Enter:

| Opción | Qué hace |
|---|---|
| **Generate .env variables** | Pide uno o varios nombres (separados por comas o espacios), la entropía y el formato, e imprime líneas `KEY=value`. |
| **Generate a raw secret** | Imprime un único secreto sin nombre. |
| **Presets** | Configuraciones listas para los casos más comunes (ver tabla abajo). |
| **Help** | Muestra ejemplos de uso desde la línea de comandos. |
| **Exit** | Sale del programa. `Ctrl+C` también sale en cualquier momento. |

Después de cada acción vuelves al menú.

#### Presets

| Preset | Variable | Entropía | Formato |
|---|---|---|---|
| JWT secret (HS256) | `JWT_SECRET` | 32 bytes (256 bits) | `base64url` |
| JWT secret (HS512) | `JWT_SECRET` | 64 bytes (512 bits) | `base64url` |
| Session secret | `SESSION_SECRET` | 32 bytes (256 bits) | `base64url` |
| API key | `API_KEY` | 32 bytes (256 bits) | `alnum` |

### Línea de comandos

```bash
# Una variable para el .env (256 bits, base64url)
secrets-gen JWT_SECRET

# Varias variables a la vez
secrets-gen JWT_SECRET SESSION_SECRET

# Agregar directamente al archivo .env
secrets-gen JWT_SECRET >> .env

# 512 bits (HS512) en hexadecimal
secrets-gen JWT_SECRET --bytes 64 --format hex

# Solo el valor, sin nombre (por ejemplo, para guardarlo en un archivo)
secrets-gen > secreto.txt

# Ayuda y versión
secrets-gen -h
secrets-gen --version
```

El menú interactivo solo se abre cuando ejecutas `secrets-gen` **sin argumentos y en una terminal**. Si pasas un nombre u opción, o rediriges la salida (`>`, `|`), la herramienta imprime el resultado directamente. Así puedes usarla en scripts sin que se quede esperando una respuesta.

### Opciones

| Opción | Valor por defecto | Descripción |
|---|---|---|
| `--bytes`, `-b` | `32` | Entropía en bytes (mínimo 16). 32 bytes = 256 bits, suficiente para HS256. Usa 64 para HS512. |
| `--format`, `-f` | `base64url` | Codificación de salida (ver tabla de formatos). |
| `--version`, `-V` | | Muestra la versión y termina. |
| `--help`, `-h` | | Muestra la ayuda con ejemplos y termina. |

### ¿Qué formato elegir?

Todos los formatos tienen la misma seguridad para la misma cantidad de bytes; solo cambia cómo se escribe el valor.

| Formato | Caracteres (32 bytes) | Cuándo usarlo |
|---|---|---|
| `base64url` | 43 | **Recomendado.** Seguro en URLs, archivos `.env` y cabeceras HTTP. |
| `base64` | 44 | Cuando una librería exige base64 estándar. Incluye `+`, `/` y `=`, que pueden requerir comillas. |
| `hex` | 64 | Cuando se espera una clave hexadecimal (por ejemplo, algunas configuraciones de cifrado). |
| `alnum` | 43 | Cuando un sistema rechaza símbolos: solo letras y dígitos. |

---

## Buenas prácticas

- [ ] **Nunca subas el `.env` al repositorio.** Agrégalo a `.gitignore` desde el primer commit.
- [ ] **Usa un secreto distinto por entorno:** desarrollo, staging y producción.
- [ ] **En producción, guarda los secretos en el gestor de tu plataforma** (variables de entorno del hosting, AWS Secrets Manager, HashiCorp Vault, etc.) y no en archivos dentro del servidor.
- [ ] **No compartas secretos por chat ni correo.** Si ocurre, rótalos.
- [ ] **No escribas secretos en logs** ni en mensajes de error.
- [ ] **Rota periódicamente** y siempre ante una sospecha de filtración.
- [ ] **Limpia la pantalla** después de generar secretos en una terminal compartida o mientras compartes pantalla.

---

## Desarrollo

```bash
git clone https://github.com/sergiodev3/secrets-generator.git
cd secrets-generator
uv sync                 # instala dependencias en un entorno virtual
uv run secrets-gen      # ejecuta la versión local sin instalarla
uv run pytest           # ejecuta los tests
```

Estructura del proyecto:

```text
src/secrets_generator/
├── core.py          # generación de secretos y presets (sin dependencias de interfaz)
├── cli.py           # comandos y opciones (Typer)
├── interactive.py   # menú interactivo (questionary)
└── ui.py            # logo, colores y presentación (rich)
tests/               # tests con pytest
```

---

## Contribuir

¿Tienes una idea, encontraste un error o algo no quedó claro? Abre un [issue](https://github.com/sergiodev3/secrets-generator/issues). Todos los comentarios son bienvenidos.

---

## Licencia

[MIT](LICENSE) © sergiodev3
