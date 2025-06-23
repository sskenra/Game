import tkinter as tk
import random
import os
import shutil
import threading
from PIL import Image, ImageTk
from playsound import playsound

# Создание основного окна
root = tk.Tk()
root.title("Ну, погоди!")
root.geometry("800x600")
root.resizable(False, False)

# Пути к папкам с ресурсами
DIR = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(DIR, "Images")
SND = os.path.join(DIR, "Sounds")
TMP = os.path.join("C:\\TempGameAssets")
os.makedirs(TMP, exist_ok=True)

# Подготовка безопасного пути к музыке
SAFE_MUSIC_PATH = os.path.join(TMP, "music.wav")
SOURCE_MUSIC_PATH = os.path.join(SND, "Pixelated Dreams.wav")

# Копирование музыки в безопасное место (если нужно)
if not os.path.exists(SAFE_MUSIC_PATH):
    try:
        shutil.copy2(SOURCE_MUSIC_PATH, SAFE_MUSIC_PATH)
    except Exception as e:
        print("Ошибка копирования музыки:", e)

# Загружает и масштабирует изображение
def img(name, w, h):
    return ImageTk.PhotoImage(Image.open(os.path.join(IMG, name)).resize((w, h)))

# Загрузка изображений
bg = img("background.png", 800, 600)
btn_start = img("Start1.png", 300, 120)
btn_exit = img("Exit1.png", 300, 120)
apple_img = img("apple.png", 50, 50)
burger_img = img("Burger2.png", 120, 80)
plate_img = img("Tarelka.png", 150, 50)

# Создание холста
canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
canvas.pack()

# Глобальные переменные
score = 0
lives = 3
running = False
paused = False
objs = []
game_running = True
music_thread = None

# Воспроизводит музыку в цикле, пока игра активна
def play_music_loop():
    while game_running:
        try:
            playsound(SAFE_MUSIC_PATH)
        except:
            break

# Запускает фоновый поток с музыкой
def start_music():
    global music_thread
    if music_thread and music_thread.is_alive():
        return
    music_thread = threading.Thread(target=play_music_loop, daemon=True)
    music_thread.start()

# Останавливает воспроизведение музыки
def stop_music():
    global game_running
    game_running = False

# Отображает главное меню с кнопками "Старт" и "Выход"
def main_menu():
    canvas.delete("all")
    root.config(cursor="")
    canvas.create_image(0, 0, image=bg, anchor="nw")
    canvas.create_text(400, 200, text="Ну, погоди!", font=("Arial", 48), fill="black")
    s = canvas.create_image(400, 370, image=btn_start)
    e = canvas.create_image(400, 450, image=btn_exit)
    canvas.tag_bind(s, "<Button-1>", lambda e: start_game())
    canvas.tag_bind(e, "<Button-1>", lambda e: (stop_music(), root.quit()))

# Запускает обратный отсчет перед началом игры
def start_countdown(callback=None):
    countdown_label = canvas.create_text(400, 300, text="3", font=("Arial", 48), fill="black", 
    tag="countdown")
    def countdown(n):
        if n > 0:
            canvas.itemconfig(countdown_label, text=str(n))
            root.after(1000, countdown, n - 1)
        else:
            canvas.delete("countdown")
            if callback:
                callback()
    countdown(3)

# Подготавливает и запускает игровую сессию
def start_game():
    global score, lives, running, paused, objs, game_running
    canvas.delete("all")
    root.config(cursor="none")
    canvas.create_image(0, 0, image=bg, anchor="nw")
    canvas.create_text(70, 30, text="Очки: 0", font=("Arial", 18), fill="black", tag="score")
    canvas.create_text(730, 30, text="Жизни: 3", font=("Arial", 18), fill="black", tag="lives")
    canvas.create_image(400, 550, image=plate_img, tag="plate")
    objs.clear()
    score = 0
    lives = 3
    running = True
    paused = False
    game_running = True
    start_music()
    start_countdown(lambda: (update(), spawn()))

# Основной игровой цикл: движение объектов, проверка столкновений, обновление счета
def update():
    if not running or paused: return
    speed = 5 + score // 1
    for o in objs[:]:
        canvas.move(o["id"], 0, speed)
        o["y"] += speed
        ox, oy = canvas.coords(o["id"])
        px, py = canvas.coords("plate")
        if abs(ox - px) < 75 and abs(oy - py) < 30:
            add_score(o)
        elif o["y"] > 600:
            if o["type"] == "apple":
                lose_life()
            canvas.delete(o["id"])
            objs.remove(o)
    canvas.itemconfig("score", text=f"Очки: {score}")
    canvas.itemconfig("lives", text=f"Жизни: {lives}")
    if lives > 0:
        root.after(50, update)
    else:
        game_over()

# Появление нового объекта (яблоко или бургер) на экране
def spawn():
    if not running or paused: return
    x = random.randint(25, 775)
    kind = random.choice(["apple", "burger"])
    img = apple_img if kind == "apple" else burger_img
    obj = canvas.create_image(x, 0, image=img)
    objs.append({"id": obj, "type": kind, "y": 0})
    root.after(800, spawn)

# Обрабатывает пойманный объект: добавляет очко или отнимает жизнь
def add_score(obj):
    global score, lives
    if obj["type"] == "apple":
        score += 1
    else:
        lives -= 1
    canvas.delete(obj["id"])
    objs.remove(obj)

# Отнимает одну жизнь при пропущенном яблоке
def lose_life():
    global lives
    lives -= 1

# Завершает игру и отображает сообщение "Игра окончена"
def game_over():
    global running
    running = False
    canvas.create_text(400, 200, text="Игра окончена", font=("Arial", 36), fill="black")

# Перемещает тарелку влево/вправо по движению мыши
def move_plate(e):
    if running and not paused:
        canvas.coords("plate", e.x, 550)

# Включает/выключает паузу по нажатию Alt
def toggle_pause(e=None):
    global paused
    if running:
        paused = not paused
        if not paused:
            update()
            spawn()

# Привязка событий клавиатуры и мыши
root.bind("<Motion>", move_plate)
root.bind("r", lambda e: start_game())
root.bind("<Alt_L>", toggle_pause)
root.bind_all("<Alt_L>", lambda e: "break")

# Запуск главного меню и основной петли интерфейса
main_menu()
root.mainloop()
