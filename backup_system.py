# backup_system.py
import os
import json
import shutil
from datetime import datetime
import logging

class SistemaBackup:
    def __init__(self, ruta_datos_func):
        """
        Inicializar sistema de backup
        
        Args:
            ruta_datos_func: Función que retorna la ruta de datos
        """
        self.obtener_ruta_datos = ruta_datos_func
        self.logger = self._configurar_logger()
    
    def _configurar_logger(self):
        """Configurar logger para el sistema de backup"""
        logger = logging.getLogger('backup_system')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def crear_backup_seguro(self):
        """Crear backup sin sobreescribir datos existentes"""
        try:
            datos_dir = self.obtener_ruta_datos()
            backup_dir = os.path.join(datos_dir, "backups")
            
            self.logger.info(f"🔍 Iniciando backup en: {backup_dir}")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                self.logger.info(f"✅ Carpeta de backups creada: {backup_dir}")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backups_creados = 0
            
            # Archivos a respaldar
            archivos_datos = ['trabajos.json', 'usuarios.json', 'recordatorios.json', 'encuestas.json']
            
            for archivo in archivos_datos:
                archivo_origen = os.path.join(datos_dir, archivo)
                
                # Verificar que el archivo existe y tiene contenido
                if os.path.exists(archivo_origen) and os.path.getsize(archivo_origen) > 10:
                    archivo_backup = os.path.join(backup_dir, f"{archivo}.{timestamp}.bak")
                    
                    if self._crear_backup_individual(archivo_origen, archivo_backup):
                        backups_creados += 1
                    else:
                        self.logger.error(f"❌ Falló backup de: {archivo}")
                else:
                    self.logger.warning(f"⚠️ Archivo no existe o está vacío: {archivo}")
            
            # Limpiar backups antiguos
            self._limpiar_backups_antiguos(backup_dir)
            
            if backups_creados > 0:
                self.logger.info(f'📦 Backup completado: {timestamp} ({backups_creados} archivos)')
                return True
            else:
                self.logger.warning('⚠️ No se crearon backups - archivos vacíos o no existen')
                return False
            
        except Exception as e:
            self.logger.error(f'❌ Error crítico en backup: {str(e)}')
            return False
    
    def _crear_backup_individual(self, archivo_origen, archivo_backup):
        """Crear backup de un archivo individual con validación"""
        try:
            # Crear copia
            shutil.copy2(archivo_origen, archivo_backup)
            
            # Validar que el backup es legible y JSON válido
            if archivo_origen.endswith('.json'):
                with open(archivo_backup, 'r', encoding='utf-8') as f:
                    json.load(f)  # Validar que es JSON válido
            
            self.logger.info(f"✅ Backup válido: {os.path.basename(archivo_backup)}")
            return True
            
        except json.JSONDecodeError:
            self.logger.error(f"❌ Backup JSON corrupto: {archivo_backup}")
            if os.path.exists(archivo_backup):
                os.remove(archivo_backup)
            return False
        except Exception as e:
            self.logger.error(f"❌ Error en backup individual: {archivo_backup} - {e}")
            if os.path.exists(archivo_backup):
                os.remove(archivo_backup)
            return False
    
    def _limpiar_backups_antiguos(self, backup_dir, max_backups=10):
        """Mantener solo los backups más recientes"""
        try:
            if not os.path.exists(backup_dir):
                return
            
            # Agrupar backups por archivo base
            backups_por_archivo = {}
            
            for archivo in os.listdir(backup_dir):
                if archivo.endswith('.bak'):
                    partes = archivo.rsplit('.', 2)
                    if len(partes) == 3:
                        base = partes[0]
                        if base not in backups_por_archivo:
                            backups_por_archivo[base] = []
                        backups_por_archivo[base].append(archivo)
            
            # Mantener solo los más recientes por cada archivo base
            for base, archivos in backups_por_archivo.items():
                if len(archivos) > max_backups:
                    archivos_ordenados = sorted(archivos, reverse=True)
                    
                    for archivo_antiguo in archivos_ordenados[max_backups:]:
                        ruta_completa = os.path.join(backup_dir, archivo_antiguo)
                        os.remove(ruta_completa)
                        self.logger.info(f"🗑️ Backup antiguo eliminado: {archivo_antiguo}")
            
            self.logger.info("✅ Limpieza de backups antiguos completada")
                    
        except Exception as e:
            self.logger.error(f'Error limpiando backups: {str(e)}')
    
    def listar_backups(self):
        """Listar todos los backups disponibles"""
        try:
            backup_dir = os.path.join(self.obtener_ruta_datos(), "backups")
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            for archivo in os.listdir(backup_dir):
                if archivo.endswith('.bak'):
                    ruta_completa = os.path.join(backup_dir, archivo)
                    stats = os.stat(ruta_completa)
                    backups.append({
                        'nombre': archivo,
                        'ruta': ruta_completa,
                        'tamaño': stats.st_size,
                        'fecha_creacion': datetime.fromtimestamp(stats.st_ctime)
                    })
            
            return sorted(backups, key=lambda x: x['fecha_creacion'], reverse=True)
            
        except Exception as e:
            self.logger.error(f'Error listando backups: {str(e)}')
            return []
    
    def restaurar_backup(self, nombre_backup):
        """Restaurar un backup específico"""
        try:
            datos_dir = self.obtener_ruta_datos()
            backup_dir = os.path.join(datos_dir, "backups")
            archivo_backup = os.path.join(backup_dir, nombre_backup)
            
            if not os.path.exists(archivo_backup):
                self.logger.error(f"❌ Backup no encontrado: {nombre_backup}")
                return False
            
            # Extraer nombre del archivo original: trabajos.json.20241201120000.bak → trabajos.json
            archivo_original = nombre_backup.rsplit('.', 2)[0] + '.json'
            ruta_original = os.path.join(datos_dir, archivo_original)
            
            # Crear backup del archivo actual antes de restaurar
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_actual = os.path.join(backup_dir, f"{archivo_original}.PRE_RESTORE.{timestamp}.bak")
            
            if os.path.exists(ruta_original):
                shutil.copy2(ruta_original, backup_actual)
                self.logger.info(f"📦 Backup pre-restauración creado: {backup_actual}")
            
            # Restaurar el backup
            shutil.copy2(archivo_backup, ruta_original)
            
            # Validar que el archivo restaurado es válido
            if ruta_original.endswith('.json'):
                with open(ruta_original, 'r', encoding='utf-8') as f:
                    json.load(f)
            
            self.logger.info(f"✅ Backup restaurado exitosamente: {nombre_backup} → {archivo_original}")
            return True
            
        except Exception as e:
            self.logger.error(f'❌ Error restaurando backup: {str(e)}')
            return False

# Función de conveniencia para uso rápido
def crear_backup_rapido(ruta_datos_func):
    """Función simple para crear backup rápido"""
    backup_system = SistemaBackup(ruta_datos_func)
    return backup_system.crear_backup_seguro()