# Environment Variables Configuration

Este directorio contiene los archivos de configuración de variables de entorno para diferentes ambientes.

## Estructura de Archivos

### Archivos Públicos (se suben a Git)
- `.env.base` - Variables compartidas entre todos los entornos (URLs públicas, configuraciones generales)
- `.env.dev.example` - Template para desarrollo local
- `.env.test.example` - Template para tests locales
- `.env.prod.example` - Template para producción (si existe)

### Archivos con Secrets (NO se suben a Git)
- `.env.dev` - Secrets de desarrollo local
- `.env.test` - Secrets para tests locales
- `.env.prod` - Secrets de producción

## Configuración Inicial

### 1. Desarrollo Local

```bash
# Copia el archivo de ejemplo
cp envs/.env.dev.example envs/.env.dev

# Edita el archivo y añade tus secrets
# envs/.env.dev
SUPABASE_SECRET_KEY=tu_secret_key_aqui
```

### 2. Tests Locales

```bash
# Copia el archivo de ejemplo
cp envs/.env.test.example envs/.env.test

# Edita el archivo y añade tus secrets
# envs/.env.test
SUPABASE_SECRET_KEY=tu_secret_key_aqui
```

## Uso en Diferentes Contextos

### Desarrollo Local con Docker
```bash
make dev
```
- Carga: `.env.base` + `.env.dev`
- Los secrets vienen de `envs/.env.dev`

### Tests Locales con Docker
```bash
make test
```
- Carga: `.env.base` + `.env.test`
- Los secrets vienen de `envs/.env.test`

### CI/CD (GitHub Actions)
- Carga: `.env.base` + `.env.test`
- Los secrets vienen de GitHub Secrets y se pasan como variables de entorno
- Configuración en `.github/workflows/ci-tests-cov.yml`

## Cómo Funciona en CI

1. GitHub Actions define el secret en el workflow:
```yaml
env:
  SUPABASE_SECRET_KEY: ${{ secrets.SUPABASE_SECRET_KEY }}
```

2. El Makefile exporta las variables al ejecutar `make test`

3. Docker Compose recibe la variable desde el entorno del host:
```yaml
environment:
  SUPABASE_SECRET_KEY: ${SUPABASE_SECRET_KEY}
```

## Añadir Nuevos Secrets

### Para desarrollo/test local:
1. Añade la variable a `.env.dev` o `.env.test`
2. Actualiza el archivo `.example` correspondiente (sin el valor real)

### Para CI/CD:
1. Ve a GitHub → Settings → Secrets and variables → Actions
2. Añade el secret con el mismo nombre
3. Asegúrate de que el workflow lo pase al contenedor en la sección `env:`

## Seguridad

- ✅ Los archivos `.env.dev`, `.env.test` y `.env.prod` están en `.gitignore`
- ✅ Solo los archivos `.example` se suben a Git
- ✅ Los secrets de CI están en GitHub Secrets, no en el código
- ⚠️ Nunca hagas commit de archivos con secrets reales
