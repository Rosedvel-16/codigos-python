from pyDatalog import pyDatalog

# Declaracion de predicados para hechos y conclusiones.
pyDatalog.create_terms(
    'X',
    # Hechos base
    'pedido_urgente', 'direccion_lejana', 'vehiculo_disponible',
    'conductor_disponible', 'paquete_fragil',
    'cliente_preferencial', 'pago_confirmado', 'pago_pendiente',
    # Conclusiones inferidas
    'puede_programarse', 'atencion_prioritaria',
    'planificacion_especial_ruta', 'embalaje_especial',
    'entrega_inmediata', 'puede_enviarse_hoy',
    'maxima_prioridad_logistica', 'asignacion_ejecutiva',
    'confirmacion_adicional'
)

# Reglas declarativas en formato legible para mostrar en la UI.
RULES = [
    "puede_programarse(X) <= pago_confirmado(X) & vehiculo_disponible(X) & conductor_disponible(X)",
    "atencion_prioritaria(X) <= pedido_urgente(X)",
    "planificacion_especial_ruta(X) <= direccion_lejana(X)",
    "embalaje_especial(X) <= paquete_fragil(X)",
    "entrega_inmediata(X) <= pedido_urgente(X) & puede_programarse(X)",
    "atencion_prioritaria(X) <= cliente_preferencial(X)",
    "confirmacion_adicional(X) <= pago_pendiente(X)",
    "puede_enviarse_hoy(X) <= puede_programarse(X) & ~confirmacion_adicional(X)",
    "maxima_prioridad_logistica(X) <= pedido_urgente(X) & direccion_lejana(X)",
    "asignacion_ejecutiva(X) <= maxima_prioridad_logistica(X) & cliente_preferencial(X)",
]


# Convierte un predicado de pyDatalog a una lista ordenada de entidades.
def _predicate_list(pred):
    if not hasattr(pred, "data") or pred.data is None:
        return []
    return sorted({row[0] for row in pred.data})


# Construye hechos y reglas, ejecuta inferencia y prepara los resultados.
def get_context():
    pyDatalog.clear()

    # P1: urgente, pago confirmado, vehiculo disponible, conductor disponible
    +pedido_urgente('P1')
    +pago_confirmado('P1')
    +vehiculo_disponible('P1')
    +conductor_disponible('P1')

    # P2: direccion lejana, pago confirmado, vehiculo disponible, conductor disponible
    +direccion_lejana('P2')
    +pago_confirmado('P2')
    +vehiculo_disponible('P2')
    +conductor_disponible('P2')

    # P3: urgente, direccion lejana, pago confirmado, vehiculo, conductor, cliente preferencial
    +pedido_urgente('P3')
    +direccion_lejana('P3')
    +pago_confirmado('P3')
    +vehiculo_disponible('P3')
    +conductor_disponible('P3')
    +cliente_preferencial('P3')

    # P4: paquete fragil, pago confirmado, vehiculo disponible, sin conductor
    +paquete_fragil('P4')
    +pago_confirmado('P4')
    +vehiculo_disponible('P4')

    # P5: cliente preferencial, pago pendiente, vehiculo disponible, conductor disponible
    +cliente_preferencial('P5')
    +pago_pendiente('P5')
    +vehiculo_disponible('P5')
    +conductor_disponible('P5')

    # P6: pago confirmado, vehiculo disponible, conductor disponible, paquete fragil
    +pago_confirmado('P6')
    +vehiculo_disponible('P6')
    +conductor_disponible('P6')
    +paquete_fragil('P6')

    # Reglas de inferencia en sintaxis pyDatalog.
    puede_programarse(X) <= pago_confirmado(X) & vehiculo_disponible(X) & conductor_disponible(X)
    atencion_prioritaria(X) <= pedido_urgente(X)
    planificacion_especial_ruta(X) <= direccion_lejana(X)
    embalaje_especial(X) <= paquete_fragil(X)
    entrega_inmediata(X) <= pedido_urgente(X) & puede_programarse(X)
    atencion_prioritaria(X) <= cliente_preferencial(X)
    confirmacion_adicional(X) <= pago_pendiente(X)
    puede_enviarse_hoy(X) <= puede_programarse(X) & ~confirmacion_adicional(X)
    maxima_prioridad_logistica(X) <= pedido_urgente(X) & direccion_lejana(X)
    asignacion_ejecutiva(X) <= maxima_prioridad_logistica(X) & cliente_preferencial(X)

    # Estructura de salida consumida por la app Streamlit.
    return {
        "puede_programarse": _predicate_list(puede_programarse(X)),
        "atencion_prioritaria": _predicate_list(atencion_prioritaria(X)),
        "embalaje_especial": _predicate_list(embalaje_especial(X)),
        "confirmacion_adicional": _predicate_list(confirmacion_adicional(X)),
        "entrega_inmediata": _predicate_list(entrega_inmediata(X)),
        "puede_enviarse_hoy": _predicate_list(puede_enviarse_hoy(X)),
        "maxima_prioridad_logistica": _predicate_list(maxima_prioridad_logistica(X)),
        "asignacion_ejecutiva": _predicate_list(asignacion_ejecutiva(X)),
        "consultas": {
            "P1 puede enviarse hoy": bool(puede_enviarse_hoy('P1')),
            "P3 maxima prioridad": bool(maxima_prioridad_logistica('P3')),
            "P3 asignacion ejecutiva": bool(asignacion_ejecutiva('P3')),
            "P4 embalaje especial": bool(embalaje_especial('P4')),
            "P5 confirmacion adicional": bool(confirmacion_adicional('P5')),
            "P6 puede programarse": bool(puede_programarse('P6')),
        },
    }


# Modo consola para imprimir resultados y consultas especificas.
def run_console():
    get_context()

    print("=" * 55)
    print("   SISTEMA EXPERTO - LOGISTICA DE ENTREGAS")
    print("=" * 55)

    print("\n📦 Pedidos que PUEDEN PROGRAMARSE:")
    print(puede_programarse(X))

    print("\n🚨 Pedidos con ATENCION PRIORITARIA:")
    print(atencion_prioritaria(X))

    print("\n📦 Pedidos con EMBALAJE ESPECIAL:")
    print(embalaje_especial(X))

    print("\n❗ Pedidos con CONFIRMACION ADICIONAL requerida:")
    print(confirmacion_adicional(X))

    print("\n⚡ Pedidos asignados a ENTREGA INMEDIATA:")
    print(entrega_inmediata(X))

    print("\n✈️  Pedidos que PUEDEN ENVIARSE HOY:")
    print(puede_enviarse_hoy(X))

    print("\n🔴 Pedidos con MAXIMA PRIORIDAD LOGISTICA:")
    print(maxima_prioridad_logistica(X))

    print("\n👑 Pedidos con ASIGNACION EJECUTIVA:")
    print(asignacion_ejecutiva(X))

    print("\n" + "=" * 55)
    print("   CONSULTAS ESPECIFICAS")
    print("=" * 55)

    print(f"\n¿P1 puede enviarse hoy?               => {bool(puede_enviarse_hoy('P1'))}")
    print(f"¿P3 tiene maxima prioridad logistica? => {bool(maxima_prioridad_logistica('P3'))}")
    print(f"¿P3 recibe asignacion ejecutiva?      => {bool(asignacion_ejecutiva('P3'))}")
    print(f"¿P4 necesita embalaje especial?       => {bool(embalaje_especial('P4'))}")
    print(f"¿P5 requiere confirmacion adicional?  => {bool(confirmacion_adicional('P5'))}")
    print(f"¿P6 puede ser programado?             => {bool(puede_programarse('P6'))}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    run_console()