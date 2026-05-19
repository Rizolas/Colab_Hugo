import speech_recognition as sr
import keyboard

def listar_dispositivos():
    dispositivos = sr.Microphone.list_microphone_names()
    for index, name in enumerate (dispositivos):
       print(f"{index}: {name}")

def SpeechToText(device_index=None):
  Ai = sr.Recognizer()
  with sr.Microphone (device_index=device_index) as source:
    print("Hablando... Presiona 'q' para salir.")
    listening = Ai.listen(source, phrase_time_limit=6)

    try:
        command = Ai.recognize_google(listening, language="es-ES")
        print("Has dicho: " + command)

        with open("transcripcion.txt", "a", encoding="utf-8") as file:
            file.write(command + "\n")
    except sr.UnknownValueError:
        print("No entendi lo que dijiste, intentémoslo de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error durante el reconocimiento: {e}")

print("Dispositivos disponibles:")
listar_dispositivos()

indice_mic = int(input("Elige el índice del micrófono que deseas usar: "))
while True:
  if keyboard.is_pressed('q'):
      print("Se presionó 'q'. Saliendo del programa...")
      break
  else:
      SpeechToText(device_index=indice_mic)