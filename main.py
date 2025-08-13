from fastapi import FastAPI
from datetime import datetime
import os
import threading
import uvicorn
import pygame

MAX_THREADS = 10
lock = threading.Lock()
active_threads = []
active_event = threading.Event()

def play_sound(path_to_sound: str, stop_event: threading.Event):
    full_path = os.path.join(os.getcwd(), path_to_sound)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Sound file not found: {full_path}")

    pygame.mixer.init()
    pygame.mixer.music.load(full_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy() and stop_event.is_set():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome! Use /play to play a sound, /stop to stop all and play stop sound."}

@app.get("/play")
def play_endpoint():
    with lock:
        if len(active_threads) >= MAX_THREADS:
            return {"error": "Maximum number of concurrent sounds reached"}
        active_event.set()
        thread = threading.Thread(target=play_sound, args=("./assets/sounds/nya.mp3", active_event))
        active_threads.append(thread)
        thread.start()

    return {
        "message": "Sound is being played in the background",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stop")
def stop_endpoint():
    active_event.clear()

    for thread in active_threads:
        thread.join()


    active_threads.clear()

    stop_thread = threading.Thread(target=play_sound, args=("./assets/sounds/stop.mp3", threading.Event()))
    stop_thread.start()

    return {
        "message": "All sounds stopped, stop sound played",
        "timestamp": datetime.now().isoformat()
    }

def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
