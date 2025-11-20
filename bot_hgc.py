import telebot
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import threading
import re
import time
import random
import os
import json
import sys
import shutil

# ==================== SISTEMA DE BACKUP ====================
try:
    from backup_system import SistemaBackup
    BACKUP_DISPONIBLE = True
    print("✅ Sistema de backup cargado correctamente")
except ImportError as e:
    BACKUP_DISPONIBLE = False
    print(f"⚠️ Sistema de backup no disponible: {e}")

# ==================== CONFIGURACIÓN DE TIMEOUT ====================
# Aumentar timeout para conexiones lentas
telebot.apihelper.READ_TIMEOUT = 30
telebot.apihelper.CONNECT_TIMEOUT = 30

# ==================== GESTIÓN SEGURA DEL TOKEN CON RUTA ABSOLUTA ====================
def obtener_ruta_base():
    """Obtener la ruta absoluta donde se está ejecutando el script"""
    if getattr(sys, 'frozen', False):
        # Si el script está ejecutándose como un ejecutable (pyinstaller)
        ruta_base = os.path.dirname(sys.executable)
    else:
        # Si se está ejecutando como script .py
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    
    print(f"📁 Ruta de ejecución detectada: {ruta_base}")
    return ruta_base

def obtener_token():
    """Obtener el token de forma segura desde archivo en la misma carpeta"""
    ruta_base = obtener_ruta_base()
    token_file = os.path.join(ruta_base, "bot_token.txt")
    
    print(f"🔍 Buscando token en: {token_file}")
    
    # Verificar si el archivo de token existe
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                token = f.read().strip()
            if token:
                print("✅ Token cargado desde archivo local")
                return token
        except Exception as e:
            print(f"❌ Error leyendo token: {e}")
    
    # Si no existe, solicitar token al usuario
    print("\n🔐 No se encontró token guardado.")
    print("Por favor ingresa el token de tu bot de Telegram:")
    print("(Puedes obtenerlo de @BotFather en Telegram)")
    token = input("Token: ").strip()
    
    # Guardar token para futuras ejecuciones
    try:
        with open(token_file, 'w', encoding='utf-8') as f:
            f.write(token)
        print(f"✅ Token guardado exitosamente en: {token_file}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el token: {e}")
    
    return token

TOKEN = obtener_token()
bot = telebot.TeleBot(TOKEN)

# ==================== SISTEMA DE PERSISTENCIA DE DATOS ====================
def obtener_ruta_datos():
    """Obtener ruta para guardar datos persistentes"""
    ruta_base = obtener_ruta_base()
    datos_dir = os.path.join(ruta_base, "datos_hgc")
    if not os.path.exists(datos_dir):
        os.makedirs(datos_dir)
    return datos_dir

def guardar_datos():
    """Guardar todos los datos en archivos JSON"""
    try:
        datos_dir = obtener_ruta_datos()
        
        # Guardar trabajos
        trabajos_file = os.path.join(datos_dir, "trabajos.json")
        with open(trabajos_file, 'w', encoding='utf-8') as f:
            json.dump(trabajos, f, ensure_ascii=False, indent=2)
        
        # Guardar encuestas
        encuestas_file = os.path.join(datos_dir, "encuestas.json")
        with open(encuestas_file, 'w', encoding='utf-8') as f:
            json.dump(encuestas, f, ensure_ascii=False, indent=2)
        
        # Guardar usuarios
        usuarios_file = os.path.join(datos_dir, "usuarios.json")
        with open(usuarios_file, 'w', encoding='utf-8') as f:
            json.dump(logger.usuarios_registrados, f, ensure_ascii=False, indent=2)
        
        # Guardar recordatorios
        recordatorios_file = os.path.join(datos_dir, "recordatorios.json")
        with open(recordatorios_file, 'w', encoding='utf-8') as f:
            json.dump(recordatorios, f, ensure_ascii=False, indent=2)
        
        logger.log('system', f'💾 Datos guardados en: {datos_dir}')
        return True
    except Exception as e:
        logger.log('error', f'Error guardando datos: {str(e)}')
        return False

def cargar_datos():
    """Cargar todos los datos desde archivos JSON"""
    global trabajos, encuestas, recordatorios
    
    try:
        datos_dir = obtener_ruta_datos()
        
        # Cargar trabajos
        trabajos_file = os.path.join(datos_dir, "trabajos.json")
        if os.path.exists(trabajos_file):
            with open(trabajos_file, 'r', encoding='utf-8') as f:
                trabajos_cargados = json.load(f)
                trabajos.extend(trabajos_cargados)
        
        # Cargar encuestas
        encuestas_file = os.path.join(datos_dir, "encuestas.json")
        if os.path.exists(encuestas_file):
            with open(encuestas_file, 'r', encoding='utf-8') as f:
                encuestas.extend(json.load(f))
        
        # Cargar usuarios
        usuarios_file = os.path.join(datos_dir, "usuarios.json")
        if os.path.exists(usuarios_file):
            with open(usuarios_file, 'r', encoding='utf-8') as f:
                usuarios_cargados = json.load(f)
                logger.usuarios_registrados.update(usuarios_cargados)
        
        # Cargar recordatorios
        recordatorios_file = os.path.join(datos_dir, "recordatorios.json")
        if os.path.exists(recordatorios_file):
            with open(recordatorios_file, 'r', encoding='utf-8') as f:
                recordatorios_cargados = json.load(f)
                recordatorios.update(recordatorios_cargados)
        
        logger.log('system', f'📂 Datos cargados: {len(trabajos)} trabajos, {len(logger.usuarios_registrados)} usuarios, {len(recordatorios)} recordatorios')
        return True
    except Exception as e:
        logger.log('error', f'Error cargando datos: {str(e)}')
        return False

# ==================== SISTEMA DE LOGGING MEJORADO ====================
class LoggerHGC:
    def __init__(self):
        self.contador_comandos = 0
        self.contador_botones = 0
        self.inicio_sistema = datetime.now()
        self.usuarios_registrados = {}
    
    def registrar_usuario(self, user_id, user_name):
        if user_id not in self.usuarios_registrados:
            self.usuarios_registrados[user_id] = {
                'nombre': user_name,
                'primer_ingreso': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'comandos_ejecutados': 0,
                'trabajos_creados': 0,
                'encuestas_creadas': 0,
                'recordatorios_recibidos': 0
            }
            self.log('user', f'Nuevo usuario registrado: {user_name}')
            return True
        else:
            self.usuarios_registrados[user_id]['ultima_actividad'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.usuarios_registrados[user_id]['comandos_ejecutados'] += 1
            return False
    
    def log(self, tipo, mensaje, usuario="Sistema"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        iconos = {
            'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌',
            'user': '👤', 'command': '📝', 'button': '🔘', 'session': '🎓',
            'poll': '📊', 'task': '✅', 'work': '📚', 'system': '🤖',
            'welcome': '🎉', 'search': '🔍', 'stats': '📈', 'reminder': '🔔'
        }
        
        icono = iconos.get(tipo, '🔵')
        print(f"{icono} {timestamp} - {usuario} - {mensaje}")
        
        if tipo == 'command': self.contador_comandos += 1
        if tipo == 'button': self.contador_botones += 1

# Instancia global del logger
logger = LoggerHGC()

# ==================== BASE DE DATOS OPTIMIZADA ====================
trabajos = []
encuestas = []
recordatorios = {}  # {user_id: {recordatorios_activos: bool, frecuencia: 'diario'/'semanal', hora: '09:00'}}

# ==================== SISTEMA DE RECORDATORIOS AUTOMÁTICOS ====================
class SistemaRecordatorios:
    def __init__(self):
        self.en_ejecucion = False
    
    def verificar_recordatorios_pendientes(self):
        """Verificar trabajos que necesitan recordatorios"""
        ahora = datetime.now()
        recordatorios_enviados = 0
        
        for trabajo in trabajos:
            if trabajo['estado'] == 'activo':
                fecha_hora_limite = datetime.strptime(trabajo['fecha_hora'], '%Y-%m-%d %H:%M')
                tiempo_restante = fecha_hora_limite - ahora
                horas_restantes = tiempo_restante.total_seconds() / 3600
                
                # Verificar si el usuario quiere recordatorios
                user_id = trabajo.get('user_id')
                if user_id and user_id in recordatorios and recordatorios[user_id].get('recordatorios_activos', True):
                    
                    # Recordatorios basados en tiempo restante
                    if 24 <= horas_restantes <= 25:  # 24 horas antes
                        self.enviar_recordatorio(trabajo, "24 HORAS", user_id)
                        recordatorios_enviados += 1
                    elif 12 <= horas_restantes <= 13:  # 12 horas antes
                        self.enviar_recordatorio(trabajo, "12 HORAS", user_id)
                        recordatorios_enviados += 1
                    elif 3 <= horas_restantes <= 4:  # 3 horas antes
                        self.enviar_recordatorio(trabajo, "3 HORAS", user_id)
                        recordatorios_enviados += 1
                    elif 1 <= horas_restantes <= 2:  # 1 hora antes
                        self.enviar_recordatorio(trabajo, "1 HORA", user_id)
                        recordatorios_enviados += 1
                    elif horas_restantes <= 0.5:  # 30 minutos antes (URGENTE)
                        self.enviar_recordatorio(trabajo, "30 MINUTOS", user_id)
                        recordatorios_enviados += 1
        
        return recordatorios_enviados
    
    def enviar_recordatorio(self, trabajo, tiempo_restante, user_id):
        """Enviar recordatorio individual a un usuario"""
        try:
            mensaje = f"""
🔔 *RECORDATORIO AUTOMÁTICO - {tiempo_restante}*

📋 *Trabajo:* {trabajo['nombre']}
📅 *Fecha límite:* {trabajo['fecha']}
⏰ *Hora límite:* {trabajo['hora']}
🎯 *Puntos:* {trabajo['puntos']}
📚 *Materia:* {trabajo.get('materia', 'General')}

💡 *¡No lo dejes para última hora!*
⏳ *Tiempo restante aproximado: {tiempo_restante}*

🚀 *¡Tú puedes! Organiza tu tiempo y logra tus metas académicas.*
            """
            
            bot.send_message(user_id, mensaje, parse_mode='Markdown')
            
            # Actualizar estadísticas
            if user_id in logger.usuarios_registrados:
                logger.usuarios_registrados[user_id]['recordatorios_recibidos'] += 1
            
            logger.log('reminder', f'Recordatorio enviado: {trabajo["nombre"]} - {tiempo_restante}')
            return True
            
        except Exception as e:
            logger.log('error', f'Error enviando recordatorio: {str(e)}')
            return False
    
    def verificar_recordatorios_diarios(self):
        """Verificar y enviar recordatorios diarios"""
        ahora = datetime.now()
        hora_actual = ahora.strftime('%H:%M')
        
        for user_id, config in recordatorios.items():
            if (config.get('recordatorios_activos', True) and 
                config.get('frecuencia') == 'diario' and 
                config.get('hora') == hora_actual):
                
                self.enviar_resumen_diario(user_id)
    
    def enviar_resumen_diario(self, user_id):
        """Enviar resumen diario de trabajos pendientes"""
        try:
            trabajos_usuario = [t for t in trabajos if t.get('user_id') == user_id and t['estado'] == 'activo']
            trabajos_proximos = []
            
            for trabajo in trabajos_usuario:
                fecha_hora_limite = datetime.strptime(trabajo['fecha_hora'], '%Y-%m-%d %H:%M')
                tiempo_restante = fecha_hora_limite - datetime.now()
                
                if tiempo_restante.days <= 7:  # Solo trabajos en los próximos 7 días
                    trabajos_proximos.append(trabajo)
            
            if not trabajos_proximos:
                return
            
            mensaje = f"""
📊 *RESUMEN DIARIO DE TRABAJOS* ☀️

*Tienes {len(trabajos_proximos)} trabajos próximos:*

"""
            
            for trabajo in trabajos_proximos[:5]:  # Máximo 5 trabajos
                fecha_hora_limite = datetime.strptime(trabajo['fecha_hora'], '%Y-%m-%d %H:%M')
                tiempo_restante = fecha_hora_limite - datetime.now()
                
                if tiempo_restante.days > 0:
                    tiempo_texto = f"{tiempo_restante.days} días"
                else:
                    horas = tiempo_restante.seconds // 3600
                    tiempo_texto = f"{horas} horas"
                
                mensaje += f"• **{trabajo['nombre']}** - ⏰ {tiempo_texto}\n"
                mensaje += f"  📅 {trabajo['fecha']} | 🎯 {trabajo['puntos']} pts\n\n"
            
            mensaje += "💡 *¡Planifica tu día y alcanza tus metas!* 🚀"
            
            bot.send_message(user_id, mensaje, parse_mode='Markdown')
            logger.log('reminder', f'Resumen diario enviado a usuario {user_id}')
            
        except Exception as e:
            logger.log('error', f'Error enviando resumen diario: {str(e)}')
    
    def iniciar_monitoreo_recordatorios(self):
        """Iniciar monitoreo continuo de recordatorios"""
        if self.en_ejecucion:
            return
        
        self.en_ejecucion = True
        
        def monitoreo_loop():
            while self.en_ejecucion:
                try:
                    # Verificar recordatorios por tiempo restante
                    recordatorios_enviados = self.verificar_recordatorios_pendientes()
                    
                    # Verificar recordatorios diarios
                    self.verificar_recordatorios_diarios()
                    
                    if recordatorios_enviados > 0:
                        logger.log('reminder', f'🔔 {recordatorios_enviados} recordatorios enviados')
                    
                    time.sleep(60)  # Verificar cada minuto
                    
                except Exception as e:
                    logger.log('error', f'Error en monitoreo de recordatorios: {str(e)}')
                    time.sleep(60)
        
        thread = threading.Thread(target=monitoreo_loop, daemon=True)
        thread.start()
        logger.log('system', '🔔 Sistema de recordatorios iniciado')

# Instancia global del sistema de recordatorios
sistema_recordatorios = SistemaRecordatorios()

# ==================== SISTEMA DE CONTADOR REGRESIVO AUTOMÁTICO ====================
class ContadorRegresivo:
    def __init__(self):
        self.mensajes_activos = {}
        self.actualizando = False
    
    def obtener_tiempo_restante_formateado(self, fecha_hora_str):
        """Calcular y formatear el tiempo restante para un trabajo"""
        try:
            fecha_hora_limite = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
            tiempo_restante = fecha_hora_limite - datetime.now()
            
            if tiempo_restante.total_seconds() <= 0:
                return "🔴 VENCIDO", "🔴"
            
            dias_restantes = tiempo_restante.days
            horas_restantes = tiempo_restante.seconds // 3600
            minutos_restantes = (tiempo_restante.seconds % 3600) // 60
            
            # Determinar color/emoji basado en urgencia
            if dias_restantes == 0 and horas_restantes < 24:
                if horas_restantes <= 3:
                    estado_urgencia = "🔴"
                elif horas_restantes <= 12:
                    estado_urgencia = "🟡"
                else:
                    estado_urgencia = "🟢"
            elif dias_restantes <= 3:
                estado_urgencia = "🔴"
            elif dias_restantes <= 7:
                estado_urgencia = "🟡"
            else:
                estado_urgencia = "🟢"
            
            # Formatear tiempo
            if dias_restantes > 0:
                mensaje_tiempo = f"{dias_restantes}d {horas_restantes}h"
            elif horas_restantes > 0:
                mensaje_tiempo = f"{horas_restantes}h {minutos_restantes}m"
            else:
                mensaje_tiempo = f"{minutos_restantes}m"
            
            return mensaje_tiempo, estado_urgencia
        except Exception as e:
            return "Error cálculo", "⚫"
    
    def actualizar_estados_trabajos(self):
        """Actualizar estados de trabajos automáticamente"""
        ahora = datetime.now()
        trabajos_actualizados = 0
        
        for trabajo in trabajos:
            if trabajo['estado'] == 'activo':
                fecha_hora_limite = datetime.strptime(trabajo['fecha_hora'], '%Y-%m-%d %H:%M')
                
                if fecha_hora_limite < ahora:
                    trabajo['estado'] = 'vencido'
                    trabajos_actualizados += 1
        
        return trabajos_actualizados
    
    def crear_mensaje_trabajos_activos(self):
        """Crear mensaje de trabajos activos con contador regresivo actualizado"""
        self.actualizar_estados_trabajos()
        trabajos_activos = [t for t in trabajos if t['estado'] == 'activo']
        
        # Crear markup con botones inline
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔄 Actualizar Ahora", callback_data="actualizar_contador"),
            InlineKeyboardButton("📊 Ver Estadísticas", callback_data="ver_estadisticas")
        )
        markup.row(
            InlineKeyboardButton("🔔 Recordatorios", callback_data="gestionar_recordatorios"),
            InlineKeyboardButton("⏰ Detalles Sistema", callback_data="ver_detalles")
        )
        
        if not trabajos_activos:
            mensaje = "✅ *NO HAY TRABAJOS ACTIVOS EN EL GRUPO*\n\n💡 ¡Sé el primero en registrar uno!"
            return mensaje, markup
        
        mensaje = "🔄 *TRABAJOS ACTIVOS - CONTADOR EN TIEMPO REAL* ⏰\n\n"
        
        for trabajo in trabajos_activos[:10]:
            mensaje_tiempo, estado_urgencia = self.obtener_tiempo_restante_formateado(trabajo['fecha_hora'])
            
            es_mio = "⭐ " if trabajo.get('user_id') else "👤 "
            
            mensaje += f"{estado_urgencia} {es_mio}*{trabajo['nombre']}*\n"
            mensaje += f"   👤 {trabajo['usuario']} | ⏰ {mensaje_tiempo}\n"
            mensaje += f"   🕒 {trabajo['fecha']} {trabajo['hora']} | 🎯 {trabajo['puntos']} pts\n"
            mensaje += f"   📚 {trabajo.get('materia', 'General')}\n\n"
        
        mensaje += f"📊 *Total activos: {len(trabajos_activos)}* | 🕐 *Actualizado: {datetime.now().strftime('%H:%M:%S')}*"
        mensaje += f"\n\n💡 *Usa los botones debajo para controlar el contador*"
        
        return mensaje, markup
    
    def iniciar_actualizacion_automatica(self, chat_id, message_id):
        """Iniciar actualización automática del contador"""
        if self.actualizando:
            return
        
        self.actualizando = True
        self.mensajes_activos[message_id] = {
            'chat_id': chat_id,
            'ultima_actualizacion': datetime.now()
        }
        
        def actualizar_loop():
            while message_id in self.mensajes_activos:
                try:
                    mensaje, markup = self.crear_mensaje_trabajos_activos()
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=mensaje,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    time.sleep(30)
                except Exception as e:
                    if "message is not modified" not in str(e):
                        logger.log('error', f'Error actualizando contador: {str(e)}')
                    time.sleep(30)
        
        thread = threading.Thread(target=actualizar_loop, daemon=True)
        thread.start()

# Instancia global del contador regresivo
contador_regresivo = ContadorRegresivo()

# ==================== SISTEMA DE BACKUP INSTANCIADO ====================
sistema_backup = SistemaBackup(obtener_ruta_datos) if BACKUP_DISPONIBLE else None

# ==================== TECLADOS PERSONALIZADOS MEJORADOS ====================
def crear_teclado_principal():
    """Teclado principal con navegación clara"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("📝 Gestión Académica"))
    markup.row(KeyboardButton("ℹ️ Información"), KeyboardButton("🆘 Ayuda"))
    markup.row(KeyboardButton("🔄 Trabajos Activos"), KeyboardButton("🔔 Recordatorios"))
    return markup

def crear_teclado_gestion_academica():
    """Teclado completo para gestión académica"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("🆕 Nuevo Trabajo"), KeyboardButton("📋 Ver Ejemplos"))
    markup.row(KeyboardButton("📊 Mi Progreso"), KeyboardButton("✅ Completados"))
    markup.row(KeyboardButton("🔄 Trabajos Activos"), KeyboardButton("📈 Estado General"))
    markup.row(KeyboardButton("🔔 Recordatorios"), KeyboardButton("🎯 Menú Principal"))
    return markup

def crear_teclado_recordatorios():
    """Teclado para gestión de recordatorios"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("🔔 Activar Recordatorios"), KeyboardButton("🔕 Desactivar Recordatorios"))
    markup.row(KeyboardButton("📅 Recordatorio Diario"), KeyboardButton("⚙️ Configurar Hora"))
    markup.row(KeyboardButton("📋 Ver Configuración"), KeyboardButton("🎯 Menú Principal"))
    return markup

def crear_teclado_inicio():
    """Teclado simplificado para el inicio (igual al principal)"""
    return crear_teclado_principal()

# ==================== INICIALIZACIÓN DEL SISTEMA ====================
def inicializar_sistema():
    logger.log('system', '🚀 INICIANDO SISTEMA HGC BOT - RECORDATORIOS ACTIVADOS')
    logger.log('system', '🔐 Token gestionado de forma segura')
    logger.log('system', '💾 Sistema de persistencia de datos activado')
    logger.log('system', '⏰ Contador regresivo automático activado')
    logger.log('system', '🔔 Sistema de recordatorios implementado')
    logger.log('system', '🔘 Botones inline funcionando')
    
    if BACKUP_DISPONIBLE:
        logger.log('system', '📦 Sistema de backup activado')
    else:
        logger.log('warning', '⚠️ Sistema de backup no disponible')
    
    # Cargar datos existentes
    cargar_datos()
    
    # Iniciar sistema de recordatorios
    sistema_recordatorios.iniciar_monitoreo_recordatorios()
    
    print("=" * 60)

# ==================== COMANDO /START - BIENVENIDA MEJORADA ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    es_nuevo_usuario = logger.registrar_usuario(user_id, user_name)
    
    # Inicializar recordatorios para el usuario
    if user_id not in recordatorios:
        recordatorios[user_id] = {
            'recordatorios_activos': True,
            'frecuencia': 'diario',
            'hora': '09:00'
        }
    
    # Guardar datos después de registrar usuario
    guardar_datos()
    
    mensajes_bienvenida = [
        f"""
🚀 *¡BIENVENIDO/A {user_name.upper()} A HGC!*

🌟 *Tu Centro de Gestión Académica Inteligente* 🌟

*¿Qué necesitas hacer hoy?*

📝 *Gestión Académica* - Registrar y gestionar trabajos
ℹ️ *Información* - Conoce el sistema
🆘 *Ayuda* - Soporte y guías
🔄 *Trabajos Activos* - Ver trabajos con contador regresivo en tiempo real
🔔 *Recordatorios* - Notificaciones automáticas para tus trabajos

*¡Tu éxito académico comienza aquí!* 💫
        """,
        
        f"""
🎉 *¡HOLA {user_name.upper()}! BIENVENIDO/A A HGC*

⚡ *La Revolución Académica ha Llegado* ⚡

*Explora las opciones:*

• 📝 *Gestión Académica* - Sistema completo
• ℹ️ *Información* - Todo sobre HGC  
• 🆘 *Ayuda* - Soporte inmediato
• 🔄 *Trabajos Activos* - Contador regresivo en vivo
• 🔔 *Recordatorios* - Alertas automáticas

*¡Comienza ahora con los botones!* 🚀
        """
    ]
    
    mensaje_bienvenida = random.choice(mensajes_bienvenida)
    
    if es_nuevo_usuario:
        logger.log('welcome', f'Nuevo usuario inició el bot: {user_name}')
    else:
        logger.log('user', f'Usuario reinició el bot: {user_name}')
    
    bot.reply_to(message, mensaje_bienvenida, parse_mode='Markdown', 
                reply_markup=crear_teclado_principal())

# ==================== SISTEMA DE REGISTRO DE TRABAJOS CON PERSISTENCIA ====================
def procesar_registro_trabajo(message):
    """Procesar el comando /registrar con parámetros"""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    texto = message.text
    
    logger.log('command', f'Procesando registro: {texto}', user_name)
    
    # Verificar si es registro múltiple (varias líneas)
    lineas = texto.strip().split('\n')
    if len(lineas) > 1:
        # Es registro múltiple
        procesar_registro_multiple(message)
        return
    
    # Es registro individual
    if procesar_registro_trabajo_individual(message):
        # Calcular tiempo hasta la fecha límite
        trabajo = trabajos[-1]  # Último trabajo registrado
        fecha_hora_limite = datetime.strptime(trabajo['fecha_hora'], '%Y-%m-%d %H:%M')
        tiempo_restante = fecha_hora_limite - datetime.now()
        
        dias_restantes = tiempo_restante.days
        horas_restantes = tiempo_restante.seconds // 3600
        minutos_restantes = (tiempo_restante.seconds % 3600) // 60
        
        # Formatear tiempo restante
        if dias_restantes > 0:
            tiempo_formateado = f"{dias_restantes} días, {horas_restantes} horas"
        elif horas_restantes > 0:
            tiempo_formateado = f"{horas_restantes} horas, {minutos_restantes} minutos"
        else:
            tiempo_formateado = f"{minutos_restantes} minutos"
        
        # Mensaje de confirmación
        confirmacion = f"""
✅ *TRABAJO REGISTRADO EXITOSAMENTE*

📝 *DETALLES DEL TRABAJO:*
• **📋 Nombre:** {trabajo['nombre']}
• **📅 Fecha límite:** {trabajo['fecha']}
• **⏰ Hora límite:** {trabajo['hora']}
• **⏳ Tiempo restante:** {tiempo_formateado}
• **🎯 Puntos académicos:** {trabajo['puntos']}
• **📚 Materia:** {trabajo['materia']}
• **🟢 Estado:** Activo

👤 *Registrado por:* {user_name}
📅 *Fecha de registro:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

🚀 *¡Excelente! Tu trabajo ha sido registrado exitosamente.*
💡 *Ve a "Trabajos Activos" para ver el contador regresivo en tiempo real*
🔔 *Recibirás recordatorios automáticos antes del vencimiento*
        """
        
        bot.reply_to(message, confirmacion, parse_mode='Markdown')
    else:
        bot.reply_to(message, 
                    """
❌ *ERROR EN EL REGISTRO*

💡 *Por favor usa el formato correcto:*
`/registrar "Nombre del trabajo" FECHA HORA PUNTOS MATERIA`

🚀 *Ejemplos:*
`/registrar "Mi trabajo" 2024-11-05 23:59 20`
`/registrar "Proyecto" 2024-11-08 14:00 30 Matemáticas`

*¡Estamos aquí para ayudarte!* 🤝
                    """, 
                    parse_mode='Markdown')

def procesar_registro_multiple(message):
    """Procesar múltiples trabajos en un solo mensaje"""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    texto = message.text
    
    # Dividir el mensaje en líneas
    lineas = texto.strip().split('\n')
    trabajos_registrados = 0
    errores = 0
    
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith('/registrar'):
            try:
                # Crear un mensaje simulado para procesar cada trabajo
                mensaje_simulado = type('obj', (object,), {
                    'from_user': message.from_user,
                    'chat': message.chat,
                    'text': linea
                })
                
                # Procesar el trabajo individual
                if procesar_registro_trabajo_individual(mensaje_simulado):
                    trabajos_registrados += 1
                else:
                    errores += 1
                    
            except Exception as e:
                errores += 1
                logger.log('error', f'Error en registro múltiple: {str(e)}', user_name)
    
    # Resumen del registro múltiple
    if trabajos_registrados > 0:
        resumen = f"""
✅ *REGISTRO MÚLTIPLE COMPLETADO*

📊 *Resultado:*
• ✅ Trabajos registrados: *{trabajos_registrados}*
• ❌ Errores: *{errores}*
• 📝 Total procesados: *{len(lineas)}*

🎯 *Tus {trabajos_registrados} trabajos han sido registrados exitosamente!*
💡 *Ve a "Trabajos Activos" para ver los contadores regresivos*
🔔 *Recibirás recordatorios automáticos para cada trabajo*
        """
        bot.send_message(message.chat.id, resumen, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 
                        "❌ *No se pudieron registrar los trabajos*\n\n💡 Verifica el formato de cada línea.", 
                        parse_mode='Markdown')

def procesar_registro_trabajo_individual(message):
    """Procesar un solo trabajo - función auxiliar para registro múltiple"""
    try:
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        texto = message.text
        
        # Extraer parámetros del comando /registrar
        partes = texto.replace('/registrar', '', 1).strip()
        
        # Verificar si tiene comillas para el nombre
        if '"' in partes:
            partes_comillas = partes.split('"')
            if len(partes_comillas) < 3:
                return False
            
            nombre = partes_comillas[1].strip()
            parametros_restantes = partes_comillas[2].strip().split()
        else:
            partes_simple = partes.split()
            if len(partes_simple) < 4:
                return False
            
            nombre = partes_simple[0]
            parametros_restantes = partes_simple[1:]
        
        if not nombre or len(parametros_restantes) < 3:
            return False
        
        # Procesar fecha y hora
        fecha_str = parametros_restantes[0]
        hora_str = parametros_restantes[1]
        
        try:
            # Procesar fecha
            for fmt_fecha in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    fecha = datetime.strptime(fecha_str, fmt_fecha)
                    break
                except ValueError:
                    continue
            else:
                return False
            
            # Procesar hora
            try:
                hora = datetime.strptime(hora_str, '%H:%M').time()
            except:
                return False
            
            # Combinar fecha y hora
            fecha_hora = datetime.combine(fecha.date(), hora)
            
            if fecha_hora < datetime.now():
                return False
            
            fecha_formateada = fecha.strftime('%Y-%m-%d')
            hora_formateada = hora.strftime('%H:%M')
            fecha_hora_formateada = fecha_hora.strftime('%Y-%m-%d %H:%M')
            
        except:
            return False
        
        # Procesar puntos
        try:
            puntos = int(parametros_restantes[2])
            if puntos <= 0 or puntos > 1000:
                return False
        except:
            return False
        
        # Procesar materia (opcional)
        materia = " ".join(parametros_restantes[3:]) if len(parametros_restantes) > 3 else "General"
        if len(materia) > 50:
            materia = materia[:47] + "..."
        
        # Crear trabajo
        trabajo_id = len(trabajos) + 1
        nuevo_trabajo = {
            'id': trabajo_id,
            'nombre': nombre,
            'fecha': fecha_formateada,
            'hora': hora_formateada,
            'fecha_hora': fecha_hora_formateada,
            'puntos': puntos,
            'materia': materia,
            'estado': 'activo',
            'avance': 0,
            'usuario': user_name,
            'user_id': user_id,
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        trabajos.append(nuevo_trabajo)
        logger.log('work', f'Trabajo registrado: {nombre}', user_name)
        
        # Actualizar estadísticas del usuario
        if user_id in logger.usuarios_registrados:
            logger.usuarios_registrados[user_id]['trabajos_creados'] += 1
        
        # GUARDAR DATOS INMEDIATAMENTE después de cada registro
        guardar_datos()
        
        return True
        
    except Exception as e:
        logger.log('error', f'Error en registro individual: {str(e)}', message.from_user.first_name)
        return False

# ==================== SISTEMA DE TRABAJOS ACTIVOS CON CONTADOR REGRESIVO ====================
def mostrar_trabajos_activos(message):
    """Mostrar trabajos activos con contador regresivo automático"""
    user_name = message.from_user.first_name
    logger.log('button', f'Mostrando trabajos activos con contador', user_name)
    
    # Obtener mensaje y markup
    mensaje, markup = contador_regresivo.crear_mensaje_trabajos_activos()
    
    try:
        # SIEMPRE enviar con markup (botones inline)
        sent_message = bot.send_message(
            message.chat.id, 
            mensaje, 
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        logger.log('system', f'✅ Mensaje enviado con ID: {sent_message.message_id}')
        logger.log('system', f'✅ Botones inline enviados correctamente')
        
        # Iniciar actualización automática solo si hay trabajos activos
        trabajos_activos = [t for t in trabajos if t['estado'] == 'activo']
        if trabajos_activos:
            contador_regresivo.iniciar_actualizacion_automatica(
                message.chat.id, 
                sent_message.message_id
            )
            logger.log('system', f'🔄 Actualización automática iniciada para {len(trabajos_activos)} trabajos')
            
    except Exception as e:
        logger.log('error', f'❌ Error enviando mensaje: {str(e)}')
        # Intentar sin markup como fallback
        try:
            bot.send_message(
                message.chat.id, 
                "❌ Error mostrando trabajos activos. Intenta nuevamente.", 
                parse_mode='Markdown'
            )
        except Exception as e2:
            logger.log('error', f'❌ Error incluso sin markup: {str(e2)}')

# ==================== SISTEMA DE RECORDATORIOS - MANEJADORES ====================
@bot.message_handler(func=lambda message: message.text == "🔔 Recordatorios")
def menu_recordatorios(message):
    """Mostrar menú de gestión de recordatorios"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Inicializar configuración si no existe
    if user_id not in recordatorios:
        recordatorios[user_id] = {
            'recordatorios_activos': True,
            'frecuencia': 'diario',
            'hora': '09:00'
        }
        guardar_datos()
    
    config = recordatorios[user_id]
    estado = "🟢 ACTIVADOS" if config['recordatorios_activos'] else "🔴 DESACTIVADOS"
    
    menu = f"""
🔔 *GESTIÓN DE RECORDATORIOS - {user_name}*

*Configuración actual:*
• **Estado:** {estado}
• **Frecuencia:** {config['frecuencia'].upper()}
• **Hora:** {config['hora']}

*¿Qué deseas hacer?*

🔔 *Activar Recordatorios* - Recibir notificaciones automáticas
🔕 *Desactivar Recordatorios* - Pausar todas las notificaciones
📅 *Recordatorio Diario* - Resumen diario de trabajos
⚙️ *Configurar Hora* - Establecer hora para recordatorios diarios
📋 *Ver Configuración* - Ver configuración actual

*💡 Los recordatorios automáticos te avisarán:*
• 24 horas antes del vencimiento
• 12 horas antes del vencimiento  
• 3 horas antes del vencimiento
• 1 hora antes del vencimiento
• 30 minutos antes (URGENTE)
    """
    
    bot.send_message(message.chat.id, menu, parse_mode='Markdown',
                    reply_markup=crear_teclado_recordatorios())

@bot.message_handler(func=lambda message: message.text == "🔔 Activar Recordatorios")
def activar_recordatorios(message):
    """Activar recordatorios para el usuario"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id not in recordatorios:
        recordatorios[user_id] = {
            'recordatorios_activos': True,
            'frecuencia': 'diario',
            'hora': '09:00'
        }
    else:
        recordatorios[user_id]['recordatorios_activos'] = True
    
    guardar_datos()
    
    respuesta = f"""
✅ *RECORDATORIOS ACTIVADOS* 🔔

¡Perfecto {user_name}! Ahora recibirás recordatorios automáticos para tus trabajos.

*Recordatorios que recibirás:*
• 🕐 24 horas antes del vencimiento
• 🕛 12 horas antes del vencimiento  
• 🕒 3 horas antes del vencimiento
• 🕐 1 hora antes del vencimiento
• 🔴 30 minutos antes (URGENTE)

*Además:*
• 📅 Resumen diario a las {recordatorios[user_id]['hora']}
• 🔔 Notificaciones de trabajos próximos

*¡Nunca más se te pasará una fecha límite!* 🚀
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🔕 Desactivar Recordatorios")
def desactivar_recordatorios(message):
    """Desactivar recordatorios para el usuario"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id in recordatorios:
        recordatorios[user_id]['recordatorios_activos'] = False
        guardar_datos()
    
    respuesta = f"""
🔕 *RECORDATORIOS DESACTIVADOS*

De acuerdo {user_name}, has desactivado los recordatorios automáticos.

*Ya no recibirás:*
• Recordatorios de vencimiento
• Resúmenes diarios
• Notificaciones de trabajos próximos

*💡 Puedes reactivarlos en cualquier momento usando* `🔔 Activar Recordatorios`

*¡Recuerda revisar manualmente tus trabajos activos!* 📝
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📅 Recordatorio Diario")
def configurar_recordatorio_diario(message):
    """Configurar recordatorio diario"""
    user_id = message.from_user.id
    
    if user_id not in recordatorios:
        recordatorios[user_id] = {
            'recordatorios_activos': True,
            'frecuencia': 'diario',
            'hora': '09:00'
        }
    else:
        recordatorios[user_id]['frecuencia'] = 'diario'
    
    guardar_datos()
    
    respuesta = f"""
📅 *RECORDATORIO DIARIO ACTIVADO*

¡Perfecto! Ahora recibirás un resumen diario de tus trabajos pendientes.

*¿Qué incluye el resumen diario?*
• 📋 Lista de trabajos activos
• ⏰ Tiempo restante para cada uno
• 🎯 Puntos académicos
• 💡 Recomendaciones de prioridad

*🕐 Hora actual:* {recordatorios[user_id]['hora']}

*¿Quieres cambiar la hora? Usa* `⚙️ Configurar Hora`
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⚙️ Configurar Hora")
def configurar_hora_recordatorio(message):
    """Configurar hora para recordatorios diarios"""
    user_id = message.from_user.id
    
    respuesta = """
⚙️ *CONFIGURAR HORA DE RECORDATORIOS*

Para establecer una nueva hora para tus recordatorios diarios, envía el comando:

`/hora_recordatorio HH:MM`

*Ejemplos:*
`/hora_recordatorio 09:00` - Para las 9:00 AM
`/hora_recordatorio 18:30` - Para las 6:30 PM
`/hora_recordatorio 08:00` - Para las 8:00 AM

*💡 Recomendación:*
Establece una hora en la que normalmente revises tus mensajes, como por la mañana o antes de comenzar a estudiar.
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown')

@bot.message_handler(commands=['hora_recordatorio'])
def establecer_hora_recordatorio(message):
    """Establecer hora específica para recordatorios"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    texto = message.text.strip()
    
    # Extraer hora del comando
    partes = texto.split()
    if len(partes) < 2:
        bot.reply_to(message, "❌ *Formato incorrecto.* Usa: `/hora_recordatorio HH:MM`", parse_mode='Markdown')
        return
    
    hora_str = partes[1]
    
    try:
        # Validar formato de hora
        datetime.strptime(hora_str, '%H:%M')
        
        # Actualizar configuración
        if user_id not in recordatorios:
            recordatorios[user_id] = {
                'recordatorios_activos': True,
                'frecuencia': 'diario',
                'hora': hora_str
            }
        else:
            recordatorios[user_id]['hora'] = hora_str
        
        guardar_datos()
        
        respuesta = f"""
✅ *HORA CONFIGURADA EXITOSAMENTE* ⏰

¡Perfecto {user_name}! Has establecido las *{hora_str}* como hora para tus recordatorios diarios.

*Ahora recibirás:*
• 📅 Resumen diario a las {hora_str}
• 🔔 Recordatorios automáticos de vencimientos
• 📊 Actualizaciones de tus trabajos pendientes

*¡Tu organización académica está en marcha!* 🚀
        """
        
        bot.reply_to(message, respuesta, parse_mode='Markdown')
        
    except ValueError:
        bot.reply_to(message, "❌ *Formato de hora inválido.* Usa el formato HH:MM (ej: 09:00 o 18:30)", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📋 Ver Configuración")
def ver_configuracion_recordatorios(message):
    """Mostrar configuración actual de recordatorios"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id not in recordatorios:
        config = {
            'recordatorios_activos': False,
            'frecuencia': 'No configurada',
            'hora': 'No configurada'
        }
    else:
        config = recordatorios[user_id]
    
    estado = "🟢 ACTIVADOS" if config.get('recordatorios_activos') else "🔴 DESACTIVADOS"
    frecuencia = config.get('frecuencia', 'No configurada').upper()
    hora = config.get('hora', 'No configurada')
    
    # Obtener estadísticas
    trabajos_usuario = [t for t in trabajos if t.get('user_id') == user_id and t['estado'] == 'activo']
    recordatorios_recibidos = logger.usuarios_registrados.get(user_id, {}).get('recordatorios_recibidos', 0)
    
    respuesta = f"""
🔔 *CONFIGURACIÓN DE RECORDATORIOS - {user_name}*

*⚙️ Configuración Actual:*
• **Estado:** {estado}
• **Frecuencia:** {frecuencia}
• **Hora diaria:** {hora}

*📊 Estadísticas:*
• **Trabajos activos:** {len(trabajos_usuario)}
• **Recordatorios recibidos:** {recordatorios_recibidos}

*💡 Funcionalidades:*
• Recordatorios automáticos de vencimiento
• Resumen diario de trabajos
• Alertas de prioridad
• Notificaciones urgentes

*¿Necesitas cambiar algo? Usa los botones de abajo.*
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown')

# ==================== SISTEMA DE BACKUP - COMANDOS ====================
@bot.message_handler(commands=['backup'])
def comando_backup(message):
    """Crear backup manualmente"""
    if not BACKUP_DISPONIBLE:
        bot.reply_to(message, "❌ Sistema de backup no disponible")
        return
    
    bot.reply_to(message, "🔄 Creando backup manual...")
    
    if sistema_backup.crear_backup_seguro():
        bot.reply_to(message, "✅ Backup creado exitosamente")
    else:
        bot.reply_to(message, "❌ Error creando backup")

@bot.message_handler(commands=['listar_backups'])
def comando_listar_backups(message):
    """Listar backups disponibles"""
    if not BACKUP_DISPONIBLE:
        bot.reply_to(message, "❌ Sistema de backup no disponible")
        return
    
    backups = sistema_backup.listar_backups()
    
    if not backups:
        bot.reply_to(message, "📭 No hay backups disponibles")
        return
    
    mensaje = "📦 *BACKUPS DISPONIBLES*\n\n"
    for i, backup in enumerate(backups[:10]):  # Mostrar solo últimos 10
        mensaje += f"*{i+1}. {backup['nombre']}*\n"
        mensaje += f"   📅 {backup['fecha_creacion'].strftime('%Y-%m-%d %H:%M')}\n"
        mensaje += f"   📊 {backup['tamaño']} bytes\n\n"
    
    mensaje += f"Total: {len(backups)} backups"
    bot.reply_to(message, mensaje, parse_mode='Markdown')

# ==================== MANEJADOR DE BOTONES INLINE MEJORADO ====================
@bot.callback_query_handler(func=lambda call: True)
def manejar_botones_inline(call):
    """Manejar botones inline"""
    try:
        logger.log('button', f'Botón inline presionado: {call.data}')
        
        if call.data == "actualizar_contador":
            mensaje, markup = contador_regresivo.crear_mensaje_trabajos_activos()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=mensaje,
                parse_mode='Markdown',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "✅ Contador actualizado - " + datetime.now().strftime("%H:%M:%S"))
            
        elif call.data == "ver_estadisticas":
            trabajos_activos = [t for t in trabajos if t['estado'] == 'activo']
            trabajos_vencidos = [t for t in trabajos if t['estado'] == 'vencido']
            total_recordatorios = sum(u.get('recordatorios_recibidos', 0) for u in logger.usuarios_registrados.values())
            
            detalles = f"""
📊 *ESTADÍSTICAS DETALLADAS - HGC*

📝 *TRABAJOS:*
• 🟢 Activos: *{len(trabajos_activos)}*
• 🔴 Vencidos: *{len(trabajos_vencidos)}*
• 📋 Total: *{len(trabajos)}*

👥 *USUARIOS:*
• 👤 Registrados: *{len(logger.usuarios_registrados)}*
• 🔔 Recordatorios enviados: *{total_recordatorios}*

⏰ *SISTEMA:*
• 🚀 Inicio: *{logger.inicio_sistema.strftime('%Y-%m-%d %H:%M')}*
• 🔄 Actualización: *Cada 30 segundos*
• 🔔 Recordatorios: *Sistema activo*
• 💾 Datos guardados: *{datetime.now().strftime('%H:%M:%S')}*

*Sistema funcionando óptimamente* 🚀
            """
            bot.answer_callback_query(call.id, "📊 Estadísticas generadas")
            bot.send_message(call.message.chat.id, detalles, parse_mode='Markdown')
            
        elif call.data == "gestionar_recordatorios":
            user_id = call.from_user.id
            if user_id not in recordatorios:
                recordatorios[user_id] = {
                    'recordatorios_activos': True,
                    'frecuencia': 'diario',
                    'hora': '09:00'
                }
                guardar_datos()
            
            config = recordatorios[user_id]
            estado = "🟢 ACTIVADOS" if config['recordatorios_activos'] else "🔴 DESACTIVADOS"
            
            respuesta = f"""
🔔 *GESTIÓN RÁPIDA DE RECORDATORIOS*

*Configuración actual:*
• **Estado:** {estado}
• **Hora diaria:** {config['hora']}

*Comandos rápidos:*
`/hora_recordatorio 09:00` - Cambiar hora
`🔔 Recordatorios` - Menú completo

*¡Mantente al día con tus trabajos!* 📚
            """
            bot.answer_callback_query(call.id, "🔔 Gestión de recordatorios")
            bot.send_message(call.message.chat.id, respuesta, parse_mode='Markdown')
            
        elif call.data == "ver_detalles":
            trabajos_activos = [t for t in trabajos if t['estado'] == 'activo']
            total_recordatorios = sum(u.get('recordatorios_recibidos', 0) for u in logger.usuarios_registrados.values())
            
            detalles = f"""
📋 *DETALLES RÁPIDOS DEL SISTEMA*

• 🟢 Trabajos activos: *{len(trabajos_activos)}*
• 👤 Usuarios: *{len(logger.usuarios_registrados)}*
• 🔔 Recordatorios enviados: *{total_recordatorios}*
• 🕐 Actualizado: *{datetime.now().strftime('%H:%M:%S')}*

*Sistema HGC - Tu asistente académico inteligente* 🎓
            """
            bot.answer_callback_query(call.id, "📋 Detalles del sistema")
            bot.send_message(call.message.chat.id, detalles, parse_mode='Markdown')
            
    except Exception as e:
        if "message is not modified" not in str(e):
            bot.answer_callback_query(call.id, "❌ Error al procesar")
            logger.log('error', f'Error en botón inline: {str(e)}')

# ==================== MANEJADOR PRINCIPAL DE BOTONES ACTUALIZADO ====================
@bot.message_handler(func=lambda message: True)
def manejar_botones_teclado(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    texto = message.text
    
    logger.log('button', f'Botón teclado: {texto}', user_name)
    
    # ========== BOTONES DE NAVEGACIÓN PRINCIPAL ==========
    if texto == "🎯 Menú Principal":
        mostrar_menu_principal(message)
        return
        
    elif texto == "📝 Gestión Académica":
        mostrar_menu_gestion_academica(message)
        return
        
    elif texto == "ℹ️ Información":
        info_comando(message)
        return
        
    elif texto == "🆘 Ayuda":
        ayuda_comando(message)
        return
        
    elif texto == "🔄 Trabajos Activos":
        mostrar_trabajos_activos(message)
        return
        
    elif texto == "🔔 Recordatorios":
        menu_recordatorios(message)
        return
    
    # ========== BOTONES DE GESTIÓN ACADÉMICA ==========
    elif texto == "🆕 Nuevo Trabajo":
        mostrar_formato_registro(message)
        return
        
    elif texto == "📋 Ver Ejemplos":
        mostrar_ejemplos_completos(message)
        return
        
    elif texto == "📊 Mi Progreso":
        mostrar_progreso_personal(message)
        return
        
    elif texto == "✅ Completados":
        mostrar_trabajos_completados(message)
        return
        
    elif texto == "📈 Estado General":
        mostrar_estado_general(message)
        return
    
    # ========== COMANDOS DIRECTOS ==========
    elif texto.startswith('/registrar') and len(texto.split()) > 1:
        procesar_registro_trabajo(message)
        return
        
    elif texto.startswith('/'):
        # Manejar comandos tradicionales
        if texto == '/ayuda':
            ayuda_comando(message)
        elif texto == '/info':
            info_comando(message)
        elif texto == '/faq':
            faq_comando(message)
        elif texto == '/start':
            start(message)
        elif texto == '/registrar':
            mostrar_menu_gestion_academica(message)
        elif texto == '/hora_recordatorio':
            establecer_hora_recordatorio(message)
        elif texto == '/backup':
            comando_backup(message)
        elif texto == '/listar_backups':
            comando_listar_backups(message)
        else:
            mostrar_comando_no_reconocido(message)
    else:
        mostrar_comando_no_reconocido(message)

# ==================== FUNCIONES DE NAVEGACIÓN MEJORADAS ====================
def mostrar_menu_principal(message):
    """Mostrar menú principal con teclado correspondiente"""
    menu = """
🎯 *MENÚ PRINCIPAL HGC*

*Opciones disponibles:*

📝 *Gestión Académica* - Sistema completo de trabajos
ℹ️ *Información* - Centro de información HGC
🆘 *Ayuda* - Centro de ayuda y soporte
🔄 *Trabajos Activos* - Ver trabajos con contador regresivo en tiempo real
🔔 *Recordatorios* - Notificaciones automáticas para tus trabajos

*Comandos rápidos:*
`/registrar` - Acceso directo a gestión
`/info` - Información del sistema
`/ayuda` - Soporte técnico

*¡Navega fácilmente con los botones!* 🚀
    """
    
    bot.send_message(message.chat.id, menu, parse_mode='Markdown',
                    reply_markup=crear_teclado_principal())

def mostrar_menu_gestion_academica(message):
    """Mostrar menú de gestión académica"""
    user_name = message.from_user.first_name
    
    menu = f"""
🎯 *GESTIÓN ACADÉMICA - {user_name}*

*¿Qué necesitas gestionar?*

🆕 *Nuevo Trabajo* - Registrar trabajos individuales o múltiples
📋 *Ver Ejemplos* - Formatos listos para usar
📊 *Mi Progreso* - Tu avance personal detallado
✅ *Completados* - Historial de trabajos terminados
🔄 *Trabajos Activos* - Ver trabajos con contador regresivo en vivo
📈 *Estado General* - Dashboard del sistema
🔔 *Recordatorios* - Gestionar notificaciones automáticas

💡 *Formato de registro:*
`/registrar "Nombre del trabajo" FECHA HORA PUNTOS MATERIA`

*¡Gestiona tu éxito académico profesionalmente!* 💪
    """
    
    bot.send_message(message.chat.id, menu, parse_mode='Markdown',
                    reply_markup=crear_teclado_gestion_academica())

def mostrar_comando_no_reconocido(message):
    """Manejar comandos no reconocidos"""
    respuesta = f"""
🤔 *No reconozco: "{message.text}"*

💡 *Usa los botones para navegar fácilmente:*

🎯 *Menú Principal* - Volver al inicio
📝 *Gestión Académica* - Sistema de trabajos
ℹ️ *Información* - Centro de información
🆘 *Ayuda* - Soporte y guías
🔄 *Trabajos Activos* - Contador regresivo en vivo
🔔 *Recordatorios* - Notificaciones automáticas

*¡La navegación por botones es más fácil!* 🚀
    """
    
    bot.send_message(message.chat.id, respuesta, parse_mode='Markdown',
                    reply_markup=crear_teclado_principal())

# ==================== FUNCIONES DE GESTIÓN ACADÉMICA ====================
def mostrar_formato_registro(message):
    """Mostrar formato de registro con ejemplos"""
    user_name = message.from_user.first_name
    
    formato = f"""
🆕 *REGISTRAR NUEVO TRABAJO - {user_name}*

*📝 FORMATO CORRECTO:*
`/registrar "NOMBRE" FECHA HORA PUNTOS MATERIA`

*🚀 EJEMPLOS PRÁCTICOS:*

*🎯 EJEMPLO SIMPLE:*
`/registrar "Ensayo Filosofía" 2024-11-05 23:59 25`

*📚 EJEMPLO CON MATERIA:*
`/registrar "Proyecto Matemáticas" 2024-11-10 14:00 30 Álgebra`

*💡 FORMATOS ACEPTADOS:*
• *Fecha:* 2024-11-05, 05/11/2024, 05-11-2024
• *Hora:* 23:59, 14:00, 09:30 (formato 24h)

*📋 PROCEDIMIENTO:*
1. *Copia* uno de los ejemplos
2. *Modifica* los datos según tu trabajo
3. *Pega* y envía el comando
4. *Ve a "Trabajos Activos" para ver el contador regresivo*

*🔔 RECORDATORIOS AUTOMÁTICOS:*
Recibirás notificaciones automáticas antes del vencimiento

*¡Selecciona, copia y modifica cualquier ejemplo!* 📝
    """
    
    bot.send_message(message.chat.id, formato, parse_mode='Markdown')

def mostrar_ejemplos_completos(message):
    """Mostrar ejemplos completos de registro"""
    ejemplos = """
📋 *EJEMPLOS COMPLETOS - LISTOS PARA USAR*

*🎯 FORMATO:*
`/registrar "NOMBRE" FECHA HORA PUNTOS MATERIA`

*🚀 EJEMPLOS PRÁCTICOS:*

1. *CIENCIAS EXACTAS:*
   `"/registrar "Proyecto: Leyes de Newton" 2024-11-05 23:59 30 Física"`
   `"/registrar "Análisis de Funciones" 2024-10-28 14:00 25 Cálculo"`

2. *HUMANIDADES:*
   `"/registrar "Ensayo sobre Ética Moderna" 2024-10-30 09:30 20 Filosofía"`
   `"/registrar "Análisis Literario" 2024-11-03 16:00 28 Literatura"`

3. *TRABAJOS GENERALES:*
   `"/registrar "Presentación Final" 2024-11-20 10:00 15"`
   `"/registrar "Proyecto de Investigación" 2024-11-25 17:30 45"`

*💡 REGISTRO MÚLTIPLE:*
*Puedes registrar varios trabajos enviando un mensaje por cada uno*

*🔔 RECORDATORIOS:*
*Recibirás notificaciones automáticas para cada trabajo registrado*

*¡Luego ve a "Trabajos Activos" para ver los contadores en tiempo real!* 📝
    """
    
    bot.send_message(message.chat.id, ejemplos, parse_mode='Markdown')

def mostrar_progreso_personal(message):
    """Mostrar progreso personal del usuario"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    trabajos_usuario = [t for t in trabajos if t['user_id'] == user_id]
    
    if trabajos_usuario:
        trabajos_activos = len([t for t in trabajos_usuario if t['estado'] == 'activo'])
        trabajos_completados = len([t for t in trabajos_usuario if t['estado'] == 'completado'])
        total_puntos = sum(t['puntos'] for t in trabajos_usuario)
        puntos_completados = sum(t['puntos'] for t in trabajos_usuario if t['estado'] == 'completado')
        recordatorios_recibidos = logger.usuarios_registrados.get(user_id, {}).get('recordatorios_recibidos', 0)
        
        progreso = f"""
📊 *PROGRESO ACADÉMICO - {user_name}*

📈 *RESUMEN GENERAL:*
• 📝 Total trabajos: *{len(trabajos_usuario)}*
• 🟢 Activos: *{trabajos_activos}*
• ✅ Completados: *{trabajos_completados}*
• 🎯 Tasa de éxito: *{(trabajos_completados/len(trabajos_usuario)*100):.1f}%*

🏆 *PUNTOS ACADÉMICOS:*
• 🎯 Total puntos: *{total_puntos}*
• ✅ Puntos ganados: *{puntos_completados}*
• 📊 Progreso: *{(puntos_completados/total_puntos*100) if total_puntos > 0 else 0:.1f}%*

🔔 *RECORDATORIOS:*
• Notificaciones recibidas: *{recordatorios_recibidos}*

🚀 *¡Sigue así! Tu progreso es impresionante.*
        """
        
        bot.send_message(message.chat.id, progreso, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 
            "📝 *AÚN NO TIENES TRABAJOS REGISTRADOS*\n\n💡 Usa 🆕 Nuevo Trabajo para comenzar!", 
            parse_mode='Markdown')

def mostrar_trabajos_completados(message):
    """Mostrar trabajos completados"""
    user_id = message.from_user.id
    trabajos_completados = [t for t in trabajos if t['estado'] == 'completado' and t['user_id'] == user_id]
    
    if trabajos_completados:
        resultado = "✅ *TUS TRABAJOS COMPLETADOS*\n\n"
        
        for trabajo in trabajos_completados[:10]:
            resultado += f"✅ *{trabajo['nombre']}*\n"
            resultado += f"   📅 {trabajo['fecha']} | 🎯 {trabajo['puntos']} pts\n"
            resultado += f"   📚 {trabajo.get('materia', 'General')}\n\n"
        
        resultado += f"📊 *Total completados: {len(trabajos_completados)}*"
        
        bot.send_message(message.chat.id, resultado, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 
            "📝 *AÚN NO HAS COMPLETADO NINGÚN TRABAJO*\n\n💡 ¡Completa tus primeros trabajos activos!", 
            parse_mode='Markdown')

def mostrar_estado_general(message):
    """Mostrar estado general del sistema"""
    total_trabajos = len(trabajos)
    trabajos_activos = len([t for t in trabajos if t['estado'] == 'activo'])
    trabajos_completados = len([t for t in trabajos if t['estado'] == 'completado'])
    total_usuarios = len(logger.usuarios_registrados)
    total_recordatorios = sum(u.get('recordatorios_recibidos', 0) for u in logger.usuarios_registrados.values())
    
    estado_general = f"""
📈 *ESTADO GENERAL DEL SISTEMA HGC*

👥 *COMUNIDAD ACADÉMICA:*
• 🎓 Estudiantes activos: *{total_usuarios}*
• 📝 Trabajos registrados: *{total_trabajos}*

📊 *ESTADÍSTICAS:*
• 🟢 En progreso: *{trabajos_activos}*
• ✅ Completados: *{trabajos_completados}*
• 📈 Tasa de éxito: *{(trabajos_completados/total_trabajos*100) if total_trabajos > 0 else 0:.1f}%*

🔔 *RECORDATORIOS:*
• Notificaciones enviadas: *{total_recordatorios}*
• Sistema activo y monitoreando

⏰ *CONTADOR REGRESIVO:*
• Sistema activo y actualizando en tiempo real
• Actualización automática cada 30 segundos
• Botones inline para control manual

🚀 *¡Sistema funcionando correctamente!*
    """
    
    bot.send_message(message.chat.id, estado_general, parse_mode='Markdown')

# ==================== COMANDOS DE INFORMACIÓN ====================
@bot.message_handler(commands=['info', 'about', 'acerca'])
def info_comando(message):
    """Centro de información completo sobre HGC"""
    user_name = message.from_user.first_name
    
    logger.log('command', f'Ejecutó /info', user_name)
    
    info_completa = """
🤖 *CENTRO DE INFORMACIÓN HGC*

## 🎯 **¿QUÉ ES ESTE BOT?**

HGC es tu *asistente académico inteligente* para organizar y gestionar todos tus trabajos de estudio en un solo lugar.

---

## 🚀 **FUNCIONALIDADES PRINCIPALES**

📝 *Registro de trabajos y proyectos*
⏰ *Contador regresivo en tiempo real*
🔔 *Sistema de recordatorios automáticos*
📊 *Seguimiento de progreso automático*  
👥 *Comunidad académica activa*
🎯 *Gestión de fechas y materias*
🔘 *Botones inline para control manual*

---

## 💡 **BENEFICIOS INMEDIATOS**

✅ Organización centralizada
✅ Contador regresivo automático
✅ Recordatorios inteligentes
✅ Control manual con botones
✅ Motivación con progreso visible
✅ Comunidad de apoyo académico
✅ Fácil uso en Telegram

---

## 🎯 **CÓMO COMENZAR**

`/registrar "Mi proyecto" 2024-11-05 23:59 25`

*Luego ve a "Trabajos Activos" para ver el contador en vivo*

*¡Transforma tu forma de estudiar!* 🚀

*¿Preguntas? Usa:* `/faq`
    """
    
    bot.reply_to(message, info_completa, parse_mode='Markdown')

@bot.message_handler(commands=['faq', 'preguntas', 'dudas'])
def faq_comando(message):
    """Centro de preguntas frecuentes"""
    user_name = message.from_user.first_name
    
    logger.log('command', f'Ejecutó /faq', user_name)
    
    faq_completo = """
❓ *CENTRO DE AYUDA - PREGUNTAS FRECUENTES*

### 🤔 **¿QUÉ ES HGC?**
HGC (Herramienta de Gestión Curricular) es un sistema inteligente de gestión académica diseñado para estudiantes, investigadores y grupos de estudio.

### 🎓 **¿PARA QUIÉN ES ESTE BOT?**
• Estudiantes universitarios
• Investigadores académicos
• Grupos de estudio colaborativo
• Profesores organizando proyectos

### 📝 **¿CÓMO REGISTRO UN TRABAJO?**
*Formato:* `/registrar "Nombre" FECHA HORA PUNTOS MATERIA`

*Ejemplos:*
`/registrar "Ensayo Filosofía" 2024-11-05 23:59 25`
`/registrar "Proyecto Matemáticas" 2024-11-10 14:00 30 Álgebra`

### ⏰ **¿CÓMO FUNCIONA EL CONTADOR REGRESIVO?**
• Se actualiza **automáticamente** cada 30 segundos
• Muestra tiempo exacto hasta la fecha límite
• Colores indican urgencia (🔴🟡🟢)
• **Botones inline debajo del mensaje** para control manual
• Funciona en tiempo real para todos los usuarios

### 🔔 **¿CÓMO FUNCIONAN LOS RECORDATORIOS?**
• **Recordatorios automáticos:** 24h, 12h, 3h, 1h, 30min antes
• **Resumen diario:** Resumen de trabajos pendientes
• **Configurable:** Puedes activar/desactivar y cambiar hora
• **Persistente:** Configuraciones se guardan entre reinicios

### 🔘 **¿QUÉ BOTONES INLINE HAY?**
• **🔄 Actualizar Ahora** - Refresca manualmente
• **📊 Ver Estadísticas** - Estadísticas detalladas
• **🔔 Recordatorios** - Gestión de notificaciones
• **⏰ Detalles Sistema** - Información del sistema

### 📊 **¿QUÉ INFORMACIÓN VEO EN MI PROGRESO?**
• Total de trabajos registrados
• Trabajos activos vs completados
• Puntos académicos totales
• Tasa de éxito y eficiencia
• Recordatorios recibidos
• Próximos vencimientos con contador

### 👥 **¿QUÉ ES LA COMUNIDAD ACADÉMICA?**
Puedes ver los trabajos activos de otros estudiantes para:
• Inspirarte en nuevos proyectos
• Coordinar tiempos de estudio
• Sentir parte de una comunidad
• Aprender de otros enfoques

### 🔐 **¿QUÉ SEGURIDAD TIENEN MIS DATOS?**
• Los datos se almacenan temporalmente en memoria
• Solo tú ves tus progresos detallados
• Información comunitaria es anónima
• Puedes reiniciar tu historial en cualquier momento

### 💰 **¿ES GRATUITO?**
¡Sí! HGC es completamente gratuito y sin planes de pago futuros.

### 🆘 **¿CÓMO OBTENGO AYUDA?**
• Usa `/ayuda` para soporte técnico
• Revisa ejemplos en `/registrar`
• Consulta el formato correcto de comandos

### 🚀 **¿QUÉ VIENE EN EL FUTURO?**
• Sistema de encuestas avanzado
• Recordatorios por WhatsApp/Email
• Colaboración en tiempo real
• Análisis de rendimiento detallado

---

*¿No encuentras tu respuesta? El sistema está diseñado para ser intuitivo. ¡Prueba y descubre!* 🎯
    """
    
    bot.reply_to(message, faq_completo, parse_mode='Markdown')

@bot.message_handler(commands=['ayuda'])
def ayuda_comando(message):
    user_name = message.from_user.first_name
    
    logger.log('command', f'Ejecutó /ayuda', user_name)
    
    respuesta = f"""
🆘 *CENTRO DE AYUDA HGC - {user_name}*

*🎯 CÓMO REGISTRAR TRABAJOS:*

📝 *FORMATO CORRECTO:*
`/registrar "Nombre del trabajo" FECHA HORA PUNTOS MATERIA`

🚀 *EJEMPLOS FUNCIONALES:*
`/registrar "Mi primer trabajo" 2024-10-30 23:59 20`
`/registrar "Proyecto Matemáticas" 2024-11-05 14:00 25 Álgebra`
`/registrar "Ensayo Filosofía" 30/10/2024 09:30 18`

💡 *CONSEJOS:*
• Usa comillas para nombres largos
• La fecha puede ser en varios formatos
• La hora en formato 24h (HH:MM)
• Los puntos deben ser números
• La materia es opcional

*⏰ CONTADOR REGRESIVO:*
• Ve a "Trabajos Activos" para ver el contador en vivo
• Se actualiza automáticamente cada 30 segundos
• **Busca los botones debajo del mensaje** para control manual
• Colores indican urgencia del trabajo

*🔔 RECORDATORIOS:*
• **Activa/Desactiva** en "🔔 Recordatorios"
• **Configura hora** con `/hora_recordatorio HH:MM`
• **Recibe alertas** automáticas antes del vencimiento
• **Resumen diario** de trabajos pendientes

*🔘 BOTONES INLINE:*
• **🔄 Actualizar Ahora** - Refresca manualmente
• **📊 Ver Estadísticas** - Estadísticas detalladas  
• **🔔 Recordatorios** - Gestión de notificaciones
• **⏰ Detalles Sistema** - Información del sistema

*📚 MÁS INFORMACIÓN:*
• `/info` - Conoce el sistema HGC
• `/faq` - Preguntas frecuentes
• `🔄 Trabajos Activos` - Ver contador regresivo en tiempo real
• `🔔 Recordatorios` - Gestionar notificaciones

*¡El sistema completo funciona al 100%!* ✅
    """
    
    bot.reply_to(message, respuesta, parse_mode='Markdown')

# ==================== COMANDO DEBUG PARA BOTONES ====================
@bot.message_handler(commands=['debug_botones'])
def debug_botones(message):
    """Comando para debug de botones inline"""
    user_name = message.from_user.first_name
    logger.log('command', f'Ejecutó /debug_botones', user_name)
    
    # Mensaje simple con botones
    mensaje = "🔄 *PRUEBA DE BOTONES INLINE* 🔘\n\n"
    mensaje += "Este es un mensaje de prueba para verificar que los botones inline funcionan correctamente.\n\n"
    mensaje += "• ✅ Si ves botones debajo → Sistema OK\n"
    mensaje += "• ❌ Si NO ves botones → Hay un problema\n\n"
    mensaje += "🕐 *Hora:* " + datetime.now().strftime('%H:%M:%S')
    
    # Crear botones inline de prueba
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔄 Botón 1 - Actualizar", callback_data="debug_actualizar"),
        InlineKeyboardButton("📊 Botón 2 - Stats", callback_data="debug_stats")
    )
    markup.row(
        InlineKeyboardButton("⏰ Botón 3 - Tiempo", callback_data="debug_tiempo"),
        InlineKeyboardButton("❌ Botón 4 - Cerrar", callback_data="debug_cerrar")
    )
    
    try:
        sent_message = bot.send_message(
            message.chat.id,
            mensaje,
            parse_mode='Markdown',
            reply_markup=markup
        )
        logger.log('system', f'✅ Mensaje debug enviado con ID: {sent_message.message_id}')
        bot.send_message(message.chat.id, "✅ *Mensaje de prueba enviado.* Revisa si ves los botones debajo.", parse_mode='Markdown')
    except Exception as e:
        logger.log('error', f'❌ Error en mensaje debug: {str(e)}')
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# ==================== SISTEMA DE MONITOREO CON PERSISTENCIA Y BACKUP ====================
def monitoreo_actividad():
    """Monitoreo que guarda datos periódicamente Y crea backups"""
    ultimo_backup = datetime.now()
    
    while True:
        time.sleep(300)  # 5 minutos
        
        # BACKUP CADA 6 HORAS (si está disponible)
        if BACKUP_DISPONIBLE:
            ahora = datetime.now()
            horas_desde_ultimo_backup = (ahora - ultimo_backup).total_seconds() / 3600
            
            if horas_desde_ultimo_backup >= 6:  # 6 horas
                print(f"🕐 Creando backup programado... ({horas_desde_ultimo_backup:.1f} horas desde último backup)")
                if sistema_backup.crear_backup_seguro():
                    ultimo_backup = ahora
                    print("✅ Backup programado completado")
                else:
                    logger.log('error', '❌ Falló backup programado')
        
        # Resto del monitoreo original (sin cambios)
        trabajos_actualizados = contador_regresivo.actualizar_estados_trabajos()
        if trabajos_actualizados > 0:
            guardar_datos()
        
        usuarios_activos = len(logger.usuarios_registrados)
        trabajos_activos = len([t for t in trabajos if t['estado'] == 'activo'])
        total_recordatorios = sum(u.get('recordatorios_recibidos', 0) for u in logger.usuarios_registrados.values())
        
        logger.log('system', f'📊 Monitoreo: {usuarios_activos} usuarios, {len(trabajos)} trabajos ({trabajos_activos} activos), {total_recordatorios} recordatorios')
        
        # Guardar datos cada 5 minutos
        guardar_datos()

# ==================== EJECUCIÓN PRINCIPAL DEL BOT ====================
def ejecutar_bot():
    """Función principal para ejecutar el bot"""
    print("=" * 60)
    print("🚀 BOT HGC INICIADO CORRECTAMENTE")
    print("🎓 Sistema de Gestión Académica")
    print("📱 Ve a Telegram y envía /start a tu bot")
    print("⏳ Esperando mensajes...")
    print("=" * 60)
    
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
        print("✅ Bot detenido normalmente")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Reiniciando en 10 segundos...")
        time.sleep(10)
        ejecutar_bot()  # Reinicio automático
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")

# ==================== INICIALIZACIÓN Y EJECUCIÓN ====================
if __name__ == "__main__":
    inicializar_sistema()
    thread_monitoreo = threading.Thread(target=monitoreo_actividad, daemon=True)
    thread_monitoreo.start()
    
    ejecutar_bot()