
import subprocess
import webbrowser
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
import requests
from bs4 import BeautifulSoup
import sys
import os

# Soporte local para reconocimiento de audio y conversión (independiente de asistente.py)
try:
    import speech_recognition as sr
except Exception:
    sr = None
import tempfile
import pathlib
try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None

# ── Configuración del motor de voz ──────────────────────────────────────────
if pyttsx3:
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
    except Exception:
        engine = None
else:
    engine = None

def hablar(texto):
    """Convierte texto a voz y lo imprime en consola."""
    print(f"[Asistente]: {texto}")
    if engine:
        try:
            engine.say(texto)
            engine.runAndWait()
        except Exception:
            pass

# ── Comandos del sistema ─────────────────────────────────────────────────────
def ejecutar_comando(cmd):
    """Lanza una aplicación del sistema según el SO."""
    if sys.platform == "win32":
        try:
            if os.path.exists(cmd):
                os.startfile(cmd)
            else:
                # Use the Windows 'start' command so applications identified by name are launched
                subprocess.Popen(['cmd', '/c', 'start', '', cmd])
        except Exception as e:
            hablar(f"No pude ejecutar {cmd}: {e}")
    elif sys.platform == "darwin":
        subprocess.Popen(["open", cmd])
    else:
        try:
            subprocess.Popen([cmd])
        except Exception as e:
            hablar(f"No pude ejecutar {cmd}: {e}")


COMANDOS = {
    "reproductor": lambda: ejecutar_comando("wmplayer") if sys.platform=="win32"
                           else ejecutar_comando("vlc"),
    "música":      lambda: ejecutar_comando("wmplayer") if sys.platform=="win32"
                           else ejecutar_comando("vlc"),
    "vlc":         lambda: ejecutar_comando("vlc"),

    # Aplicaciones de oficina
    "word":        lambda: ejecutar_comando("winword") if sys.platform=="win32"
                           else ejecutar_comando("soffice"),
    "excel":       lambda: ejecutar_comando("excel")  if sys.platform=="win32"
                           else ejecutar_comando("scalc"),
    "bloc":        lambda: ejecutar_comando("notepad") if sys.platform=="win32"
                           else ejecutar_comando("gedit"),
    # Alias común (usuario dijo "blog" en lugar de "bloc")
    "blog":        lambda: ejecutar_comando("notepad") if sys.platform=="win32"
                           else ejecutar_comando("gedit"),

    # Navegador
    "navegador":   lambda: webbrowser.open("https://www.google.com"),
    "chrome":      lambda: webbrowser.open("https://www.google.com"),
    "youtube":     lambda: webbrowser.open("https://www.youtube.com"),
    "gato":        lambda: webbrowser.open("https://www.youtube.com/watch?v=Z1UWsBJ5HgU"),

    # Sistema
    "apagar":      lambda: os.system("shutdown /s /t 5") if sys.platform=="win32"
                           else os.system("sudo shutdown -h now"),
    "reiniciar":   lambda: os.system("shutdown /r /t 5") if sys.platform=="win32"
                           else os.system("sudo reboot"),
    "salir":       lambda: sys.exit(hablar("¡Hasta luego!")),
}

# ── Procesar instrucción ─────────────────────────────────────────────────────
def procesar(instruccion):
    """Identifica la intención y ejecuta la acción correspondiente."""
    if not instruccion:
        return

    # Búsqueda web
    if "busca" in instruccion or "buscar" in instruccion or "qué es" in instruccion:
        # Extrae el término: todo lo que va después de la palabra clave
        for kw in ("busca ", "buscar ", "qué es ", "que es "):
            if kw in instruccion:
                termino = instruccion.split(kw, 1)[1]
                buscar_web(termino)
                return
        hablar("¿Qué quieres que busque?")
        return

    # Comandos directos
    for clave, accion in COMANDOS.items():
        if clave in instruccion:
            hablar(f"Ejecutando: {clave}")
            accion()
            return

    hablar("No reconocí ese comando. Intenta de nuevo.")


def buscar_web(consulta):
    """Abre el navegador y lee el primer párrafo de Wikipedia si está disponible."""
    url = f"https://www.google.com/search?q={consulta.replace(' ', '+')}"
    webbrowser.open(url)
    hablar(f"Buscando: {consulta}")

    try:
        wiki_url = f"https://es.wikipedia.org/wiki/{consulta.replace(' ', '_')}"
        resp = requests.get(wiki_url, timeout=5,
                            headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        parrafos = soup.find_all("p")
        for p in parrafos:
            texto = p.get_text().strip()
            if len(texto) > 60:
                hablar("Encontré esto en Wikipedia:")
                hablar(texto[:300])
                return
    except Exception:
        pass
    hablar("No pude leer un resumen automático. Revisa el navegador.")


def reconocer_desde_wav(ruta):
    """Reconoce texto desde un archivo WAV (o lo convierte) y devuelve la cadena en minúsculas."""
    if not sr:
        hablar("El paquete 'SpeechRecognition' no está disponible. Instala 'pip install SpeechRecognition'.")
        return ""
    if not os.path.exists(ruta):
        hablar("Archivo de audio no encontrado.")
        return ""
    # Asegurarse de que la ruta apunta a un archivo (no a un directorio)
    if not os.path.isfile(ruta):
        hablar("La ruta indicada no es un archivo válido. Proporciona la ruta completa al archivo de audio (ej: C:\\ruta\\archivo.wav).")
        return ""
    ext = pathlib.Path(ruta).suffix.lower()
    temp_wav = None
    source_path = ruta
    if ext not in (".wav",):
        if AudioSegment is None:
            hablar("Formato de audio no WAV detectado pero 'pydub' no está instalado. Instala 'pydub' y ffmpeg para soporte adicional.")
            return ""
        try:
            audio_seg = AudioSegment.from_file(ruta)
            fd, temp_wav = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            audio_seg.export(temp_wav, format='wav')
            source_path = temp_wav
        except PermissionError as e:
            hablar(f"Permiso denegado al acceder al archivo: {e}")
            return ""
        except Exception as e:
            hablar(f"Error convirtiendo audio: {e}")
            return ""

    r = sr.Recognizer()
    try:
        with sr.AudioFile(source_path) as source:
            audio = r.record(source)
        texto = r.recognize_google(audio, language="es-ES")
        print(f"[Tú (audio)]: {texto}")
        return texto.lower()
    except sr.UnknownValueError:
        hablar("No entendí el audio.")
        return ""
    except sr.RequestError:
        hablar("Error de conexión con el servicio de reconocimiento.")
        return ""
    except Exception as e:
        hablar(f"Error al procesar WAV: {e}")
        return ""
    finally:
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass


def escuchar():
    """Escucha desde el micrófono y devuelve el texto reconocido."""
    if not sr:
        hablar("El paquete 'SpeechRecognition' no está disponible. Instala 'pip install SpeechRecognition'.")
        return ""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as fuente:
            hablar("Escuchando... habla ahora.")
            r.adjust_for_ambient_noise(fuente, duration=0.5)
            audio = r.listen(fuente, timeout=5, phrase_time_limit=8)
        try:
            texto = r.recognize_google(audio, language="es-ES")
            print(f"[Tú (micrófono)]: {texto}")
            return texto.lower()
        except sr.UnknownValueError:
            hablar("No entendí. Repite por favor.")
            return ""
        except sr.RequestError:
            hablar("Sin conexión al servicio de reconocimiento.")
            return ""
    except Exception as e:
        hablar(f"Error accediendo al micrófono: {e}")
        return ""

# ── Bucle principal ──────────────────────────────────────────────────────────
def main():
    hablar("Hola, soy tu asistente virtual. Elige modo de interacción:")
    while True:
        print("\n1) Texto  2) WAV  3) Audio en tiempo real  4) Salir")
        opcion = input("Selecciona una opción (1/2/3/4): ").strip()
        if opcion == '1':
            hablar("Modo texto activado. Escribe 'salir' para volver al menú.")
            while True:
                instruccion = input("\nEscribe tu instrucción: ").lower().strip()
                if instruccion == 'salir':
                    hablar("Volviendo al menú principal.")
                    break
                procesar(instruccion)
        elif opcion == '2':
            if reconocer_desde_wav is None:
                hablar("La función de transcripción desde WAV no está disponible. Asegúrate de tener `asistente.py` y dependencias.")
                continue
            ruta = input("Ruta al archivo WAV: ").strip().strip('"')
            if not ruta:
                hablar("Ruta vacía.")
                continue
            texto = reconocer_desde_wav(ruta)
            if texto:
                hablar(f"Transcripción: {texto}")
                procesar(texto)
        elif opcion == '3':
            if escuchar is None:
                hablar("La función de escucha en micrófono no está disponible. Asegúrate de tener `asistente.py` y dependencias.")
                continue
            hablar("Modo audio en tiempo real activado. Di 'salir' para volver al menú.")
            while True:
                texto = escuchar()
                if not texto:
                    continue
                if 'salir' in texto:
                    hablar('Saliendo del modo en tiempo real.')
                    break
                procesar(texto)
        elif opcion == '4':
            hablar('¡Hasta luego!')
            break
        else:
            hablar('Opción no válida.')

if __name__ == "__main__":
    main()
