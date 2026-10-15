# secrets-generator

CLI para generar secretos criptográficamente seguros (claves JWT, secretos de sesión, API keys) para aplicaciones en producción.

Usa el módulo `secrets` de Python (CSPRNG del sistema operativo). Nunca `random`.

## Instalación

```bash
uv tool install .
```

## Modo interactivo

Ejecuta `secrets-gen` sin argumentos en una terminal para abrir el menú interactivo. Muestra el logo, el nombre de la aplicación y la versión, y permite navegar con las flechas arriba/abajo y confirmar con Enter:

- **Generate .env variables**: pide uno o varios nombres (separados por comas o espacios), la entropía y el formato, e imprime líneas `KEY=value`.
- **Generate a raw secret**: imprime un único secreto sin nombre.
- **Presets**: configuraciones listas para casos comunes.
- **Help**: ejemplos de uso no interactivo.
- **Exit**: sale del programa. `Ctrl+C` también sale en cualquier momento.

Después de cada acción se vuelve al menú. Los secretos se imprimen sin saltos de línea ni formato adicional para que se puedan copiar tal cual.

El menú solo se abre cuando la entrada y la salida son una terminal. Si la salida se redirige o se usa en una tubería (`secrets-gen > secreto.txt`, `secrets-gen | clip`), o si se pasa cualquier nombre u opción, el comportamiento es el no interactivo descrito abajo.

### Presets

| Preset | Variable | Entropía | Formato |
|---|---|---|---|
| JWT secret (HS256) | `JWT_SECRET` | 32 bytes (256 bits) | `base64url` |
| JWT secret (HS512) | `JWT_SECRET` | 64 bytes (512 bits) | `base64url` |
| Session secret | `SESSION_SECRET` | 32 bytes (256 bits) | `base64url` |
| API key | `API_KEY` | 32 bytes (256 bits) | `alnum` |

## Uso no interactivo

```bash
# Secreto sin nombre (32 bytes = 256 bits, base64url); fuera de una terminal
secrets-gen > secreto.txt

# Líneas para un archivo .env
secrets-gen JWT_SECRET SESSION_SECRET
# JWT_SECRET=Q3x...
# SESSION_SECRET=9fA...

# Agregar a un archivo .env
secrets-gen JWT_SECRET >> .env

# Más entropía y otra codificación
secrets-gen JWT_SECRET --bytes 64 --format hex

# Ayuda con ejemplos y versión
secrets-gen -h
secrets-gen --version
```

### Opciones

| Opción | Valor por defecto | Descripción |
|---|---|---|
| `--bytes`, `-b` | `32` | Entropía en bytes (mínimo 16). 32 bytes = 256 bits, suficiente para HS256. Usa 64 para HS512. |
| `--format`, `-f` | `base64url` | `base64url`, `base64`, `hex` o `alnum` |
| `--version`, `-V` | | Muestra la versión y termina. |
| `--help`, `-h` | | Muestra la ayuda con ejemplos y termina. |

La longitud depende de la entropía, no de la cantidad de caracteres: 32 bytes generan 64 caracteres en `hex`, 43 en `base64url` y 43 en `alnum`.

## Desarrollo

```bash
uv sync
uv run pytest
```
