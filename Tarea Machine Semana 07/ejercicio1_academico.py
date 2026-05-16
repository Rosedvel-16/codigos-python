from pyDatalog import pyDatalog

# Declaracion de todos los predicados que se usaran en las reglas.
pyDatalog.create_terms(
    'X',
    # Hechos base
    'promedio_aprobatorio', 'promedio_desaprobatorio',
    'asistencia_suficiente', 'asistencia_baja',
    'proyecto_entregado', 'participacion_destacada',
    'situacion_economica_vulnerable',
    # Conclusiones inferidas
    'aprueba', 'desaprueba',
    'habilitado_cierre', 'no_habilitado_cierre',
    'observacion_inasistencia',
    'puede_postular_beca', 'no_puede_postular_beca',
    'reconocimiento_academico',
    'requiere_seguimiento',
    'alta_prioridad_beca'
)

# Reglas declarativas en formato legible para mostrar en la UI.
RULES = [
    "aprueba(X) <= promedio_aprobatorio(X) & asistencia_suficiente(X)",
    "desaprueba(X) <= promedio_desaprobatorio(X)",
    "observacion_inasistencia(X) <= asistencia_baja(X)",
    "habilitado_cierre(X) <= aprueba(X) & proyecto_entregado(X)",
    "puede_postular_beca(X) <= aprueba(X) & situacion_economica_vulnerable(X) & habilitado_cierre(X)",
    "reconocimiento_academico(X) <= aprueba(X) & participacion_destacada(X)",
    "no_habilitado_cierre(X) <= promedio_aprobatorio(X) & ~proyecto_entregado(X)",
    "requiere_seguimiento(X) <= observacion_inasistencia(X)",
    "alta_prioridad_beca(X) <= puede_postular_beca(X) & participacion_destacada(X)",
]


# Convierte un predicado de pyDatalog a una lista ordenada de entidades.
def _predicate_list(pred):
    if not hasattr(pred, "data") or pred.data is None:
        return []
    return sorted({row[0] for row in pred.data})


# Construye hechos y reglas, ejecuta inferencia y prepara los resultados.
def get_context():
    pyDatalog.clear()

    # 1. Ana: promedio aprobatorio, asistencia suficiente, proyecto entregado, participacion destacada
    +promedio_aprobatorio('Ana')
    +asistencia_suficiente('Ana')
    +proyecto_entregado('Ana')
    +participacion_destacada('Ana')

    # 2. Luis: promedio desaprobatorio, asistencia suficiente
    +promedio_desaprobatorio('Luis')
    +asistencia_suficiente('Luis')

    # 3. Carla: promedio aprobatorio, asistencia baja, proyecto entregado, situacion economica vulnerable
    +promedio_aprobatorio('Carla')
    +asistencia_baja('Carla')
    +proyecto_entregado('Carla')
    +situacion_economica_vulnerable('Carla')

    # 4. Pedro: promedio aprobatorio, asistencia suficiente, proyecto entregado, situacion economica vulnerable
    +promedio_aprobatorio('Pedro')
    +asistencia_suficiente('Pedro')
    +proyecto_entregado('Pedro')
    +situacion_economica_vulnerable('Pedro')

    # 5. Maria: promedio aprobatorio, asistencia suficiente, sin proyecto, participacion destacada
    +promedio_aprobatorio('Maria')
    +asistencia_suficiente('Maria')
    +participacion_destacada('Maria')

    # Reglas de inferencia en sintaxis pyDatalog.
    aprueba(X) <= promedio_aprobatorio(X) & asistencia_suficiente(X)
    desaprueba(X) <= promedio_desaprobatorio(X)
    observacion_inasistencia(X) <= asistencia_baja(X)
    habilitado_cierre(X) <= aprueba(X) & proyecto_entregado(X)
    puede_postular_beca(X) <= aprueba(X) & situacion_economica_vulnerable(X) & habilitado_cierre(X)
    reconocimiento_academico(X) <= aprueba(X) & participacion_destacada(X)
    no_habilitado_cierre(X) <= promedio_aprobatorio(X) & ~proyecto_entregado(X)
    requiere_seguimiento(X) <= observacion_inasistencia(X)
    alta_prioridad_beca(X) <= puede_postular_beca(X) & participacion_destacada(X)

    # Estructura de salida consumida por la app Streamlit.
    return {
        "aprueba": _predicate_list(aprueba(X)),
        "desaprueba": _predicate_list(desaprueba(X)),
        "habilitado_cierre": _predicate_list(habilitado_cierre(X)),
        "observacion_inasistencia": _predicate_list(observacion_inasistencia(X)),
        "puede_postular_beca": _predicate_list(puede_postular_beca(X)),
        "reconocimiento_academico": _predicate_list(reconocimiento_academico(X)),
        "requiere_seguimiento": _predicate_list(requiere_seguimiento(X)),
        "alta_prioridad_beca": _predicate_list(alta_prioridad_beca(X)),
        "consultas": {
            "Ana habilitada para cierre": bool(habilitado_cierre('Ana')),
            "Luis desaprueba": bool(desaprueba('Luis')),
            "Carla puede postular a beca": bool(puede_postular_beca('Carla')),
            "Pedro puede postular a beca": bool(puede_postular_beca('Pedro')),
            "Maria recibe reconocimiento": bool(reconocimiento_academico('Maria')),
            "Carla requiere seguimiento": bool(requiere_seguimiento('Carla')),
        },
    }


# Modo consola para imprimir resultados y consultas especificas.
def run_console():
    get_context()

    print("=" * 55)
    print("   SISTEMA EXPERTO - EVALUACION ACADEMICA")
    print("=" * 55)

    print("\n✅ Estudiantes que APRUEBAN el curso:")
    print(aprueba(X))

    print("\n❌ Estudiantes que DESAPRUEBAN el curso:")
    print(desaprueba(X))

    print("\n🎓 Habilitados para CIERRE ACADEMICO:")
    print(habilitado_cierre(X))

    print("\n⚠️  Con OBSERVACION POR INASISTENCIA:")
    print(observacion_inasistencia(X))

    print("\n💰 Pueden POSTULAR A BECA:")
    print(puede_postular_beca(X))

    print("\n🏅 Reciben RECONOCIMIENTO ACADEMICO:")
    print(reconocimiento_academico(X))

    print("\n🔍 Requieren SEGUIMIENTO ACADEMICO:")
    print(requiere_seguimiento(X))

    print("\n⭐ ALTA PRIORIDAD DE BECA:")
    print(alta_prioridad_beca(X))

    print("\n" + "=" * 55)
    print("   CONSULTAS ESPECIFICAS")
    print("=" * 55)

    print(f"\n¿Ana esta habilitada para cierre academico?  => {bool(habilitado_cierre('Ana'))}")
    print(f"¿Luis desaprueba el curso?                   => {bool(desaprueba('Luis'))}")
    print(f"¿Carla puede postular a beca?                => {bool(puede_postular_beca('Carla'))}")
    print(f"¿Pedro puede postular a beca?                => {bool(puede_postular_beca('Pedro'))}")
    print(f"¿Maria recibe reconocimiento academico?      => {bool(reconocimiento_academico('Maria'))}")
    print(f"¿Carla requiere seguimiento academico?       => {bool(requiere_seguimiento('Carla'))}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    run_console()
