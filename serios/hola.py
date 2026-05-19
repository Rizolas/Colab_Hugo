import speech_recognition as sr

filename = "audio.wav"
output_file = "output.txt"

r = sr.Recognizer()

try:
    with sr.AudioFile(filename) as source:
        duration = int(source.DURATION)
        full_transcripcion = ""
        print("Procesando el archivo de audio...")
        for i in range(0, duration,10):
            try:
                audio_data = r.record(source, duration=10)
                text = r.recognize_google(audio_data, language='es-ES')
                full_transcripcion += text + "\n"
                print(f"Fragmento {i // 10 + 1}: {text}")
            except sr.UnknownValueError:
                print(f"Fragmento {i // 10 + 1}: No se pudo reconocer el audio")
                full_transcripcion += "[No se pudo reconocer el audio]\n"
            except sr.RequestError as e:
                print(f"Error al comunicarse con el servicio de Google: {e}")
                break
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_transcripcion)
        print(f"Transcripción guardada en {output_file}")

except FileNotFoundError:
    print(f"El archivo {filename} no fue encontrado.")

except ValueError as e:
    print(f"Error con el archivo de audio: {e}")

except Exception as e:
    print(f"Ocurrió un error: {e}")