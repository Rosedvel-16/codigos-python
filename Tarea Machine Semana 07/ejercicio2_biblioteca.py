from pyDatalog import pyDatalog

# Declaracion de predicados para hechos y conclusiones.
pyDatalog.create_terms(
    'X',
    # Hechos base
    'prestamo_activo', 'devolucion_tardia', 'deuda_pendiente',
    'reserva_realizada', 'es_tesista', 'libro_alta_demanda',
    # Conclusiones inferidas
    'tiene_multa', 'servicio_suspendido',
    'puede_renovar', 'prioridad_prestamo',
    'reserva_prioritaria', 'reserva_especial',
    'maxima_prioridad', 'usuario_habilitado'
)

# Reglas declarativas en formato legible para mostrar en la UI.
RULES = [
    "tiene_multa(X) <= devolucion_tardia(X)",
    "servicio_suspendido(X) <= deuda_pendiente(X)",
    "servicio_suspendido(X) <= tiene_multa(X)",
    "puede_renovar(X) <= prestamo_activo(X) & ~servicio_suspendido(X)",
    "prioridad_prestamo(X) <= es_tesista(X)",
    "reserva_prioritaria(X) <= reserva_realizada(X) & libro_alta_demanda(X)",
    "reserva_especial(X) <= es_tesista(X) & libro_alta_demanda(X)",
    "maxima_prioridad(X) <= reserva_prioritaria(X) & es_tesista(X)",
    "usuario_habilitado(X) <= prestamo_activo(X) & ~deuda_pendiente(X) & ~tiene_multa(X)",
    "usuario_habilitado(X) <= reserva_realizada(X) & ~deuda_pendiente(X) & ~tiene_multa(X)",
]


# Convierte un predicado de pyDatalog a una lista ordenada de entidades.
def _predicate_list(pred):
    if not hasattr(pred, "data") or pred.data is None:
        return []
    return sorted({row[0] for row in pred.data})


# Construye hechos y reglas, ejecuta inferencia y prepara los resultados.
def get_context():
    pyDatalog.clear()

    # 1. Ana: prestamo activo, devolucion tardia, tesista
    +prestamo_activo('Ana')
    +devolucion_tardia('Ana')
    +es_tesista('Ana')

    # 2. Luis: prestamo activo, sin devolucion tardia, sin deuda
    +prestamo_activo('Luis')

    # 3. Carla: deuda pendiente, prestamo activo
    +deuda_pendiente('Carla')
    +prestamo_activo('Carla')

    # 4. Pedro: reserva, tesista, libro de alta demanda
    +reserva_realizada('Pedro')
    +es_tesista('Pedro')
    +libro_alta_demanda('Pedro')

    # 5. Maria: prestamo activo, sin devolucion tardia, reserva, libro alta demanda
    +prestamo_activo('Maria')
    +reserva_realizada('Maria')
    +libro_alta_demanda('Maria')

    # Reglas de inferencia en sintaxis pyDatalog.
    tiene_multa(X) <= devolucion_tardia(X)
    servicio_suspendido(X) <= deuda_pendiente(X)
    servicio_suspendido(X) <= tiene_multa(X)
    puede_renovar(X) <= prestamo_activo(X) & ~servicio_suspendido(X)
    prioridad_prestamo(X) <= es_tesista(X)
    reserva_prioritaria(X) <= reserva_realizada(X) & libro_alta_demanda(X)
    reserva_especial(X) <= es_tesista(X) & libro_alta_demanda(X)
    maxima_prioridad(X) <= reserva_prioritaria(X) & es_tesista(X)
    usuario_habilitado(X) <= prestamo_activo(X) & ~deuda_pendiente(X) & ~tiene_multa(X)
    usuario_habilitado(X) <= reserva_realizada(X) & ~deuda_pendiente(X) & ~tiene_multa(X)

    # Estructura de salida consumida por la app Streamlit.
    return {
        "tiene_multa": _predicate_list(tiene_multa(X)),
        "servicio_suspendido": _predicate_list(servicio_suspendido(X)),
        "puede_renovar": _predicate_list(puede_renovar(X)),
        "prioridad_prestamo": _predicate_list(prioridad_prestamo(X)),
        "reserva_prioritaria": _predicate_list(reserva_prioritaria(X)),
        "reserva_especial": _predicate_list(reserva_especial(X)),
        "maxima_prioridad": _predicate_list(maxima_prioridad(X)),
        "usuario_habilitado": _predicate_list(usuario_habilitado(X)),
        "consultas": {
            "Ana tiene multa": bool(tiene_multa('Ana')),
            "Ana servicio suspendido": bool(servicio_suspendido('Ana')),
            "Luis puede renovar": bool(puede_renovar('Luis')),
            "Carla servicio suspendido": bool(servicio_suspendido('Carla')),
            "Pedro reserva especial": bool(reserva_especial('Pedro')),
            "Maria reserva prioritaria": bool(reserva_prioritaria('Maria')),
        },
    }


# Modo consola para imprimir resultados y consultas especificas.
def run_console():
    get_context()

    print("=" * 55)
    print("   SISTEMA EXPERTO - BIBLIOTECA UNIVERSITARIA")
    print("=" * 55)

    print("\n⚠️  Usuarios con MULTA:")
    print(tiene_multa(X))

    print("\n🚫 Usuarios con SERVICIO SUSPENDIDO:")
    print(servicio_suspendido(X))

    print("\n🔄 Usuarios que PUEDEN RENOVAR PRESTAMO:")
    print(puede_renovar(X))

    print("\n🎖️  Usuarios con PRIORIDAD DE PRESTAMO (tesistas):")
    print(prioridad_prestamo(X))

    print("\n📌 Usuarios con RESERVA PRIORITARIA:")
    print(reserva_prioritaria(X))

    print("\n🔑 Usuarios con acceso a RESERVA ESPECIAL:")
    print(reserva_especial(X))

    print("\n⭐ Usuarios con MAXIMA PRIORIDAD DE ATENCION:")
    print(maxima_prioridad(X))

    print("\n✅ Usuarios HABILITADOS:")
    print(usuario_habilitado(X))

    print("\n" + "=" * 55)
    print("   CONSULTAS ESPECIFICAS")
    print("=" * 55)

    print(f"\n¿Ana tiene multa?                     => {bool(tiene_multa('Ana'))}")
    print(f"¿Ana tiene el servicio suspendido?    => {bool(servicio_suspendido('Ana'))}")
    print(f"¿Luis puede renovar prestamo?         => {bool(puede_renovar('Luis'))}")
    print(f"¿Carla tiene el servicio suspendido?  => {bool(servicio_suspendido('Carla'))}")
    print(f"¿Pedro puede acceder a reserva esp.?  => {bool(reserva_especial('Pedro'))}")
    print(f"¿Maria tiene reserva prioritaria?     => {bool(reserva_prioritaria('Maria'))}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    run_console()