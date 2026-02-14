# 🔐 Guía de Autenticación

## Descripción

El sistema RAG AI Assistant ahora incluye un sistema de autenticación integrado en el frontend de Gradio. Los usuarios deben autenticarse con usuario y contraseña antes de acceder a la aplicación.

## Características

- ✅ Pantalla de login integrada en el frontend
- ✅ Autenticación basada en usuario/contraseña
- ✅ Múltiples usuarios soportados
- ✅ Configuración mediante variables de entorno
- ✅ Modo sin autenticación para desarrollo local

## Configuración

### 1. Variables de Entorno

Añade los usuarios autorizados en tu archivo `.env`:

```bash
# Formato: "usuario1:contraseña1,usuario2:contraseña2"
GRADIO_AUTH_USERS=admin:MiPasswordSegura2024,demo:demo123,usuario:pass456
```

**Importante:** 
- Separa usuarios con comas (`,`)
- Separa usuario y contraseña con dos puntos (`:`)
- Usa contraseñas seguras en producción
- NO subas el archivo `.env` a Git

### 2. Credenciales por Defecto

Si no configuras `GRADIO_AUTH_USERS`, el sistema usará credenciales por defecto:

```
Usuario: admin
Contraseña: admin123
```

⚠️ **ADVERTENCIA:** Las credenciales por defecto son solo para desarrollo. ¡NO las uses en producción!

## Uso

### Ejecutar con autenticación (recomendado para web)

```bash
python app.py --host 0.0.0.0 --port 7860
```

Los usuarios verán una pantalla de login antes de acceder a la aplicación.

### Ejecutar sin autenticación (solo desarrollo local)

```bash
python app.py --no-auth
```

La aplicación se ejecutará sin requerir login (útil para desarrollo local).

### Ejecutar con Gemini y autenticación

```bash
python app.py --use-google --host 0.0.0.0
```


## Seguridad

### Mejores Prácticas

1. **Contraseñas Fuertes**: Usa contraseñas de al menos 12 caracteres
2. **Cambio Regular**: Cambia las contraseñas periódicamente
3. **Secretos**: Usa gestores de secretos (Azure Key Vault, Railway Secrets)
4. **HTTPS**: Siempre despliega con HTTPS en producción
5. **No Hardcodear**: Nunca pongas contraseñas en el código

### Limitaciones

⚠️ Este es un sistema de autenticación **básico** adecuado para:
- Demos y presentaciones
- Desarrollo y testing
- Aplicaciones internas con pocos usuarios
- Proyectos académicos

Para aplicaciones de producción con muchos usuarios, considera:
- OAuth2/OpenID Connect
- JWT tokens
- Base de datos de usuarios
- 2FA (autenticación de dos factores)
- Rate limiting

## Ejemplo Completo

### 1. Crear archivo `.env`

```bash
# .env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX
GRADIO_AUTH_USERS=profesor:ProfePass2024,alumno1:Estudiante1,alumno2:Estudiante2
PORT=7860
```

### 2. Ejecutar la aplicación

```bash
python app.py --use-google --host 0.0.0.0
```

### 3. Acceder desde el navegador

1. Abre `http://localhost:7860`
2. Verás la pantalla de login
3. Introduce credenciales:
   - Usuario: `profesor`
   - Contraseña: `ProfePass2024`
4. Click en "🔓 Login"
5. Accede a la aplicación completa

## Troubleshooting

### "Invalid credentials"
- Verifica que el usuario/contraseña estén bien escritos
- Revisa el archivo `.env` (sin espacios extras)
- Verifica que hayas cargado las variables: `python -c "import os; print(os.getenv('GRADIO_AUTH_USERS'))"`

### Login no aparece
- Verifica que NO estés usando `--no-auth`
- Confirma que `auth_users` no sea `None` en el código

### Credenciales por defecto no funcionan
- Si configuraste `GRADIO_AUTH_USERS`, las credenciales por defecto se deshabilitan
- Usa las credenciales que configuraste en `.env`

## Personalización

### Cambiar el mensaje de login

Edita `src/interface/gradio_chat.py`:

```python
gr.Markdown("# 🔐 Login - Mi Aplicación Personalizada")
gr.Markdown("Mensaje personalizado de bienvenida")
```

### Añadir validación adicional

Modifica la función `handle_login()` en `gradio_chat.py` para añadir lógica personalizada.

## Comandos Útiles

```bash
# Ver usuarios configurados (sin contraseñas)
python -c "import os; users = os.getenv('GRADIO_AUTH_USERS', '').split(','); print([u.split(':')[0] for u in users if ':' in u])"

# Ejecutar con debug
python app.py --debug

# Crear link público temporal (con autenticación)
python app.py --share

# Sin autenticación en localhost
python app.py --no-auth --host localhost
```

## Soporte

Para más información sobre Gradio authentication, visita:
- [Documentación oficial de Gradio](https://www.gradio.app/docs/interface#authentication)
