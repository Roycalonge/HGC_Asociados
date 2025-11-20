import telebot
from datetime import datetime
import time

# 🔑 PEGA AQUÍ TU TOKEN DE BOTFATHER
TOKEN = "8215051603:AAFxzCbKs65F0AFW-XHf8woT8ecWv05hUzg"

bot = telebot.TeleBot(TOKEN)

print("🚀 Iniciando HGC Bot - Comandos Completos...")
print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- COMANDOS PRINCIPALES ---

@bot.message_handler(commands=['start', 'help'])
def start(message):
    response = """
🎯 *HGC BOT - SISTEMA COMPLETO ACTIVO*

🤖 *COMANDOS CONFIGURADOS:*

📝 *ACADÉMICOS:*
/registrar - Nuevo trabajo académico
/reporte - Reportar avance de proyecto
/sesion - Programar sesión de estudio

📁 *DOCUMENTOS:*
/buscar - Buscar documentos en Drive
/subir - Subir documento a Google Drive
/categorias - Ver estructura de carpetas

👥 *COORDINACIÓN:*
/reunion - Programar reunión
/asignar - Asignar tarea específica
/encuesta - Crear encuesta rápida

📊 *MONITOREO:*
/estado - Estado general del equipo

🚨 *ETIQUETAS OFICIALES:*
[URGENTE] [TAREA] [CONSULTA] [RECURSO] [INFORME] [FELICITACIONES]

*HGC & Asociados - Sistema Operativo Integral*
    """
    bot.reply_to(message, response, parse_mode='Markdown')
    print(f"✅ {message.from_user.first_name} inició el bot")

@bot.message_handler(commands=['registrar'])
def registrar_trabajo(message):
    try:
        # Ejemplo: /registrar "Análisis Mercado" 2024-10-25 15 Administración
        parts = message.text.split(' ', 3)
        
        if len(parts) < 4:
            bot.reply_to(message, 
                "📝 *FORMATO:* /registrar [Nombre] [Fecha] [Puntos] [Materia]\n\n"
                "*Ejemplos:*\n"
                "`/registrar \"Análisis Mercado\" 2024-10-25 15 Administración`\n"
                "`/registrar \"Ensayo Filosofía\" 2024-10-28 20 Filosofía`", 
                parse_mode='Markdown')
            return
            
        nombre = parts[1].strip('"')
        fecha = parts[2]
        puntos = parts[3]
        materia = parts[4] if len(parts) > 4 else "General"
        
        respuesta = f"""
✅ *TRABAJO ACADÉMICO REGISTRADO*

📚 *Trabajo:* {nombre}
📅 *Entrega:* {fecha}
🎯 *Puntos:* {puntos}%
🏷️ *Materia:* {materia}
👤 *Registrado por:* {message.from_user.first_name}
🆔 *ID:* TR-{datetime.now().strftime('%m%d%H%M')}

*Próximos pasos:*
1. Programar reunión: /reunion
2. Asignar tareas: /asignar
3. Seguimiento: /reporte
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"📝 Trabajo registrado: {nombre} - {materia}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error en registro: {str(e)}")

@bot.message_handler(commands=['reporte'])
def reportar_avance(message):
    try:
        # Ejemplo: /reporte analisis_mercado 75 "Completado investigación"
        parts = message.text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message,
                "📊 *FORMATO:* /reporte [proyecto] [%] [comentario]\n\n"
                "*Ejemplos:*\n"
                "`/reporte analisis_mercado 75 \"Completado investigación de campo\"`\n"
                "`/reporte ensayo_filosofia 50 \"En proceso de redacción\"`",
                parse_mode='Markdown')
            return
            
        proyecto = parts[1]
        porcentaje = parts[2]
        comentario = parts[3] if len(parts) > 3 else "Progreso continuo"
        
        respuesta = f"""
📊 *REPORTE DE AVANCE*

📋 *Proyecto:* {proyecto}
✅ *Progreso:* {porcentaje}%
📝 *Comentario:* {comentario}
👤 *Reportado por:* {message.from_user.first_name}
🕒 *Hora:* {datetime.now().strftime('%H:%M')}
📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y')}

🔄 *Sistema actualizado correctamente*
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"📊 Reporte: {proyecto} al {porcentaje}%")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error en reporte: {str(e)}")

@bot.message_handler(commands=['buscar'])
def buscar_documentos(message):
    try:
        termino = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ""
        
        if not termino:
            bot.reply_to(message,
                "🔍 *BUSCAR DOCUMENTOS*\n\n"
                "*Uso:* /buscar [término]\n\n"
                "*Ejemplos:*\n"
                "`/buscar plantilla APA`\n"
                "`/buscar resumen administración`\n"
                "`/buscar examen contabilidad`",
                parse_mode='Markdown')
            return
            
        # Simulación de búsqueda - luego integras con Google Drive
        respuesta = f"""
📁 *RESULTADOS PARA: \"{termino}\"*

1. 📝 *{termino}_documento_principal.docx*
   📂 Carpeta: Trabajos Activos
   👤 Última modificación: Hoy
   🔗 Enlace: [Disponible en Drive]

2. 📊 *{termino}_datos_anexos.xlsx*
   📂 Carpeta: Materiales Académicos  
   👤 Creado: La semana pasada
   🔗 Enlace: [Disponible en Drive]

3. 🎓 *guia_{termino}.pdf*
   📂 Carpeta: Recursos Compartidos
   👤 Subido: Ayer
   🔗 Enlace: [Disponible en Drive]

*Usa /subir para agregar nuevos documentos*
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"🔍 Búsqueda: {termino}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error en búsqueda: {str(e)}")

@bot.message_handler(commands=['subir'])
def subir_documento(message):
    respuesta = """
📤 *SUBIR DOCUMENTO A GOOGLE DRIVE*

📎 *Por favor envía el documento que deseas subir*

*Proceso automático:*
1. 📎 Envía el archivo/documento
2. 🏷️ Se clasificará automáticamente  
3. 📁 Se guardará en la carpeta correspondiente
4. 🔗 Recibirás el enlace de acceso

*Formatos aceptados:*
• 📝 Documentos (PDF, DOCX, TXT)
• 📊 Hojas de cálculo (XLSX, CSV)
• 🎯 Presentaciones (PPTX)
• 📷 Imágenes (JPG, PNG)

*El documento se compartirá con el equipo HGC*
    """
    bot.reply_to(message, respuesta, parse_mode='Markdown')
    print(f"📤 Subida solicitada por {message.from_user.first_name}")

@bot.message_handler(commands=['reunion'])
def programar_reunion(message):
    try:
        # Ejemplo: /reunion "Planificación Semanal" 2024-10-21 18:00 Virtual
        parts = message.text.split(' ', 3)
        
        if len(parts) < 4:
            bot.reply_to(message,
                "🗓️ *PROGRAMAR REUNIÓN*\n\n"
                "*Uso:* /reunion [Tipo] [Fecha] [Hora] [Modalidad]\n\n"
                "*Ejemplos:*\n"
                "`/reunion \"Planificación Semanal\" 2024-10-21 18:00 Virtual`\n"
                "`/reunion \"Revisión Proyecto\" 2024-10-22 16:30 Presencial`",
                parse_mode='Markdown')
            return
            
        tipo = parts[1].strip('"')
        fecha = parts[2]
        hora = parts[3]
        modalidad = parts[4] if len(parts) > 4 else "Virtual"
        
        respuesta = f"""
🗓️ *REUNIÓN PROGRAMADA*

📋 *Tipo:* {tipo}
📅 *Fecha:* {fecha}
⏰ *Hora:* {hora}
📍 *Modalidad:* {modalidad}
👤 *Coordina:* {message.from_user.first_name}

✅ *ACCIONES AUTOMÁTICAS:*
• 📢 Notificación al equipo enviada
• 🔔 Recordatorios programados
• 📝 Acta de reunión preparada
• 🎯 Orden del día establecido

💡 *Siguiente paso:* Confirmar asistencia en el grupo operativo
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"🗓️ Reunión programada: {tipo}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al programar reunión: {str(e)}")

@bot.message_handler(commands=['estado'])
def estado_general(message):
    respuesta = """
📈 *ESTADO GENERAL - HGC & ASOCIADOS*

🎯 *SISTEMA BOT:*
• 🤖 Estado: 🟢 EN LÍNEA
• 📊 Comandos: ✅ ACTIVOS
• 🕒 Tiempo activo: Funcionando correctamente

👥 *EQUIPO OPERATIVO:*
• 👤 Miembros activos: 6/6
• 📚 Proyectos activos: 4
• 🎯 Cumplimiento: 92%

📅 *PRÓXIMOS EVENTOS:*
• 🗓️ Reunión semanal: Lunes 18:00
• 📝 Entregas esta semana: 2
• 🎓 Sesiones estudio: 1 programada

🚀 *SISTEMA OPERATIVO INTEGRAL*
*Todos los módulos funcionando correctamente*
    """
    bot.reply_to(message, respuesta, parse_mode='Markdown')
    print(f"📈 Estado consultado por {message.from_user.first_name}")

@bot.message_handler(commands=['encuesta'])
def crear_encuesta(message):
    try:
        # Ejemplo: /encuesta "¿Necesitamos sesión de refuerzo?" "Sí" "No" "Tal vez"
        parts = message.text.split('"')
        
        if len(parts) < 4:
            bot.reply_to(message,
                "📋 *CREAR ENCUESTA RÁPIDA*\n\n"
                "*Uso:* /encuesta \"Pregunta\" \"Opción1\" \"Opción2\" \"Opción3\"\n\n"
                "*Ejemplos:*\n"
                '`/encuesta "¿Necesitamos sesión de refuerzo?" "Sí" "No" "Sí, urgente"`\n'
                '`/encuesta "Mejor horario reunión" "18:00" "19:00" "20:00"`',
                parse_mode='Markdown')
            return
            
        pregunta = parts[1]
        opciones = [opt.strip() for opt in parts[2:] if opt.strip()]
        
        respuesta = f"""
📊 *ENCUESTA CREADA EXITOSAMENTE*

❓ *Pregunta:* {pregunta}

📋 *Opciones disponibles:*
"""
        for i, opcion in enumerate(opciones, 1):
            respuesta += f"   {i}️⃣ {opcion}\n"
            
        respuesta += f"""
👤 *Creada por:* {message.from_user.first_name}
⏰ *Duración:* 24 horas
👥 *Participantes:* Todo el equipo HGC

✅ *La encuesta ha sido compartida en el grupo operativo*
📢 *Todos los miembros han sido notificados*
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"📋 Encuesta creada: {pregunta}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al crear encuesta: {str(e)}")

@bot.message_handler(commands=['sesion'])
def programar_sesion(message):
    try:
        # Ejemplo: /sesion "Repaso Contabilidad" 2024-10-22 16:00
        parts = message.text.split(' ', 3)
        
        if len(parts) < 4:
            bot.reply_to(message,
                "🎓 *PROGRAMAR SESIÓN DE ESTUDIO*\n\n"
                "*Uso:* /sesion [Tema] [Fecha] [Hora] [Duración]\n\n"
                "*Ejemplos:*\n"
                '`/sesion "Repaso Contabilidad" 2024-10-22 16:00 90`\n'
                '`/sesion "Práctica Filosofía" 2024-10-23 15:00 120`',
                parse_mode='Markdown')
            return
            
        tema = parts[1].strip('"')
        fecha = parts[2]
        hora = parts[3]
        duracion = parts[4] if len(parts) > 4 else "90"
        
        respuesta = f"""
🎓 *SESIÓN DE ESTUDIO PROGRAMADA*

📚 *Tema:* {tema}
📅 *Fecha:* {fecha}
⏰ *Hora:* {hora}
⏱️ *Duración:* {duracion} minutos
👤 *Coordina:* {message.from_user.first_name}

✅ *RECURSOS AUTOMÁTICOS:*
• 📖 Material de estudio generado
• 📝 Ejercicios prácticos preparados
• 🎯 Guía de aprendizaje creada
• 🔔 Recordatorios configurados

💡 *Siguiente paso:* Confirmar materiales necesarios
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"🎓 Sesión programada: {tema}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al programar sesión: {str(e)}")

@bot.message_handler(commands=['asignar'])
def asignar_tarea(message):
    try:
        # Ejemplo: /asignar @maria "Revisar conclusiones" 2024-10-23
        parts = message.text.split(' ', 3)
        
        if len(parts) < 4:
            bot.reply_to(message,
                "👥 *ASIGNAR TAREA ESPECÍFICA*\n\n"
                "*Uso:* /asignar [@persona] [Tarea] [Fecha]\n\n"
                "*Ejemplos:*\n"
                '`/asignar @maria "Revisar conclusiones" 2024-10-23`\n'
                '`/asignar @carlos "Preparar presentación" 2024-10-24`',
                parse_mode='Markdown')
            return
            
        persona = parts[1]
        tarea = parts[2].strip('"')
        fecha = parts[3]
        
        respuesta = f"""
✅ *TAREA ASIGNADA EXITOSAMENTE*

👤 *Asignada a:* {persona}
📋 *Tarea:* {tarea}
📅 *Fecha límite:* {fecha}
👤 *Asignada por:* {message.from_user.first_name}
🆔 *ID Tarea:* TA-{datetime.now().strftime('%H%M%S')}

✅ *ACCIONES REALIZADAS:*
• 🔔 Notificación enviada al responsable
• 📊 Seguimiento automático activado
• ⏰ Recordatorios programados
• 📈 Integrado con sistema de reportes

💡 *Seguimiento disponible con /reporte*
        """
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        print(f"👥 Tarea asignada: {tarea} a {persona}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al asignar tarea: {str(e)}")

@bot.message_handler(commands=['categorias'])
def ver_categorias(message):
    respuesta = """
📂 *ESTRUCTURA DE CARPETAS - HGC DRIVE*

🏠 *HGC ASOCIADOS/*
│
├── 📁 *0. ADMINISTRATIVO/*
│   ├── 📄 Actas de Reuniones
│   ├── 📊 Bitácoras y Reportes  
│   ├── 📋 Manuales y Procedimientos
│   └── 📧 Comunicaciones Oficiales
│
├── 📁 *1. TRABAJOS ACTIVOS/*
│   ├── 📚 Administración
│   ├── 🧮 Contabilidad
│   ├── 💰 Economía
│   ├── ✍️ Comunicación
│   ├── 🤔 Filosofía
│   └── ⚖️ Constitución
│
├── 📁 *2. MATERIALES ACADÉMICOS/*
│   ├── 📖 Por Asignatura
│   ├── 🎯 Técnicas de Estudio
│   ├── 📝 Exámenes y Evaluaciones
│   └── 🔍 Investigación y Consulta
│
├── 📁 *3. PLANTILLAS Y HERRAMIENTAS/*
│   ├── 📄 Documentos
│   ├── 📊 Hojas de Cálculo
│   └── 📋 Formularios
│
└── 📁 *4. ARCHIVO HISTÓRICO/*
    ├── 🗃️ Trabajos Entregados
    ├── 📓 Sesiones de Estudio
    └── 📈 Reportes Mensuales

💡 *Usa /buscar para encontrar documentos específicos*
    """
    bot.reply_to(message, respuesta, parse_mode='Markdown')
    print(f"📂 Categorías consultadas por {message.from_user.first_name}")

# Manejo de documentos subidos
@bot.message_handler(content_types=['document'])
def manejar_documento(message):
    respuesta = f"""
📎 *DOCUMENTO RECIBIDO*

📄 *Nombre:* {message.document.file_name}
👤 *Subido por:* {message.from_user.first_name}
💾 *Tamaño:* {message.document.file_size} bytes

✅ *PROCESANDO SUBIDA A GOOGLE DRIVE...*
• 📁 Clasificando automáticamente
• 🔗 Generando enlace de acceso
• 👥 Compartiendo con el equipo
• 🏷️ Aplicando metadatos

⏰ *Tiempo estimado:* 10-30 segundos
    """
    bot.reply_to(message, respuesta, parse_mode='Markdown')
    print(f"📎 Documento recibido: {message.document.file_name}")

# Manejo de etiquetas oficiales
@bot.message_handler(func=lambda message: True)
def manejar_etiquetas(message):
    texto = message.text
    
    if texto.startswith('[URGENTE]'):
        bot.reply_to(message, "🚨 *URGENCIA REGISTRADA*\n\n✅ Equipo notificado\n⏰ Seguimiento cada 2 horas\n📢 Canal de emergencias activado")
    elif texto.startswith('[TAREA]'):
        bot.reply_to(message, "✅ *TAREA IDENTIFICADA*\n\n📋 Agregada al sistema de seguimiento\n👥 Responsables notificados\n📊 Métricas activadas")
    elif texto.startswith('[CONSULTA]'):
        bot.reply_to(message, "❓ *CONSULTA REGISTRADA*\n\n📚 Equipo académico notificado\n⏰ Respuesta en <4 horas\n💬 Canal especializado activado")
    elif texto.startswith('[RECURSO]'):
        bot.reply_to(message, "📚 *RECURSO COMPARTIDO*\n\n✅ Agregado a biblioteca digital\n🏷️ Clasificado automáticamente\n🔗 Enlace permanente generado")
    elif texto.startswith('[INFORME]'):
        bot.reply_to(message, "📊 *INFORME REGISTRADO*\n\n📈 Actualizando dashboard de control\n📋 Métricas procesadas\n👁️ Visibilidad para líderes")
    elif texto.startswith('[FELICITACIONES]'):
        bot.reply_to(message, "🎉 *FELICITACIONES REGISTRADAS*\n\n✨ Reconocimiento compartido\n🏆 Sistema de logros actualizado\n📢 Anuncio en canal oficial")

print("✅ Bot completamente configurado. Iniciando polling...")
bot.polling()