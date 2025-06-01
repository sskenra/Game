import tkinter as tk
import random

# Настройки окна
window_width = 800
window_height = 500

# Настройки объектов
plate_width = 150
plate_height = 30
object_size = 50
plate_speed = 50

# Счёт и жизни
score = 0
lives = 3
game_running = True
falling_objects = []

# Создаём окно
root = tk.Tk()
root.title("Простая игра")
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="lightblue")
canvas.pack()

# Тарелка
plate = canvas.create_rectangle(
    window_width // 2 - plate_width // 2,
    window_height - plate_height - 10,
    window_width // 2 + plate_width // 2,
    window_height - 10,
    fill="white"
)

# Движение тарелки
def move_plate(event):
    if not game_running:
        return
    if event.keysym == "Left":
        canvas.move(plate, -plate_speed, 0)
    elif event.keysym == "Right":
        canvas.move(plate, plate_speed, 0)

# Создание объектов
def spawn_object():
    if not game_running:
        return
    x = random.randint(0, window_width - object_size)
    object_type = random.choice(["good", "bad"])
    color = "blue" if object_type == "good" else "red"
    obj = canvas.create_rectangle(x, 0, x + object_size, object_size, fill=color)
    falling_objects.append({"id": obj, "type": object_type, "y": 0})
    root.after(1000, spawn_object)

# Проверка столкновений и обновление игры
def update_game():
    global score, lives, game_running

    if not game_running:
        return

    for obj in falling_objects[:]:
        canvas.move(obj["id"], 0, 5)
        obj["y"] += 5

        obj_coords = canvas.coords(obj["id"])
        plate_coords = canvas.coords(plate)

        # Столкновение
        if (plate_coords[0] < obj_coords[2] and plate_coords[2] > obj_coords[0] and
            plate_coords[1] < obj_coords[3] and plate_coords[3] > obj_coords[1]):
            if obj["type"] == "good":
                score += 1
            else:
                lives -= 1
            canvas.delete(obj["id"])
            falling_objects.remove(obj)

        # Упал вниз
        elif obj["y"] > window_height:
            if obj["type"] == "good":
                lives -= 1
            canvas.delete(obj["id"])
            falling_objects.remove(obj)

    if lives <= 0:
        game_running = False
    else:
        root.after(50, update_game)

# Отображение счёта и жизней
def draw_score():
    canvas.delete("score")
    canvas.create_text(10, 10, anchor="nw", text="Счёт: " + str(score), font=("Arial", 14), tags="score")
    canvas.create_text(10, 30, anchor="nw", text="Жизни: " + str(lives), font=("Arial", 14), tags="score")
    if game_running:
        root.after(100, draw_score)

# Управление
root.bind("<Left>", move_plate)
root.bind("<Right>", move_plate)

# Запуск игры
spawn_object()
update_game()
draw_score()

root.mainloop()
