import json
import os
import random
import smtplib
import time
import tkinter as tk
from email.message import EmailMessage
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(ROOT_DIR, "accounts_data.json")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
CACTUS_ASSETS_DIR = os.path.join(ASSETS_DIR, "cactus")

BASE_WIDTH = 1280
BASE_HEIGHT = 720
GRAVITY = 0.6
JUMP_FORCE = -11
SPAWN_MIN = 900
SPAWN_MAX = 1700
FRAME_MS = 20
BIRD_SCORE_THRESHOLD = 500
COIN_SPAWN_MIN = 1200
COIN_SPAWN_MAX = 2200
COIN_SPAWN_CHANCE = 0.9
BG_COLOR = "#111827"
SKY_SWITCH_POINTS = 750


class DinoRunner:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Modern Dinosaur Game")
        self.root.configure(bg="#0f172a")
        self.root.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")
        self.data_file = Path(__file__).with_name("accounts_data.json")
        self.accounts = self.load_accounts()
        self.current_user = ""

        self.score_var = tk.StringVar(value="Puntaje: 0")
        self.best_var = tk.StringVar(value="Récord: 0")
        self.emilianos_var = tk.StringVar(value="Emilianos: 0")

        self.best_score = 0
        self.emilianos = 0
        self.running = True
        self.game_width = BASE_WIDTH - 32
        self.game_height = BASE_HEIGHT - 120
        self.ground_y = self.game_height - 170
        self.cactus_images = self.load_cactus_images()

        hud = tk.Frame(root, bg="#0f172a")
        hud.pack(fill="x", padx=16, pady=(14, 6))
        self.title_label = tk.Label(hud, text="Modern Dinosaur Game", fg="#e2e8f0", bg="#0f172a", font=("Segoe UI", 18, "bold"))
        self.title_label.pack(side="left")

        stats = tk.Frame(hud, bg="#0f172a")
        stats.pack(side="right")
        self.emilianos_label = tk.Label(stats, textvariable=self.emilianos_var, fg="#fbbf24", bg="#0f172a", font=("Segoe UI", 18, "bold"))
        self.emilianos_label.pack(side="left", padx=10)
        self.score_label = tk.Label(stats, textvariable=self.score_var, fg="#67e8f9", bg="#0f172a", font=("Segoe UI", 18, "bold"))
        self.score_label.pack(side="left", padx=10)

        self.record_box = tk.Frame(stats, bg="#0f172a")
        self.record_box.pack(side="left", padx=10)
        self.best_label = tk.Label(self.record_box, textvariable=self.best_var, fg="#a5b4fc", bg="#0f172a", font=("Segoe UI", 18, "bold"))
        self.best_label.pack(anchor="e")

        self.canvas = tk.Canvas(root, width=BASE_WIDTH - 32, height=BASE_HEIGHT - 120, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.help_label = tk.Label(
            root,
            text="Espacio / ↑: saltar · ↓: agacharse · R: pausar juego",
            fg="#cbd5e1",
            bg="#0f172a",
            font=("Segoe UI", 14, "bold"),
        )
        self.help_label.pack(pady=(0, 14))

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.login_status_var = tk.StringVar(value="")
        self.recover_email_var = tk.StringVar()
        self.recover_code_var = tk.StringVar()
        self.recover_new_pass_var = tk.StringVar()
        self.recover_confirm_pass_var = tk.StringVar()
        self.recover_status_var = tk.StringVar(value="")
        self.register_user_var = tk.StringVar()
        self.register_email_var = tk.StringVar()
        self.register_pass_var = tk.StringVar()
        self.register_confirm_var = tk.StringVar()
        self.register_status_var = tk.StringVar(value="")
        self.recovery_code = ""
        self.recovery_verified_email = ""
        self.login_entry = tk.Entry(root, textvariable=self.login_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a")
        self.password_entry = tk.Entry(root, textvariable=self.password_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a", show="•")
        self.recover_email_entry = tk.Entry(root, textvariable=self.recover_email_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a")
        self.recover_code_entry = tk.Entry(root, textvariable=self.recover_code_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a")
        self.recover_new_pass_entry = tk.Entry(root, textvariable=self.recover_new_pass_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a", show="•")
        self.recover_confirm_pass_entry = tk.Entry(root, textvariable=self.recover_confirm_pass_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a", show="•")
        self.register_user_entry = tk.Entry(root, textvariable=self.register_user_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a")
        self.register_email_entry = tk.Entry(root, textvariable=self.register_email_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a")
        self.register_pass_entry = tk.Entry(root, textvariable=self.register_pass_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a", show="•")
        self.register_confirm_entry = tk.Entry(root, textvariable=self.register_confirm_var, font=("Segoe UI", 18, "bold"), justify="center", bg="#e2e8f0", fg="#0f172a", show="•")

        self.skins = {
            "default": {
                "name": "Skin predeterminada",
                "cost": 0,
                "owned": True,
                "base": "#a16207",
                "dark": "#78350f",
            },
            "infernal": {
                "name": "Dragon infernal",
                "cost": 50,
                "owned": False,
                "base": "#ef4444",
                "dark": "#7f1d1d",
            },
        }
        self.equipped_skin = "default"

        self.screen = "login"  # login | register_account | recover_password | main_menu | shop | skins_menu | playing | pause_menu | game_over_menu
        self.buttons: list[tuple[float, float, float, float, str]] = []

        self.reset_run(reset_record=True)

        self.root.bind("r", self.on_restart_request)
        self.root.bind("R", self.on_restart_request)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.root.bind("<Return>", self.on_enter_key)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.loop()

    def load_accounts(self) -> dict[str, dict[str, object]]:
        if not self.data_file.exists():
            return {}
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save_accounts(self) -> None:
        try:
            self.data_file.write_text(json.dumps(self.accounts, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def save_current_account(self) -> None:
        if not self.current_user:
            return
        current_info = self.accounts.get(self.current_user, {})
        if not isinstance(current_info, dict):
            current_info = {}
        owned = [key for key, skin in self.skins.items() if bool(skin["owned"])]
        # Conserva credenciales/correo ya guardados para no romper login ni recuperación.
        updated_info = {
            "password": str(current_info.get("password", "")),
            "email": str(current_info.get("email", "")),
            "emilianos": int(self.emilianos),
            "best_score": int(self.best_score),
            "equipped_skin": self.equipped_skin,
            "owned_skins": owned,
        }
        self.accounts[self.current_user] = updated_info
        self.save_accounts()

    def is_valid_email(self, value: str) -> bool:
        email = value.strip()
        return "@" in email and "." in email

    def find_account_by_email(self, email: str) -> str:
        normalized = email.strip().lower()
        if not normalized:
            return ""
        return next(
            (
                username
                for username, info in self.accounts.items()
                if isinstance(info, dict) and str(info.get("email", "")).strip().lower() == normalized
            ),
            "",
        )

    def apply_account(self, username: str, password: str) -> bool:
        info = self.accounts.get(username)
        if not isinstance(info, dict):
            info = {
                "password": password,
                "email": "",
                "emilianos": 0,
                "best_score": 0,
                "equipped_skin": "default",
                "owned_skins": ["default"],
            }
            self.accounts[username] = info
        elif str(info.get("password", "")) != password:
            return False

        self.current_user = username
        self.emilianos = int(info.get("emilianos", 0))
        self.best_score = int(info.get("best_score", 0))

        owned_skins = set(info.get("owned_skins", ["default"]))
        owned_skins.add("default")
        for key, skin in self.skins.items():
            skin["owned"] = key in owned_skins

        equipped = str(info.get("equipped_skin", "default"))
        self.equipped_skin = equipped if equipped in self.skins and self.skins[equipped]["owned"] else "default"
        self.score_var.set("Puntaje: 0")
        self.best_var.set(f"Récord: {self.best_score}")
        self.emilianos_var.set(f"Emilianos: {self.emilianos}")
        self.save_current_account()
        return True

    def generate_recovery_code(self, length: int = 6) -> str:
        digits = "0123456789"
        return "".join(random.choice(digits) for _ in range(max(1, int(length))))

    def send_recovery_code(self, recipient: str, code: str) -> tuple[bool, str]:
        host = os.getenv("SMTP_HOST", "")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER", "")
        password = os.getenv("SMTP_PASS", "")
        sender = os.getenv("SMTP_SENDER", user)

        if not host or not user or not password or not sender:
            return False, "SMTP no configurado (define SMTP_HOST/SMTP_USER/SMTP_PASS/SMTP_SENDER)."

        msg = EmailMessage()
        msg["Subject"] = "Código de recuperación - Modern Dinosaur Game"
        msg["From"] = sender
        msg["To"] = recipient
        msg.set_content(f"Tu código de recuperación es: {code}")

        try:
            with smtplib.SMTP(host, port, timeout=12) as server:
                server.starttls()
                server.login(user, password)
                server.send_message(msg)
            return True, f"Código enviado a {recipient}"
        except Exception:
            return False, "No se pudo enviar el correo. Revisa la configuración SMTP."

    def send_recovery_email(self, recipient: str, code: str) -> tuple[bool, str]:
        # Compatibilidad con llamadas existentes.
        return self.send_recovery_code(recipient, code)

    def on_enter_key(self, _event=None) -> None:
        if self.screen == "login":
            self.handle_action("login")
        elif self.screen == "recover_password":
            self.handle_action("reset_password")
        elif self.screen == "register_account":
            self.handle_action("register")

    def on_close(self) -> None:
        self.save_current_account()
        self.root.destroy()

    def on_resize(self, event: tk.Event) -> None:
        self.game_width = max(700, int(event.width))
        self.game_height = max(420, int(event.height))
        self.ground_y = self.game_height - 170

        self.player_y = self.ground_y - self.player_h
        for obs in self.obstacles:
            if obs["type"] == "cactus":
                obs["y"] = self.ground_y - float(obs["h"])

    def load_cactus_images(self) -> list[tk.PhotoImage]:
        assets_dir = Path(CACTUS_ASSETS_DIR)
        if not assets_dir.is_dir():
            return []

        images: list[tk.PhotoImage] = []
        for image_path in sorted(assets_dir.glob("*.png")):
            try:
                images.append(tk.PhotoImage(file=str(image_path)))
            except tk.TclError:
                continue
        return images

    def reset_run(self, reset_record: bool) -> None:
        if reset_record:
            self.best_score = 0

        self.player_x = 100
        self.player_w = 58
        self.player_h = 50
        self.stand_h = 50
        self.crouch_h = 34
        self.player_y = self.ground_y - self.player_h
        self.vel_y = 0
        self.grounded = True
        self.crouching = False

        self.speed = 8.0
        if not hasattr(self, "_movement_binds_ready"):
            self.root.bind("<space>", self.on_jump, add="+")
            self.root.bind("<Up>", self.on_jump, add="+")
            self.root.bind("<Down>", self.on_crouch_press, add="+")
            self.root.bind("<KeyRelease-Down>", self.on_crouch_release, add="+")
            self._movement_binds_ready = True
        self.score = 0
        self.score_elapsed_ms = 0
        self.spawn_timer = random.randint(SPAWN_MIN, SPAWN_MAX)
        self.coin_timer = random.randint(COIN_SPAWN_MIN, COIN_SPAWN_MAX)
        self.obstacles: list[dict[str, object]] = []
        self.coins: list[dict[str, float]] = []
        self.running = True
        self.score_var.set("Puntaje: 0")
        self.best_var.set(f"Récord: {self.best_score}")
        self.emilianos_var.set(f"Emilianos: {self.emilianos}")

    def restart_keep_progress(self) -> None:
        current_score = self.score
        current_best = self.best_score

        self.player_x = 100
        self.player_w = 58
        self.player_h = 50
        self.player_y = self.ground_y - self.player_h
        self.vel_y = 0
        self.grounded = True
        self.crouching = False

        self.speed = 8.0
        self.score = current_score
        self.best_score = current_best
        self.score_elapsed_ms = 0
        self.spawn_timer = random.randint(SPAWN_MIN, SPAWN_MAX)
        self.coin_timer = random.randint(COIN_SPAWN_MIN, COIN_SPAWN_MAX)
        self.obstacles = []
        self.coins = []
        self.running = True
        self.score_var.set(f"Puntaje: {self.score}")
        self.best_var.set(f"Récord: {self.best_score}")
        self.emilianos_var.set(f"Emilianos: {self.emilianos}")

    def on_crouch_press(self, _event=None) -> None:
        if self.screen != "playing" or not self.running:
            return
        if not self.crouching:
            self.crouching = True
            self.player_h = self.crouch_h
            self.player_y = self.ground_y - self.player_h

    def on_crouch_release(self, _event=None) -> None:
        if self.crouching:
            self.crouching = False
            self.player_h = self.stand_h
            self.player_y = self.ground_y - self.player_h

    def on_jump(self, _event=None) -> None:
        if self.screen == "playing" and self.running and self.grounded:
            self.vel_y = JUMP_FORCE
            self.grounded = False

    def on_restart_request(self, _event=None) -> None:
        if self.screen == "playing":
            self.screen = "pause_menu"

    def on_canvas_click(self, event: tk.Event) -> None:
        for x1, y1, x2, y2, action in self.buttons:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.handle_action(action)
                return

        if self.screen == "playing" and self.running:
            self.on_jump()

    def handle_action(self, action: str) -> None:
        if action == "login":
            username = self.login_var.get().strip()
            password = self.password_var.get()
            if not username or not password:
                self.login_status_var.set("Completa usuario y contraseña")
                return
            if self.apply_account(username, password):
                self.login_status_var.set("")
                self.screen = "main_menu"
                self.password_var.set("")
                return
            self.login_status_var.set("Usuario o contraseña incorrectos")
            return
        if action == "open_recover":
            self.recover_status_var.set("")
            self.recover_email_var.set("")
            self.recover_code_var.set("")
            self.recover_new_pass_var.set("")
            self.recover_confirm_pass_var.set("")
            self.recovery_code = ""
            self.recovery_verified_email = ""
            self.screen = "recover_password"
            return
        if action == "open_register":
            self.register_status_var.set("")
            self.register_user_var.set("")
            self.register_email_var.set("")
            self.register_pass_var.set("")
            self.register_confirm_var.set("")
            self.screen = "register_account"
            return
        if action == "register":
            user = self.register_user_var.get().strip()
            email = self.register_email_var.get().strip()
            pwd = self.register_pass_var.get()
            confirm = self.register_confirm_var.get()
            if not user or not email or not pwd or not confirm:
                self.register_status_var.set("Completa todos los campos")
                return
            if not self.is_valid_email(email):
                self.register_status_var.set("Correo inválido")
                return
            if pwd != confirm:
                self.register_status_var.set("Las contraseñas no coinciden")
                return
            if user in self.accounts:
                self.register_status_var.set("Ese usuario ya existe")
                return
            if self.find_account_by_email(email):
                self.register_status_var.set("Ese correo ya está registrado")
                return
            self.accounts[user] = {
                "password": pwd,
                "email": email,
                "emilianos": 0,
                "best_score": 0,
                "equipped_skin": "default",
                "owned_skins": ["default"],
            }
            self.save_accounts()
            self.login_var.set(user)
            self.password_var.set("")
            self.register_status_var.set("Cuenta creada. Inicia sesión")
            self.screen = "login"
            return
        if action == "back_login_from_register":
            self.screen = "login"
            self.register_status_var.set("")
            return
        if action == "send_recovery":
            email = self.recover_email_var.get().strip()
            if not self.is_valid_email(email):
                self.recover_status_var.set("Ingresa un correo electrónico válido")
                return
            if not self.find_account_by_email(email):
                self.recover_status_var.set("Ese correo no está registrado")
                return
            self.recovery_code = self.generate_recovery_code(6)
            self.recovery_verified_email = ""
            ok, msg = self.send_recovery_code(email, self.recovery_code)
            self.recover_status_var.set(msg)
            return
        if action == "verify_recovery":
            if not self.recovery_code:
                self.recover_status_var.set("Primero envía el código a tu correo")
                return
            current_email = self.recover_email_var.get().strip().lower()
            if self.recover_code_var.get().strip() == self.recovery_code:
                self.recovery_verified_email = current_email
                self.recover_status_var.set("Código correcto. Ahora escribe tu nueva contraseña")
            else:
                self.recovery_verified_email = ""
                self.recover_status_var.set("Código incorrecto")
            return
        if action == "reset_password":
            email = self.recover_email_var.get().strip().lower()
            new_password = self.recover_new_pass_var.get()
            confirm_password = self.recover_confirm_pass_var.get()

            if not email or not new_password or not confirm_password:
                self.recover_status_var.set("Completa correo y nueva contraseña")
                return
            if self.recovery_verified_email != email:
                self.recover_status_var.set("Primero verifica el código de recuperación")
                return
            if new_password != confirm_password:
                self.recover_status_var.set("Las contraseñas no coinciden")
                return

            target_user = self.find_account_by_email(email)
            if not target_user:
                self.recover_status_var.set("Ese correo no está registrado")
                return

            info = self.accounts[target_user]
            if not isinstance(info, dict):
                self.recover_status_var.set("Cuenta inválida")
                return

            info["password"] = new_password
            self.accounts[target_user] = info
            self.save_accounts()
            self.login_var.set(target_user)
            self.password_var.set("")
            self.recover_status_var.set("Contraseña actualizada. Inicia sesión")
            self.recover_code_var.set("")
            self.recover_new_pass_var.set("")
            self.recover_confirm_pass_var.set("")
            self.recovery_code = ""
            self.recovery_verified_email = ""
            self.screen = "login"
            return
        if action == "back_login":
            self.screen = "login"
            self.recover_status_var.set("")
            self.recover_code_var.set("")
            self.recover_new_pass_var.set("")
            self.recover_confirm_pass_var.set("")
            self.recovery_verified_email = ""
            return
        if action == "play":
            self.screen = "playing"
            self.reset_run(reset_record=False)
            return
        if action == "exit":
            self.root.destroy()
            return
        if action == "open_shop":
            self.screen = "shop"
            return
        if action == "open_skins":
            self.screen = "skins_menu"
            return
        if action == "back_menu":
            self.screen = "main_menu"
            self.running = True
            return
        if action == "continue_play":
            self.screen = "playing"
            return
        if action == "play_again":
            self.screen = "playing"
            self.reset_run(reset_record=False)
            return
        if action.startswith("skin:"):
            key = action.split(":", 1)[1]
            skin = self.skins[key]
            if not skin["owned"]:
                cost = int(skin["cost"])
                if self.emilianos >= cost:
                    self.emilianos -= cost
                    skin["owned"] = True
                    self.emilianos_var.set(f"Emilianos: {self.emilianos}")
            if skin["owned"]:
                self.equipped_skin = key
            self.save_current_account()
            return
        if action.startswith("equip:"):
            key = action.split(":", 1)[1]
            skin = self.skins.get(key)
            if skin and skin["owned"]:
                self.equipped_skin = key
                self.save_current_account()
                return

    def spawn_obstacle(self) -> None:
        can_spawn_bird = self.score >= BIRD_SCORE_THRESHOLD
        spawn_bird = can_spawn_bird and random.random() < 0.4

        if spawn_bird:
            flight_level = random.choice([90, 150, 210])
            obstacle = {"type": "bird", "x": self.game_width + 30, "y": self.ground_y - flight_level, "w": 80, "h": 44, "image": None}
        elif self.cactus_images:
            sprite = random.choice(self.cactus_images)
            obstacle = {"type": "cactus", "x": self.game_width + 20, "y": self.ground_y - sprite.height(), "w": sprite.width(), "h": sprite.height(), "image": sprite}
        else:
            tall = random.random() > 0.5
            h = 60 if tall else 40
            w = 28 if tall else 42
            obstacle = {"type": "cactus", "x": self.game_width + 20, "y": self.ground_y - h, "w": w, "h": h, "image": None}
        self.obstacles.append(obstacle)

    def spawn_coin(self) -> None:
        r = 22.0
        y = self.ground_y - random.choice([44, 44, 44, 70, 120])
        self.coins.append({"x": float(self.game_width + 30), "y": float(y), "r": r})

    def collide(self, obs: dict[str, object]) -> bool:
        px1, py1 = self.player_x + 6, self.player_y + 4
        px2, py2 = px1 + self.player_w - 12, py1 + self.player_h - 6

        ox1 = float(obs["x"])
        oy1 = float(obs["y"])
        ox2 = ox1 + float(obs["w"])
        oy2 = oy1 + float(obs["h"])
        return px1 < ox2 and px2 > ox1 and py1 < oy2 and py2 > oy1

    def collect_coin(self, coin: dict[str, float]) -> bool:
        px1, py1 = self.player_x + 6, self.player_y + 4
        px2, py2 = px1 + self.player_w - 12, py1 + self.player_h - 6

        cx = coin["x"] + coin["r"]
        cy = coin["y"] + coin["r"]
        closest_x = min(max(cx, px1), px2)
        closest_y = min(max(cy, py1), py2)
        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy <= coin["r"] * coin["r"]

    def update(self) -> None:
        if self.screen != "playing" or not self.running:
            return

        self.vel_y += GRAVITY
        self.player_y += self.vel_y
        if self.player_y >= self.ground_y - self.player_h:
            self.player_y = self.ground_y - self.player_h
            self.vel_y = 0
            self.grounded = True

        self.score_elapsed_ms += FRAME_MS
        while self.score_elapsed_ms >= 1000:
            self.score += 10
            self.score_elapsed_ms -= 1000
            self.score_var.set(f"Puntaje: {self.score}")

        self.spawn_timer -= FRAME_MS
        if self.spawn_timer <= 0:
            self.spawn_obstacle()
            self.spawn_timer = random.randint(SPAWN_MIN, SPAWN_MAX)

        self.coin_timer -= FRAME_MS
        if self.coin_timer <= 0:
            if random.random() < COIN_SPAWN_CHANCE:
                self.spawn_coin()
            self.coin_timer = random.randint(COIN_SPAWN_MIN, COIN_SPAWN_MAX)

        self.speed += 0.002
        for obs in self.obstacles:
            base_speed = self.speed * (1.25 if obs["type"] == "bird" else 1.0)
            obs["x"] = float(obs["x"]) - base_speed
            if obs["type"] == "cactus":
                obs["y"] = self.ground_y - float(obs["h"])
            if self.collide(obs):
                self.running = False
                self.best_score = max(self.best_score, self.score)
                self.best_var.set(f"Récord: {self.best_score}")
                self.screen = "game_over_menu"
                self.save_current_account()

        new_coins: list[dict[str, float]] = []
        for coin in self.coins:
            coin["x"] -= self.speed * 1.05
            if self.collect_coin(coin):
                self.emilianos += 2
                self.emilianos_var.set(f"Emilianos: {self.emilianos}")
                self.save_current_account()
                continue
            if coin["x"] + coin["r"] * 2 > -40:
                new_coins.append(coin)
        self.coins = new_coins

        self.obstacles = [obs for obs in self.obstacles if float(obs["x"]) + float(obs["w"]) > -50]

    def draw_player_default(self, x: float, y: float, base: str, dark: str) -> None:
        if self.crouching:
            self.canvas.create_rectangle(x + 12, y + 12, x + 52, y + 34, fill=base, outline=dark, width=2)
            self.canvas.create_oval(x + 40, y + 6, x + 58, y + 22, fill=base, outline=dark, width=2)
            self.canvas.create_oval(x + 50, y + 13, x + 54, y + 17, fill="#0f172a", outline="")
        else:
            self.canvas.create_rectangle(x + 12, y + 12, x + 48, y + 42, fill=base, outline=dark, width=2)
            self.canvas.create_oval(x + 34, y + 4, x + 58, y + 24, fill=base, outline=dark, width=2)
            self.canvas.create_polygon(x + 6, y + 22, x + 14, y + 26, x + 8, y + 34, fill=base, outline=dark, width=2)
            self.canvas.create_rectangle(x + 20, y + 42, x + 28, y + 50, fill=base, outline=dark)
            self.canvas.create_rectangle(x + 34, y + 42, x + 42, y + 50, fill=base, outline=dark)
            self.canvas.create_oval(x + 48, y + 14, x + 52, y + 18, fill="#0f172a", outline="")

    def draw_player_cr7(self, x: float, y: float) -> None:
        # Dinosaurio inspirado en uniforme de la selección portuguesa
        shirt = "#dc2626"
        stripe = "#16a34a"
        detail = "#111827"
        shorts = "#14532d"
        skin = "#f59e0b"

        self.canvas.create_rectangle(x + 10, y + 12, x + 50, y + 40, fill=shirt, outline=detail, width=2)
        self.canvas.create_rectangle(x + 28, y + 12, x + 36, y + 40, fill=stripe, outline="")
        self.canvas.create_oval(x + 33, y + 3, x + 60, y + 24, fill=skin, outline=detail, width=2)
        self.canvas.create_rectangle(x + 18, y + 40, x + 42, y + 50, fill=shorts, outline=detail)
        self.canvas.create_rectangle(x + 20, y + 50, x + 27, y + 58, fill=shirt, outline=detail)
        self.canvas.create_rectangle(x + 34, y + 50, x + 41, y + 58, fill=shirt, outline=detail)
        self.canvas.create_text(x + 30, y + 26, text="7", fill="#facc15", font=("Segoe UI", 12, "bold"))
        self.canvas.create_oval(x + 50, y + 13, x + 54, y + 17, fill="#0f172a", outline="")

    def draw_player_messi(self, x: float, y: float) -> None:
        # Dinosaurio con uniforme inspirado en Messi
        shirt = "#60a5fa"
        stripe = "#e0f2fe"
        detail = "#0f172a"
        shorts = "#1e3a8a"
        skin = "#f59e0b"

        self.canvas.create_rectangle(x + 10, y + 12, x + 50, y + 40, fill=shirt, outline=detail, width=2)
        self.canvas.create_rectangle(x + 18, y + 12, x + 24, y + 40, fill=stripe, outline="")
        self.canvas.create_rectangle(x + 30, y + 12, x + 36, y + 40, fill=stripe, outline="")
        self.canvas.create_oval(x + 33, y + 3, x + 60, y + 24, fill=skin, outline=detail, width=2)
        self.canvas.create_rectangle(x + 18, y + 40, x + 42, y + 50, fill=shorts, outline=detail)
        self.canvas.create_rectangle(x + 20, y + 50, x + 27, y + 58, fill=shirt, outline=detail)
        self.canvas.create_rectangle(x + 34, y + 50, x + 41, y + 58, fill=shirt, outline=detail)
        self.canvas.create_text(x + 30, y + 26, text="10", fill="#111827", font=("Segoe UI", 10, "bold"))
        self.canvas.create_oval(x + 50, y + 13, x + 54, y + 17, fill="#0f172a", outline="")

    def draw_player_neymar(self, x: float, y: float) -> None:
        # Dinosaurio con uniforme inspirado en Brasil
        shirt = "#facc15"
        detail = "#166534"
        shorts = "#1d4ed8"
        skin = "#f59e0b"

        self.canvas.create_rectangle(x + 10, y + 12, x + 50, y + 40, fill=shirt, outline=detail, width=2)
        self.canvas.create_polygon(x + 30, y + 18, x + 36, y + 26, x + 30, y + 34, x + 24, y + 26, fill="#2563eb", outline="")
        self.canvas.create_oval(x + 33, y + 3, x + 60, y + 24, fill=skin, outline="#111827", width=2)
        self.canvas.create_rectangle(x + 18, y + 40, x + 42, y + 50, fill=shorts, outline="#111827")
        self.canvas.create_rectangle(x + 20, y + 50, x + 27, y + 58, fill=shirt, outline="#111827")
        self.canvas.create_rectangle(x + 34, y + 50, x + 41, y + 58, fill=shirt, outline="#111827")
        self.canvas.create_text(x + 30, y + 26, text="10", fill="#111827", font=("Segoe UI", 10, "bold"))
        self.canvas.create_oval(x + 50, y + 13, x + 54, y + 17, fill="#0f172a", outline="")

    def draw_player_infernal(self, x: float, y: float) -> None:
        # Inspirado en una silueta de dragon volador (sin cambiar escala del personaje)
        wing_fill = "#c2410c"
        wing_dark = "#7c2d12"
        membrane = "#ea580c"
        body_fill = "#292524"
        body_dark = "#0c0a09"
        horn = "#fbbf24"

        # Alas extendidas (compactas para mantenerse en el bounding actual)
        self.canvas.create_polygon(x + 8, y + 20, x + 24, y + 8, x + 30, y + 24, x + 16, y + 30, fill=wing_fill, outline=wing_dark, width=2)
        self.canvas.create_polygon(x + 30, y + 24, x + 52, y + 10, x + 56, y + 26, x + 40, y + 34, fill=wing_fill, outline=wing_dark, width=2)
        self.canvas.create_polygon(x + 17, y + 24, x + 24, y + 14, x + 28, y + 24, x + 20, y + 28, fill=membrane, outline="")
        self.canvas.create_polygon(x + 39, y + 24, x + 47, y + 15, x + 50, y + 27, x + 42, y + 32, fill=membrane, outline="")

        # Cuerpo/cabeza
        self.canvas.create_oval(x + 20, y + 20, x + 42, y + 42, fill=body_fill, outline=body_dark, width=2)
        self.canvas.create_oval(x + 34, y + 24, x + 54, y + 42, fill=body_fill, outline=body_dark, width=2)

        # Cuernos y brillo ocular
        self.canvas.create_polygon(x + 41, y + 22, x + 45, y + 15, x + 47, y + 23, fill=horn, outline="")
        self.canvas.create_polygon(x + 47, y + 23, x + 51, y + 17, x + 52, y + 25, fill=horn, outline="")
        self.canvas.create_oval(x + 49, y + 31, x + 52, y + 34, fill="#34d399", outline="")

        # Cola/espinas
        self.canvas.create_polygon(x + 20, y + 34, x + 12, y + 38, x + 22, y + 39, fill=body_fill, outline=body_dark, width=1)
        for i in range(4):
            sx = x + 26 + i * 3
            self.canvas.create_polygon(sx, y + 20 - i, sx + 2, y + 15 - i, sx + 3, y + 20 - i, fill=horn, outline="")

    def draw_player(self) -> None:
        x = self.player_x
        y = self.player_y
        if self.equipped_skin == "cr7":
            self.draw_player_cr7(x, y)
        elif self.equipped_skin == "infernal":
            self.draw_player_infernal(x, y)
        elif self.equipped_skin == "messi":
            self.draw_player_messi(x, y)
        elif self.equipped_skin == "neymar":
            self.draw_player_neymar(x, y)
        else:
            skin = self.skins[self.equipped_skin]
            self.draw_player_default(x, y, str(skin["base"]), str(skin["dark"]))

    def draw_bird(self, x: float, y: float) -> None:
        wing_up = int((x // 14) % 2 == 0)
        self.canvas.create_oval(x + 20, y + 8, x + 66, y + 36, fill="#f59e0b", outline="")
        self.canvas.create_polygon(x + 20, y + 20, x - 4, y + 24, x + 20, y + 29, fill="#fde68a", outline="")
        wing = [x + 42, y + 18, x + 70, y - 10, x + 36, y + 23] if wing_up else [x + 42, y + 22, x + 72, y + 40, x + 32, y + 28]
        self.canvas.create_polygon(wing, fill="#fbbf24", outline="")
        self.canvas.create_oval(x + 26, y + 14, x + 30, y + 18, fill="#0f172a", outline="")

    def draw_emiliano_coin(self, x: float, y: float, r: float) -> None:
        self.canvas.create_oval(x, y, x + 2 * r, y + 2 * r, fill="#facc15", outline="#a16207", width=2)
        self.canvas.create_oval(x + 4, y + 4, x + 2 * r - 4, y + 2 * r - 4, fill="#fbbf24", outline="#d97706", width=1)
        cx = x + r
        cy = y + r
        self.canvas.create_oval(cx - 4, cy - 12, cx + 4, cy - 4, fill="#92400e", outline="")
        self.canvas.create_line(cx, cy - 4, cx + 3, cy + 10, fill="#92400e", width=2)
        self.canvas.create_text(cx - 7, cy - 1, text="E", fill="#92400e", font=("Segoe UI", 9, "bold"))

    def is_day_sky(self) -> bool:
        return (self.score // SKY_SWITCH_POINTS) % 2 == 0

    def draw_day_sky(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#38bdf8", outline="")

        # Sol con brillo
        sx, sy = self.game_width * 0.78, self.game_height * 0.2
        for r, c in [(90, "#bfdbfe"), (70, "#dbeafe"), (45, "#ffffff")]:
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=c, outline="")

        # Rayos
        for dx, dy in [(130, 0), (0, 130), (92, 92), (92, -92), (-130, 0), (0, -130), (-92, -92), (-92, 92)]:
            self.canvas.create_line(sx, sy, sx + dx, sy + dy, fill="#e0f2fe", width=2)

        # Nubes
        clouds = [(160, 95, 70), (300, 150, 80), (520, 90, 60), (760, 170, 85)]
        for cx, cy, r in clouds:
            self.canvas.create_oval(cx - r, cy - r * 0.55, cx + r, cy + r * 0.55, fill="#f8fafc", outline="")
            self.canvas.create_oval(cx - r * 0.6, cy - r * 0.7, cx + r * 0.2, cy + r * 0.25, fill="#f8fafc", outline="")
            self.canvas.create_oval(cx - r * 0.1, cy - r * 0.75, cx + r * 0.7, cy + r * 0.25, fill="#f8fafc", outline="")

    def draw_night_sky(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#0f172a", outline="")

        # Estrellas
        for i in range(120):
            x = (i * 97) % int(self.game_width)
            y = (i * 53) % int(max(1, self.ground_y - 20))
            size = 2 if i % 3 == 0 else 1
            self.canvas.create_oval(x, y, x + size, y + size, fill="#e2e8f0", outline="")

        # Luna
        mx, my = self.game_width * 0.8, self.game_height * 0.2
        self.canvas.create_oval(mx - 55, my - 55, mx + 55, my + 55, fill="#e2e8f0", outline="")
        self.canvas.create_oval(mx - 42, my - 42, mx + 42, my + 42, fill="#f8fafc", outline="")

    def draw_dynamic_sky(self) -> None:
        if self.is_day_sky():
            self.draw_day_sky()
        else:
            self.draw_night_sky()

    def draw_ground(self) -> None:
        self.canvas.create_rectangle(0, self.ground_y, self.game_width, self.game_height, fill="#14532d", outline="")
        self.canvas.create_line(0, self.ground_y, self.game_width, self.ground_y, fill="#22c55e", width=3)

    def draw_grass_tuft(self, x: float, y: float, size: float) -> None:
        dark = "#166534"
        light = "#4ade80"
        self.canvas.create_polygon(x, y, x + size * 0.18, y - size * 0.95, x + size * 0.36, y, fill=dark, outline="#052e16", width=1)
        self.canvas.create_polygon(x + size * 0.22, y, x + size * 0.46, y - size * 1.15, x + size * 0.68, y, fill=dark, outline="#052e16", width=1)
        self.canvas.create_polygon(x + size * 0.52, y, x + size * 0.72, y - size * 0.85, x + size * 0.94, y, fill=dark, outline="#052e16", width=1)
        self.canvas.create_polygon(x + size * 0.28, y - size * 0.08, x + size * 0.42, y - size * 0.82, x + size * 0.52, y - size * 0.08, fill=light, outline="")

    def draw_grass_decor(self) -> None:
        spacing = 145
        phase = int(self.score * 0.9) % spacing
        for i in range(-1, int(self.game_width / spacing) + 2):
            x = i * spacing - phase
            if ((i * 31) + int(self.score / 18)) % 4 != 0:
                continue
            size = 42 if i % 2 == 0 else 34
            self.draw_grass_tuft(x + 20, self.ground_y + 6, size)

    def button(self, x: float, y: float, w: float, h: float, text: str, action: str, fill: str, text_color: str = "#111") -> None:
        self.buttons.append((x, y, x + w, y + h, action))
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=fill, outline="#111827", width=2)
        self.canvas.create_text(x + w / 2, y + h / 2, text=text, fill=text_color, font=("Segoe UI", 20, "bold"))

    def draw_login_screen(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#060b34", width=0)
        self.canvas.create_rectangle(0, self.game_height * 0.66, self.game_width, self.game_height, fill="#1e1b4b", width=0)

        card_w = min(760, self.game_width - 140)
        card_h = 500
        x1 = (self.game_width - card_w) / 2
        y1 = max(70, (self.game_height - card_h) / 2 - 10)
        x2 = x1 + card_w
        y2 = y1 + card_h

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#0b1120", outline="#334155", width=3)
        cx = self.game_width / 2

        self.canvas.create_oval(cx - 58, y1 + 36, cx + 58, y1 + 152, fill="#64748b", outline="#94a3b8", width=2)
        self.canvas.create_oval(cx - 26, y1 + 52, cx + 26, y1 + 100, fill="#e2e8f0", outline="")
        self.canvas.create_rectangle(cx - 34, y1 + 96, cx + 34, y1 + 132, fill="#e2e8f0", outline="")

        self.canvas.create_text(cx, y1 + 188, text="Iniciar sesión", fill="#e2e8f0", font=("Segoe UI", 42, "bold"))
        self.canvas.create_text(cx, y1 + 220, text="Tu progreso de Emilianos y skins se guardará por cuenta", fill="#93c5fd", font=("Segoe UI", 16, "bold"))

        self.canvas.create_text(cx - 280, y1 + 328, text="👤", fill="#1e3a5f", font=("Segoe UI", 18, "bold"), anchor="w")
        self.canvas.create_text(cx - 246, y1 + 328, text="Username", fill="#64748b", font=("Segoe UI", 15), anchor="w")

        self.canvas.create_text(cx - 280, y1 + 400, text="🔒", fill="#1e3a5f", font=("Segoe UI", 18, "bold"), anchor="w")
        self.canvas.create_text(cx - 246, y1 + 400, text="Password", fill="#64748b", font=("Segoe UI", 15), anchor="w")

        self.canvas.create_text(cx - 195, y1 + 441, text="¿Te olvidaste de la contraseña?", fill="#93c5fd", font=("Segoe UI", 14, "underline"), anchor="w")
        self.buttons.append((cx - 195, y1 + 430, cx + 120, y1 + 452, "open_recover"))
        self.canvas.create_text(cx + 195, y1 + 441, text="Registrarse", fill="#93c5fd", font=("Segoe UI", 14, "underline"), anchor="e")
        self.buttons.append((cx + 95, y1 + 430, cx + 195, y1 + 452, "open_register"))

        status = self.login_status_var.get().strip()
        if status:
            self.canvas.create_text(cx, y1 + 468, text=status, fill="#fca5a5", font=("Segoe UI", 14, "bold"))

        self.button(cx - 170, y1 + 478, 340, 56, "Entrar", "login", "#22c55e")

    def draw_register_screen(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#050a2b", width=0)
        card_w = min(760, self.game_width - 140)
        card_h = 520
        x1 = (self.game_width - card_w) / 2
        y1 = max(70, (self.game_height - card_h) / 2 - 10)
        x2 = x1 + card_w

        self.canvas.create_rectangle(x1, y1, x2, y1 + card_h, fill="#0b1120", outline="#334155", width=3)
        cx = self.game_width / 2
        self.canvas.create_text(cx, y1 + 76, text="Crear cuenta", fill="#e2e8f0", font=("Segoe UI", 40, "bold"))

        self.canvas.create_text(cx, y1 + 176, text="Nombre de usuario", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 248, text="Correo electrónico", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 320, text="Contraseña", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 392, text="Confirmar contraseña", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))

        status = self.register_status_var.get().strip()
        if status:
            self.canvas.create_text(cx, y1 + 426, text=status, fill="#fca5a5", font=("Segoe UI", 14, "bold"))

        self.button(cx - 170, y1 + 448, 340, 46, "Crear cuenta", "register", "#22c55e")
        self.button(cx - 170, y1 + 498, 340, 38, "Volver al login", "back_login_from_register", "#a78bfa")

    def draw_recover_screen(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#050a2b", width=0)
        card_w = min(760, self.game_width - 140)
        card_h = 620
        x1 = (self.game_width - card_w) / 2
        y1 = max(100, (self.game_height - card_h) / 2)
        x2 = x1 + card_w

        self.canvas.create_rectangle(x1, y1, x2, y1 + card_h, fill="#0b1120", outline="#334155", width=3)
        cx = self.game_width / 2
        self.canvas.create_text(cx, y1 + 62, text="Recuperar contraseña", fill="#e2e8f0", font=("Segoe UI", 38, "bold"))
        self.canvas.create_text(cx, y1 + 110, text="Ingresa tu correo, verifica código y define nueva contraseña", fill="#93c5fd", font=("Segoe UI", 15, "bold"))

        self.canvas.create_text(cx, y1 + 198, text="Correo electrónico", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 270, text="Código recibido", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 342, text="Nueva contraseña", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(cx, y1 + 414, text="Confirmar contraseña", fill="#cbd5e1", font=("Segoe UI", 16, "bold"))

        status = self.recover_status_var.get().strip()
        if status:
            self.canvas.create_text(cx, y1 + 452, text=status, fill="#facc15", font=("Segoe UI", 13, "bold"))

        self.button(cx - 170, y1 + 480, 340, 42, "Enviar código", "send_recovery", "#22c55e")
        self.button(cx - 170, y1 + 526, 340, 42, "Verificar código", "verify_recovery", "#38bdf8")
        self.button(cx - 170, y1 + 572, 340, 42, "Guardar nueva contraseña", "reset_password", "#f59e0b")
        self.button(cx - 170, y1 + 618, 340, 36, "Volver al login", "back_login", "#a78bfa")

    def draw_main_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#0b1120", width=0)
        self.canvas.create_text(self.game_width / 2, self.game_height / 2 - 140, text="Modern Dinosaur Game", fill="#e2e8f0", font=("Segoe UI", 42, "bold"))
        if self.current_user:
            self.canvas.create_text(self.game_width / 2, self.game_height / 2 - 95, text=f"Cuenta: {self.current_user}", fill="#93c5fd", font=("Segoe UI", 18, "bold"))
        cx = self.game_width / 2 - 130
        self.button(cx, self.game_height / 2 - 20, 260, 62, "Jugar", "play", "#22c55e")
        self.button(cx, self.game_height / 2 + 60, 260, 62, "Tienda", "open_shop", "#f59e0b")
        self.button(cx, self.game_height / 2 + 140, 260, 62, "Skins", "open_skins", "#60a5fa")
        self.button(cx, self.game_height / 2 + 220, 260, 62, "Salir", "exit", "#ef4444")

    def draw_shop(self) -> None:
        # Fondo inspirado en la fachada y separador central
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#121212", width=0)
        self.canvas.create_rectangle(0, 0, self.game_width, 100, fill="#1f2937", width=0)
        self.canvas.create_text(self.game_width / 2, 50, text="MERCADONA SHOP", fill="#22c55e", font=("Segoe UI", 36, "bold"))
        self.draw_shop_logo(110, 50, 36)
        self.draw_shop_logo(self.game_width - 110, 50, 36)
        self.canvas.create_rectangle(self.game_width / 2 - 20, 100, self.game_width / 2 + 20, self.game_height, fill="#6b7280", width=0)

        self.canvas.create_text(self.game_width / 4, 120, text="Lado izquierdo", fill="#d1d5db", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(self.game_width * 3 / 4, 120, text="Lado derecho", fill="#d1d5db", font=("Segoe UI", 16, "bold"))

        # Skins disponibles (solo las definidas en self.skins)
        left_keys = ["default", "infernal"]
        right_keys: list[str] = []

        self.draw_skin_cards(left_keys, start_x=70, start_y=150)
        self.draw_skin_cards(right_keys, start_x=self.game_width / 2 + 50, start_y=150)

        self.button(40, self.game_height - 90, 220, 52, "Volver al menú", "back_menu", "#a78bfa")

    def draw_shop_screen(self) -> None:
        # Alias para mantener compatibilidad con el nombre esperado por comentarios.
        self.draw_shop()

    def draw_shop_logo(self, cx: float, cy: float, r: float) -> None:
        # Logo inspirado en cesta de Mercadona dentro de circulo verde
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#f8fafc", outline="#15803d", width=5)
        self.canvas.create_rectangle(cx - 24, cy + 4, cx + 24, cy + 26, fill="#f59e0b", outline="")
        self.canvas.create_line(cx, cy + 6, cx, cy - 16, fill="#f59e0b", width=6)
        self.canvas.create_arc(cx - 15, cy - 10, cx + 15, cy + 12, start=0, extent=180, style="arc", outline="#f59e0b", width=4)
        self.canvas.create_oval(cx - 18, cy - 4, cx - 4, cy + 8, fill="#16a34a", outline="")
        self.canvas.create_oval(cx - 3, cy - 10, cx + 9, cy + 2, fill="#ef4444", outline="")
        self.canvas.create_oval(cx + 8, cy - 5, cx + 20, cy + 8, fill="#a3e635", outline="")
        self.canvas.create_oval(cx + 16, cy - 12, cx + 28, cy, fill="#9333ea", outline="")

    def draw_skin_preview(self, key: str, x: float, y: float) -> None:
        # Mini preview entre nombre y coste para facilitar compra
        if key == "infernal":
            self.draw_player_infernal(x + 8, y + 3)
        else:
            self.draw_player_default(x + 8, y + 3)

    def draw_skin_cards(self, keys: list[str], start_x: float, start_y: float) -> None:
        y = start_y
        for key in keys:
            skin = self.skins[key]
            owned = bool(skin["owned"])
            cost = int(skin["cost"])
            self.canvas.create_rectangle(start_x, y, start_x + 470, y + 130, fill="#1f2937", outline="#374151", width=2)
            self.canvas.create_text(start_x + 18, y + 22, anchor="w", text=skin["name"], fill="#e5e7eb", font=("Segoe UI", 18, "bold"))

            preview_x = start_x + 22
            preview_y = y + 36
            self.canvas.create_rectangle(preview_x, preview_y, preview_x + 74, preview_y + 56, fill="#111827", outline="#334155", width=2)
            self.draw_skin_preview(key, preview_x, preview_y)

            self.canvas.create_text(start_x + 18, y + 112, anchor="w", text=f"Coste: {cost} Emilianos", fill="#fbbf24", font=("Segoe UI", 14, "bold"))

            if self.equipped_skin == key:
                label = "Usando"
            elif owned:
                label = "Equipar"
            else:
                label = f"Comprar {cost}"
            self.button(start_x + 280, y + 40, 170, 50, label, f"skin:{key}", "#60a5fa")
            y += 145

    def draw_skins_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#0b1120", width=0)
        self.canvas.create_text(self.game_width / 2, 70, text="Skins", fill="#e2e8f0", font=("Segoe UI", 40, "bold"))
        self.canvas.create_text(self.game_width / 2, 108, text="Aquí puedes equipar sin entrar a la tienda", fill="#93c5fd", font=("Segoe UI", 16, "bold"))

        keys = ["default", "infernal"]
        self.draw_owned_skin_cards(keys, start_x=90, start_y=150)
        self.button(40, self.game_height - 90, 220, 52, "Volver al menú", "back_menu", "#a78bfa")

    def draw_skins_screen(self) -> None:
        # Alias para mantener compatibilidad con el nombre esperado por comentarios.
        self.draw_skins_menu()

    def draw_owned_skin_cards(self, keys: list[str], start_x: float, start_y: float) -> None:
        columns = [start_x, start_x + 520]
        card_w = 460
        card_h = 126
        gap_y = 18

        for i, key in enumerate(keys):
            skin = self.skins[key]
            col = i % 2
            row = i // 2
            x = columns[col]
            y = start_y + row * (card_h + gap_y)
            owned = bool(skin["owned"])

            self.canvas.create_rectangle(x, y, x + card_w, y + card_h, fill="#1f2937", outline="#334155", width=2)
            self.canvas.create_text(x + 16, y + 24, anchor="w", text=str(skin["name"]), fill="#e5e7eb", font=("Segoe UI", 18, "bold"))

            preview_x = x + 16
            preview_y = y + 40
            self.canvas.create_rectangle(preview_x, preview_y, preview_x + 74, preview_y + 56, fill="#111827", outline="#334155", width=2)
            self.draw_skin_preview(key, preview_x, preview_y)

            status = "Comprada" if owned else "No comprada"
            status_color = "#4ade80" if owned else "#fca5a5"
            self.canvas.create_text(x + 102, y + 74, anchor="w", text=f"Estado: {status}", fill=status_color, font=("Segoe UI", 14, "bold"))

            if self.equipped_skin == key:
                label = "Usando"
            elif owned:
                label = "Equipar"
            else:
                label = "Bloqueada"
            action = f"equip:{key}" if owned else "none"
            btn_color = "#60a5fa" if owned else "#6b7280"
            self.button(x + 280, y + 38, 160, 50, label, action, btn_color)

    def draw_pause_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#020617", width=0)
        self.canvas.create_text(self.game_width / 2, self.game_height / 2 - 120, text="Juego en pausa", fill="#e2e8f0", font=("Segoe UI", 36, "bold"))
        self.button(self.game_width / 2 - 170, self.game_height / 2 - 20, 340, 64, "Seguir jugando", "continue_play", "#22c55e")
        self.button(self.game_width / 2 - 170, self.game_height / 2 + 70, 340, 64, "Volver al menú", "back_menu", "#a78bfa")

    def draw_game_over_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, self.game_width, self.game_height, fill="#020617", width=0)
        self.canvas.create_text(self.game_width / 2, self.game_height / 2 - 120, text="Has perdido", fill="#fb7185", font=("Segoe UI", 36, "bold"))
        self.button(self.game_width / 2 - 170, self.game_height / 2 - 20, 340, 64, "Jugar otra partida", "play_again", "#22c55e")
        self.button(self.game_width / 2 - 170, self.game_height / 2 + 70, 340, 64, "Volver al menú", "back_menu", "#a78bfa")

    def draw_game_over(self) -> None:
        # Alias para mantener compatibilidad con el nombre esperado por comentarios.
        self.draw_game_over_menu()

    def draw_game(self) -> None:
        self.draw_dynamic_sky()
        self.draw_ground()
        self.draw_player()
        for coin in self.coins:
            self.draw_emiliano_coin(coin["x"], coin["y"], coin["r"])
        for obs in self.obstacles:
            if obs["type"] == "bird":
                self.draw_bird(float(obs["x"]), float(obs["y"]))
            else:
                x1 = float(obs["x"])
                y1 = float(obs["y"])
                x2 = x1 + float(obs["w"])
                y2 = y1 + float(obs["h"])
                w = x2 - x1
                h = y2 - y1
                cactus_fill = "#84cc16"
                cactus_dark = "#3f6212"

                # Tronco principal tipo saguaro
                trunk_x1 = x1 + w * 0.36
                trunk_x2 = x1 + w * 0.64
                self.canvas.create_rectangle(trunk_x1, y1, trunk_x2, y2, fill=cactus_fill, outline=cactus_dark, width=2)

                # Brazo izquierdo: segmento horizontal + segmento vertical
                left_joint_y = y1 + h * 0.40
                left_arm_h = max(4.0, h * 0.16)
                self.canvas.create_rectangle(
                    x1 + w * 0.14,
                    left_joint_y,
                    trunk_x1,
                    left_joint_y + left_arm_h,
                    fill=cactus_fill,
                    outline=cactus_dark,
                    width=2,
                )
                self.canvas.create_rectangle(
                    x1 + w * 0.14,
                    y1 + h * 0.14,
                    x1 + w * 0.28,
                    left_joint_y,
                    fill=cactus_fill,
                    outline=cactus_dark,
                    width=2,
                )

                # Brazo derecho: segmento horizontal + segmento vertical (más alto)
                right_joint_y = y1 + h * 0.30
                right_arm_h = max(4.0, h * 0.16)
                self.canvas.create_rectangle(
                    trunk_x2,
                    right_joint_y,
                    x1 + w * 0.88,
                    right_joint_y + right_arm_h,
                    fill=cactus_fill,
                    outline=cactus_dark,
                    width=2,
                )
                self.canvas.create_rectangle(
                    x1 + w * 0.74,
                    y1 + h * 0.05,
                    x1 + w * 0.88,
                    right_joint_y,
                    fill=cactus_fill,
                    outline=cactus_dark,
                    width=2,
                )

    def update_hud_branding_visibility(self) -> None:
        show = self.screen == "shop"
        if show and not self.title_label.winfo_ismapped():
            self.title_label.pack(side="left")
        if not show and self.title_label.winfo_ismapped():
            self.title_label.pack_forget()

    def update_shop_stats_visibility(self) -> None:
        in_shop = self.screen == "shop"
        if in_shop and self.score_label.winfo_ismapped():
            self.score_label.pack_forget()
        if in_shop and self.record_box.winfo_ismapped():
            self.record_box.pack_forget()

        if not in_shop and not self.score_label.winfo_ismapped():
            self.score_label.pack(side="left", padx=10)
        if not in_shop and not self.record_box.winfo_ismapped():
            self.record_box.pack(side="left", padx=10)

    def update_login_entry_visibility(self) -> None:
        if self.screen == "login":
            card_w = min(760, self.game_width - 140)
            card_h = 500
            y1 = max(70, (self.game_height - card_h) / 2 - 10)
            cx = self.game_width / 2

            entry_w = min(560, card_w - 120)
            self.login_entry.place(x=cx - entry_w / 2, y=y1 + 307, width=entry_w, height=38)
            self.password_entry.place(x=cx - entry_w / 2, y=y1 + 379, width=entry_w, height=38)
            self.recover_email_entry.place_forget()
            self.recover_code_entry.place_forget()
            self.register_user_entry.place_forget()
            self.register_email_entry.place_forget()
            self.register_pass_entry.place_forget()
            self.register_confirm_entry.place_forget()
            if self.root.focus_get() not in {self.login_entry, self.password_entry}:
                self.login_entry.focus_set()
        elif self.screen == "recover_password":
            card_w = min(760, self.game_width - 140)
            card_h = 500
            y1 = max(70, (self.game_height - card_h) / 2 - 10)
            cx = self.game_width / 2
            entry_w = min(560, card_w - 120)
            self.recover_email_entry.place(x=cx - entry_w / 2, y=y1 + 170, width=entry_w, height=38)
            self.recover_code_entry.place(x=cx - entry_w / 2, y=y1 + 230, width=entry_w, height=38)
            self.recover_new_pass_entry.place(x=cx - entry_w / 2, y=y1 + 290, width=entry_w, height=38)
            self.recover_confirm_pass_entry.place(x=cx - entry_w / 2, y=y1 + 350, width=entry_w, height=38)
            self.login_entry.place_forget()
            self.password_entry.place_forget()
            self.register_user_entry.place_forget()
            self.register_email_entry.place_forget()
            self.register_pass_entry.place_forget()
            self.register_confirm_entry.place_forget()
            if self.root.focus_get() not in {self.recover_email_entry, self.recover_code_entry, self.recover_new_pass_entry, self.recover_confirm_pass_entry}:
                self.recover_email_entry.focus_set()
        elif self.screen == "register_account":
            card_w = min(760, self.game_width - 140)
            card_h = 520
            y1 = max(70, (self.game_height - card_h) / 2 - 10)
            cx = self.game_width / 2
            entry_w = min(560, card_w - 120)
            self.register_user_entry.place(x=cx - entry_w / 2 + 2, y=y1 + 120, width=entry_w - 4, height=36)
            self.register_email_entry.place(x=cx - entry_w / 2 + 2, y=y1 + 192, width=entry_w - 4, height=36)
            self.register_pass_entry.place(x=cx - entry_w / 2 + 2, y=y1 + 264, width=entry_w - 4, height=36)
            self.register_confirm_entry.place(x=cx - entry_w / 2 + 2, y=y1 + 336, width=entry_w - 4, height=36)
            self.login_entry.place_forget()
            self.password_entry.place_forget()
            self.recover_email_entry.place_forget()
            self.recover_code_entry.place_forget()
            self.recover_new_pass_entry.place_forget()
            self.recover_confirm_pass_entry.place_forget()
            if self.root.focus_get() not in {self.register_user_entry, self.register_email_entry, self.register_pass_entry, self.register_confirm_entry}:
                self.register_user_entry.focus_set()
        else:
            self.login_entry.place_forget()
            self.password_entry.place_forget()
            self.recover_email_entry.place_forget()
            self.recover_code_entry.place_forget()
            self.recover_new_pass_entry.place_forget()
            self.recover_confirm_pass_entry.place_forget()
            self.register_user_entry.place_forget()
            self.register_email_entry.place_forget()
            self.register_pass_entry.place_forget()
            self.register_confirm_entry.place_forget()

    def update_help_label_visibility(self) -> None:
        show = self.screen in {"main_menu", "playing"}
        if show and not self.help_label.winfo_ismapped():
            self.help_label.pack(pady=(0, 14))
        if not show and self.help_label.winfo_ismapped():
            self.help_label.pack_forget()

    def draw(self) -> None:
        self.update_hud_branding_visibility()
        self.update_shop_stats_visibility()
        self.update_login_entry_visibility()
        self.update_help_label_visibility()
        self.canvas.delete("all")
        self.buttons = []

        if self.screen == "login":
            self.draw_login_screen()
        elif self.screen == "recover_password":
            self.draw_recover_screen()
        elif self.screen == "register_account":
            self.draw_register_screen()
        elif self.screen == "main_menu":
            self.draw_main_menu()
        elif self.screen == "shop":
            self.draw_shop()
        elif self.screen == "skins_menu":
            self.draw_skins_menu()
        elif self.screen == "pause_menu":
            self.draw_pause_menu()
        elif self.screen == "game_over_menu":
            self.draw_game_over_menu()
        else:
            self.draw_game()

    def loop(self) -> None:
        self.update()
        self.draw()
        self.root.after(FRAME_MS, self.loop)


def main() -> None:
    root = tk.Tk()
    DinoRunner(root)
    root.mainloop()


if __name__ == "__main__":
    main()
