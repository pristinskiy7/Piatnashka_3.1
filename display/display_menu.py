# display/display_menu.py


import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import random

from players.manager import (
    get_current_player_name, save_current_player,
    get_all_player_names, add_new_player, delete_player
)
from players.team_manager import get_team_name, save_team_name
from players.cloud_sync import sync_data


def open_leaderboard():
    """Открывает окно рейтинга с двумя вкладками: Команды и Топ-50 Игроков."""
    wait_win = tk.Toplevel()
    wait_win.title("Загрузка...")
    wait_win.geometry("250x100")
    tk.Label(wait_win, text="Получаем данные рейтинга...", pady=20).pack()
    wait_win.update()

    result = sync_data()
    wait_win.destroy()

    if not result:
        messagebox.showerror("Ошибка", "Облако временно недоступно.")
        return

    rank_win = tk.Toplevel()
    rank_win.title("🏆 Глобальный рейтинг")
    rank_win.geometry("650x500")

    # Создаем вкладки
    notebook = ttk.Notebook(rank_win)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    # --- ВКЛАДКА 1: КОМАНДЫ ---
    frame_teams = tk.Frame(notebook)
    notebook.add(frame_teams, text=" 👥 Топ-10 Команд ")

    cols_t = ("Rank", "Team", "Total_XP", "Size")
    tree_t = ttk.Treeview(frame_teams, columns=cols_t, show='headings')
    tree_t.heading("Rank", text="№");
    tree_t.column("Rank", width=40, anchor="center")
    tree_t.heading("Team", text="Команда");
    tree_t.column("Team", width=250)
    tree_t.heading("Total_XP", text="Суммарный XP");
    tree_t.column("Total_XP", width=120, anchor="center")
    tree_t.heading("Size", text="Участников");
    tree_t.column("Size", width=100, anchor="center")

    for i, team in enumerate(result["teams"], 1):
        tree_t.insert("", "end",
                      values=(i, team.get("team_name"), int(team.get("total_xp", 0)), team.get("players_count")))
    tree_t.pack(expand=True, fill="both", padx=5, pady=5)

    # --- ВКЛАДКА 2: ИГРОКИ (ТОП-50) ---
    frame_players = tk.Frame(notebook)
    notebook.add(frame_players, text=" 🎖️ Топ-50 Мастеров (Best XP) ")

    cols_p = ("Rank", "Player", "Best_XP", "Board", "Team")
    tree_p = ttk.Treeview(frame_players, columns=cols_p, show='headings')
    tree_p.heading("Rank", text="№");
    tree_p.column("Rank", width=30, anchor="center")
    tree_p.heading("Player", text="Игрок");
    tree_p.column("Player", width=150)
    tree_p.heading("Best_XP", text="Рекорд XP");
    tree_p.column("Best_XP", width=90, anchor="center")
    tree_p.heading("Board", text="Поле");
    tree_p.column("Board", width=70, anchor="center")
    tree_p.heading("Team", text="Команда");
    tree_p.column("Team", width=150)

    for i, p in enumerate(result["players"], 1):
        tree_p.insert("", "end",
                      values=(i, p.get("player_name"), int(p.get("best_xp", 0)), p.get("board"), p.get("team_name")))

    # Добавляем полосу прокрутки для топ-50
    scrollbar = ttk.Scrollbar(frame_players, orient="vertical", command=tree_p.yview)
    tree_p.configure(yscrollcommand=scrollbar.set)
    tree_p.pack(side="left", expand=True, fill="both", padx=(5, 0), pady=5)
    scrollbar.pack(side="right", fill="y", pady=5)

    tk.Button(rank_win, text="Закрыть", command=rank_win.destroy, bg="#d1e7ff").pack(pady=10)

def show_menu():
    root = tk.Tk()
    root.title("Пятнашки 2026 - Управление")
    root.geometry("450x700")  # Увеличил высоту для ползунков

    def refresh():
        root.destroy()
        show_menu()

    t_name = get_team_name()

    # --- СЦЕНА 1: ЕСЛИ НЕТ КОМАНДЫ ---
    if not t_name:
        tk.Label(root, text="СОЗДАНИЕ НОВОЙ КОМАНДЫ", font=("Arial", 12, "bold")).pack(pady=20)
        e = tk.Entry(root, font=("Arial", 12))
        e.pack(pady=10)

        def create_t():
            name = e.get().strip()
            if name:
                save_team_name(name)
                refresh()
            else:
                messagebox.showwarning("!", "Введите название команды")

        tk.Button(root, text="Создать команду", command=create_t, bg="lightgreen", font=("Arial", 10, "bold")).pack(
            pady=10)

    # --- СЦЕНА 2: ГЛАВНОЕ МЕНЮ ---
    else:
        tk.Label(root, text=f"Команда: {t_name}", font=("Arial", 14, "bold"), fg="blue").pack(pady=10)

        curr_p = get_current_player_name()
        tk.Label(root, text=f"Текущий игрок: {curr_p or '---'}", font=("Arial", 11, "italic")).pack()

        # --- БЛОК НАСТРОЙКИ ПОЛЯ ---
        size_frame = tk.LabelFrame(root, text=" Размер поля (от 4 до 10) ", padx=10, pady=10)
        size_frame.pack(pady=15, fill="x", padx=40)

        tk.Label(size_frame, text="Ширина:").grid(row=0, column=0)
        w_scale = tk.Scale(size_frame, from_=4, to=10, orient="horizontal")
        w_scale.set(4)
        w_scale.grid(row=0, column=1, sticky="we")

        tk.Label(size_frame, text="Высота:").grid(row=1, column=0)
        h_scale = tk.Scale(size_frame, from_=4, to=10, orient="horizontal")
        h_scale.set(4)
        h_scale.grid(row=1, column=1, sticky="we")
        size_frame.columnconfigure(1, weight=1)

        rand_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Случайный размер при старте", variable=rand_var).pack()

        # Кнопка ИГРАТЬ
        def start_game():
            if not curr_p:
                messagebox.showwarning("!", "Сначала добавьте игрока!")
                return

            if rand_var.get():
                w, h = random.randint(4, 10), random.randint(4, 10)
            else:
                w, h = w_scale.get(), h_scale.get()

            from game.game_loop import start_game_loop
            root.withdraw()
            start_game_loop(root, curr_p, w, h)

        tk.Button(root, text="🎮 В БОЙ!", command=start_game, bg="#c8e6c9",
                  font=("Arial", 14, "bold"), height=2).pack(pady=10, fill='x', padx=50)

        # --- УПРАВЛЕНИЕ ИГРОКАМИ ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        def add_p():
            name = simpledialog.askstring("Новый игрок", "Введите имя игрока:")
            if name and name.strip():
                if add_new_player(name.strip()):
                    refresh()
                else:
                    messagebox.showerror("Ошибка", "Имя занято")

        def del_p():
            if not curr_p: return
            if messagebox.askyesno("Удаление", f"Удалить игрока {curr_p}?\n(Если он последний, команда удалится)"):
                delete_player(curr_p)
                refresh()

        tk.Button(btn_frame, text="➕ Добавить", command=add_p, bg="#e3f2fd", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ Удалить", command=del_p, bg="#ffebee", width=12).pack(side="left", padx=5)

        all_p = get_all_player_names()
        if all_p:
            tk.Label(root, text="Сменить игрока:").pack(pady=(5, 0))
            p_var = tk.StringVar(root)
            p_var.set(curr_p)
            om = tk.OptionMenu(root, p_var, *all_p, command=lambda v: [save_current_player(v), refresh()])
            om.pack(pady=5)

        # Кнопка РЕЙТИНГА
        tk.Button(root, text="🌐 ГЛОБАЛЬНЫЙ РЕЙТИНГ", command=open_leaderboard,
                  bg="#bbdefb", font=("Arial", 10, "bold")).pack(pady=20, fill='x', padx=50)

    tk.Button(root, text="Выход из программы", command=root.quit, fg="red").pack(side="bottom", pady=20)

    # Центрирование
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()