"""
Demo de persistencia de chat - Script de ejemplo
Este NO es un test unitario, solo una demostración de la funcionalidad.
"""
from src.application.container import AppContainer

# Crear container con persistencia habilitada
print("🚀 Iniciando test de persistencia...")
container = AppContainer(
    enable_chat_persistence=True,
    chat_db_path="./data/test_chat.db",
    default_session_id="test_session"
)

# Obtener servicio de chat
chat_service = container.chat_service

# Enviar mensaje 1
print("\n📝 Enviando mensaje 1...")
response1 = chat_service.chat("Hola, mi nombre es Juan", use_rag=False, stream=False)
print(f"Respuesta: {response1[:100]}...")

# Enviar mensaje 2
print("\n📝 Enviando mensaje 2...")
response2 = chat_service.chat("¿Recuerdas mi nombre?", use_rag=False, stream=False)
print(f"Respuesta: {response2[:100]}...")

# Ver historial en memoria
print("\n📜 Historial en memoria:")
history = chat_service.get_history()
print(f"Total mensajes: {len(history)}")
for i, msg in enumerate(history):
    print(f"  {i+1}. {msg.role.value}: {msg.content[:50]}...")

# Verificar que se guardó en BD
print("\n💾 Verificando persistencia en BD...")
chat_repo = container.chat_repository
if chat_repo:
    db_history = chat_repo.get_history("test_session")
    print(f"Mensajes en BD: {len(db_history)}")
    
    stats = chat_repo.get_session_stats("test_session")
    print(f"Estadísticas: {stats}")
    
    sessions = chat_repo.list_sessions()
    print(f"Sesiones disponibles: {sessions}")

print("\n✅ Test completado!")
