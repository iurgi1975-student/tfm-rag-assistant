# 🔐 Guía de Autenticación con Roles

## Descripción

El sistema RAG AI Assistant incluye un sistema de autenticación integrado con **control de acceso basado en roles (RBAC)**. Los usuarios deben autenticarse con usuario y contraseña, y tendrán diferentes niveles de acceso según su rol.

## Características

- ✅ Pantalla de login integrada en el frontend
- ✅ Autenticación basada en usuario/contraseña
- ✅ **Control de acceso basado en roles (RBAC)**
- ✅ **Dos roles: Admin (acceso completo) y User (solo chat)**
- ✅ Múltiples usuarios soportados
- ✅ Configuración mediante variables de entorno
- ✅ Modo sin autenticación para desarrollo local
- ✅ Arquitectura DDD con Clean Architecture

## Roles de Usuario

### 👑 Admin (Administrador)
- **Acceso completo** a todas las funcionalidades
- ✅ Chat con el asistente IA
- ✅ Subir y procesar documentos PDF
- ✅ Añadir texto directamente a la base de conocimiento
- ✅ Buscar en documentos
- ✅ Limpiar la base de conocimiento
- **Tabs visibles**: "💬 Chat" y "📄 Document Management"

### 👤 User (Usuario)
- **Acceso limitado** solo al chat
- ✅ Chat con el asistente IA (usa conocimiento existente)
- ✅ Ver estado de la base de conocimiento
- ❌ NO puede subir documentos
- ❌ NO puede procesar PDFs
- ❌ NO puede modificar la base de conocimiento
- **Tab visible**: "💬 Chat" únicamente

## Configuración

### 1. Variables de Entorno (Nuevo Formato con Roles)

Añade los usuarios autorizados en tu archivo `.env`:

```bash
# Formato: "usuario1:contraseña1:rol,usuario2:contraseña2:rol"
# Roles disponibles: admin, user
GRADIO_AUTH_USERS=admin:MiPasswordSegura2024:admin,juan:juan123:user,maria:maria456:admin
```

**Importante:** 
- Separa usuarios con comas (`,`)
- Separa usuario, contraseña y rol con dos puntos (`:`)
- Roles válidos: `admin` o `user` (en minúsculas)
- Si no especificas rol, se asigna `user` por defecto (seguridad)
- Usa contraseñas seguras en producción
- NO subas el archivo `.env` a Git

### 2. Credenciales por Defecto

Si no configuras `GRADIO_AUTH_USERS`, el sistema creará usuario por defecto:

```
Usuario: admin      Contraseña: admin123      Rol: Admin
```

⚠️ **ADVERTENCIA:** Las credenciales por defecto son solo para desarrollo. ¡NO las uses en producción!

## Uso

### Ejecutar con autenticación (recomendado para web)

```bash
python app.py --host 0.0.0.0 --port 7860
```

Los usuarios verán una pantalla de login antes de acceder. El rol determina qué funcionalidades pueden usar.

### Ejecutar sin autenticación (solo desarrollo local)

```bash
python app.py --no-auth
```

La aplicación se ejecutará sin requerir login (útil para desarrollo local). Todas las funcionalidades estarán disponibles.

### Ejecutar con Gemini y autenticación

```bash
python app.py --use-google --host 0.0.0.0
```

## Ejemplo Completo

### 1. Crear archivo `.env`

```bash
# .env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX

# Configurar usuarios con roles
# Formato: usuario:contraseña:rol
GRADIO_AUTH_USERS=profesor:ProfePass2024:admin,alumno1:Estudiante1:user,alumno2:Estudiante2:user,tutor:Tutor2024:admin

PORT=7860
```

**Explicación de usuarios:**
- `profesor` - Admin con acceso completo
- `alumno1` y `alumno2` - Users con acceso solo a chat
- `tutor` - Otro admin con acceso completo

### NOTA
GRADIO_AUTH_USERS="Las verdaderas claves para el acceso a la aplicación están publicadas en la presentación compartida con mouredev@gmail.com"

### 2. Ejecutar la aplicación

```bash
python app.py --use-google --host 0.0.0.0
```

### 3. Acceder desde el navegador

**Como Admin (profesor):**
1. Abre `http://localhost:7860`
2. Introduce credenciales:
   - Usuario: `profesor`
   - Contraseña: `ProfePass2024`
3. Click en "🔓 Login"
4. Verás: **👑 Admin | Logged in as: Profesor**
5. Tienes acceso a:
   - ✅ Tab "💬 Chat"
   - ✅ Tab "📄 Document Management"

**Como User (alumno1):**
1. Abre `http://localhost:7860`
2. Introduce credenciales:
   - Usuario: `alumno1`
   - Contraseña: `Estudiante1`
3. Click en "🔓 Login"
4. Verás: **👤 User | Logged in as: Alumno1**
5. Tienes acceso a:
   - ✅ Tab "💬 Chat" únicamente
   - ❌ NO verás la tab de Document Management

## Troubleshooting

### "Invalid credentials"
- Verifica que el usuario/contraseña estén bien escritos
- Revisa el archivo `.env` (sin espacios extras)
- Verifica que hayas cargado las variables: `python -c "import os; print(os.getenv('GRADIO_AUTH_USERS'))"`
- El formato correcto es: `usuario:password:rol` (con `:` entre cada campo)

### Login no aparece
- Verifica que NO estés usando `--no-auth`
- Confirma que la autenticación esté habilitada en el container

### Credenciales por defecto no funcionan
- Si configuraste `GRADIO_AUTH_USERS`, las credenciales por defecto se deshabilitan
- Usa las credenciales que configuraste en `.env`

### No veo la tab de "Document Management"
- **Esto es normal** si iniciaste sesión como **User** (rol limitado)
- Solo los usuarios con rol **Admin** pueden ver esta tab
- Verifica tu rol al hacer login (aparece junto a tu nombre)
- Si necesitas acceso completo, solicita a un administrador que cambie tu rol a `admin`

### Error: "Username cannot be empty"
- Asegúrate de introducir un nombre de usuario
- No dejes espacios en blanco al inicio o final

### Cambio de rol no se refleja
- Cierra sesión (🚪 Logout)
- Actualiza el archivo `.env` con el nuevo rol
- Reinicia la aplicación: `Ctrl+C` y luego `python app.py`
- Vuelve a iniciar sesión

## Retrocompatibilidad

### Formato antiguo (sin roles)

Si usas el formato antiguo `usuario:password`, el sistema asignará automáticamente rol **User**:

```bash
# Formato antiguo (se asigna rol User por defecto)
GRADIO_AUTH_USERS=usuario1:password1,usuario2:password2
```

Ambos usuarios tendrán acceso limitado (solo chat). Para cambiarlos a admin, añade `:admin`:

```bash
# Formato nuevo con roles explícitos
GRADIO_AUTH_USERS=usuario1:password1:admin,usuario2:password2:user
```


## Seguridad

### Mejores Prácticas

1. **Contraseñas Fuertes**: Usa contraseñas de al menos 12 caracteres
2. **Cambio Regular**: Cambia las contraseñas periódicamente
3. **Secretos**: Usa gestores de secretos (Azure Key Vault, Railway Secrets)
4. **HTTPS**: Siempre despliega con HTTPS en producción
5. **No Hardcodear**: Nunca pongas contraseñas en el código
6. **Principio de Mínimo Privilegio**: Usa rol User por defecto, Admin solo cuando sea necesario

### Limitaciones

⚠️ Este es un sistema de autenticación **básico** adecuado para:
- Demos y presentaciones
- Desarrollo y testing
- Aplicaciones internas con pocos usuarios
- Proyectos académicos

Para aplicaciones de producción con muchos usuarios, considera:
- OAuth2/OpenID Connect
- JWT tokens
- Base de datos de usuarios con password hashing (bcrypt, argon2)
- 2FA (autenticación de dos factores)
- Rate limiting
- Auditoría de accesos

## Arquitectura DDD (Domain-Driven Design)

El sistema de autenticación sigue los principios de **Clean Architecture** y **DDD**:

### Capas de la Arquitectura

```
┌─────────────────────────────────────────┐
│   Interface Layer (gradio_chat.py)     │  ← Presentación
├─────────────────────────────────────────┤
│   Application Layer                     │
│   - AuthenticationService               │  ← Lógica de aplicación
├─────────────────────────────────────────┤
│   Domain Layer                          │
│   - User (Entity)                       │
│   - UserRole (Enum)                     │  ← Lógica de negocio
│   - AuthenticationRepository (Port)     │
├─────────────────────────────────────────┤
│   Infrastructure Layer                  │
│   - InMemoryAuthRepository (Adapter)    │  ← Implementación
└─────────────────────────────────────────┘
```

### Componentes

1. **Domain Layer** (`src/domain/`):
   - `models/user.py`: Entidad User con lógica de permisos
   - `models/user.py`: Enum UserRole (ADMIN, USER)
   - `repositories/authentication_repository.py`: Interfaz del repositorio

2. **Application Layer** (`src/application/`):
   - `services/authentication_service.py`: Servicio de autenticación
   - `container.py`: Inyección de dependencias

3. **Infrastructure Layer** (`src/infrastructure/`):
   - `authentication/in_memory_auth_repository.py`: Implementación en memoria

4. **Interface Layer** (`src/interface/`):
   - `gradio_chat.py`: UI con control basado en roles

### Ventajas de esta Arquitectura

- ✅ **Separación de responsabilidades**: Cada capa tiene una función clara
- ✅ **Testeable**: Fácil crear mocks de repositorios
- ✅ **Extensible**: Se puede cambiar InMemory por PostgreSQL sin tocar dominio
- ✅ **Mantenible**: Los cambios en infraestructura no afectan la lógica de negocio
- ✅ **Domain-Driven**: El dominio define las reglas (permisos, roles)

## Personalización

### Cambiar el mensaje de login

Edita `src/interface/gradio_chat.py`:

```python
gr.Markdown("# 🔐 Login - Mi Aplicación Personalizada")
gr.Markdown("Mensaje personalizado de bienvenida")
```

### Añadir un nuevo rol

Para añadir más roles (ej: MODERATOR), sigue estos pasos:

1. **Edita el enum en** `src/domain/models/user.py`:
```python
class UserRole(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"  # Nuevo rol
    USER = "user"
```

2. **Añade métodos de permisos** en la clase `User`:
```python
def can_moderate_documents(self) -> bool:
    return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
```

3. **Actualiza la interfaz** en `src/interface/gradio_chat.py` para mostrar/ocultar tabs según el nuevo rol

4. **Actualiza el repositorio** para parsear el nuevo rol desde el `.env`

### Cambiar a repositorio persistente

Para usar PostgreSQL en lugar de InMemory:

1. Implementa `PostgreSQLAuthRepository` que herede de `AuthenticationRepository`
2. Usa bcrypt para hashear contraseñas
3. Actualiza `container.py` para usar el nuevo repositorio
4. ¡No cambias nada en domain ni application! (Clean Architecture)

## Comandos Útiles

```bash
# Ver usuarios y roles configurados
python -c "import os; users = os.getenv('GRADIO_AUTH_USERS', '').split(','); print([f'{u.split(\":\")[0]} ({u.split(\":\")[2] if len(u.split(\":\"))>2 else \"user\"})' for u in users if ':' in u])"

# Ejecutar con debug y autenticación
python app.py --debug

# Ejecutar sin autenticación (desarrollo local)
python app.py --no-auth --host localhost

# Crear link público temporal (con autenticación y roles)
python app.py --share

# Ver solo nombres de usuario
python -c "import os; users = os.getenv('GRADIO_AUTH_USERS', '').split(','); print([u.split(':')[0] for u in users if ':' in u])"
```

## Casos de Uso

### Caso 1: Escuela/Universidad
```bash
GRADIO_AUTH_USERS=profesor1:Pass123:admin,profesor2:Pass456:admin,alumno1:Est123:user,alumno2:Est456:user
```
- Profesores (admin): Pueden subir material y gestionar documentos
- Alumnos (user): Solo pueden consultar mediante chat

### Caso 2: Empresa
```bash
GRADIO_AUTH_USERS=gerente:Mgr2024:admin,analista:Ana2024:admin,cliente:Client123:user
```
- Gerente y Analista (admin): Gestionan la base de conocimiento
- Cliente (user): Solo consulta información vía chat

### Caso 3: Proyecto Personal
```bash
GRADIO_AUTH_USERS=yo:MiPassword:admin,amigo:AmigoPass:user
```
- Tú (admin): Control total
- Amigos (user): Solo pueden chatear con tus documentos

### Caso 4: Equipo de Investigación
```bash
GRADIO_AUTH_USERS=investigador_principal:IP2024:admin,investigador2:Inv2024:admin,asistente:Asist2024:user
```
- Investigadores (admin): Cargan papers y documentos
- Asistentes (user): Consultan la base de conocimiento

## Testing

### Probar roles diferentes

1. **Login como Admin:**
```bash
# Usuario: admin
# Password: admin123
# Resultado esperado: Ver ambas tabs (Chat + Document Management)
```

2. **Login como User:**
```bash
# Crear usuario de prueba en .env:
# GRADIO_AUTH_USERS=admin:admin123:admin,testuser:test123:user
#
# Usuario: testuser
# Password: test123
# Resultado esperado: Ver solo tab Chat
```

3. **Probar formato antiguo (backward compatibility):**
```bash
# GRADIO_AUTH_USERS=olduser:oldpass
# Usuario: olduser tendrá rol User automáticamente
```

## FAQ

**P: ¿Puedo cambiar el rol default de User a Admin?**  
R: Sí, edita `InMemoryAuthRepository.from_env_config()` en `src/infrastructure/authentication/in_memory_auth_repository.py` y cambia `UserRole.USER` por `UserRole.ADMIN` en la línea 109.

**P: ¿Las contraseñas se almacenan de forma segura?**  
R: En esta implementación simple, no. Las contraseñas se almacenan en texto plano. Para producción, implementa hashing con bcrypt o argon2.

**P: ¿Puedo tener múltiples admins?**  
R: Sí, simplemente añade más usuarios con `:admin` en el .env.

**P: ¿Qué pasa si olvido mi contraseña?**  
R: Al ser un sistema sin base de datos, necesitas actualizar el `.env` manualmente y reiniciar la aplicación.

**P: ¿Se puede añadir un rol "readonly" que pueda ver documentos pero no modificarlos?**  
R: Sí, sigue los pasos en la sección "Añadir un nuevo rol" más arriba.

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


