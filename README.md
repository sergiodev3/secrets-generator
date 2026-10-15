# secrets-generator

CLI para generar secretos criptográficamente seguros (claves JWT, secretos de sesión, API keys) para aplicaciones en producción.

Usa el módulo `secrets` de Python (CSPRNG del sistema operativo). Nunca `random`.

## Instalación

```bash
uv tool install .
```

## Uso

```bash
# Secreto sin nombre (32 bytes = 256 bits, base64url)
secrets-gen

# Líneas para un archivo .env
secrets-gen JWT_SECRET SESSION_SECRET
# JWT_SECRET=Q3x...
# SESSION_SECRET=9fA...

# Agregar a un archivo .env
secrets-gen JWT_SECRET >> .env

# Más entropía y otra codificación
secrets-gen JWT_SECRET --bytes 64 --format hex
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
