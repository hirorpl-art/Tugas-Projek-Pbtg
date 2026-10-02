import math
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# ============================================================
# GEOMETRI EDU 3D
# Aplikasi pembelajaran geometri untuk Thonny
# Hanya memakai Python standar + Tkinter.
# ============================================================

APP_BG = "#e8f5e9"
PANEL = "#c8e6c9"
CARD = "#a5d6a7"
CARD2 = "#66bb6a"
TEXT = "#173b1a"
MUTED = "#47724a"
ACCENT = "#2e7d32"
GREEN = "#1b5e20"
YELLOW = "#43a047"
RED = "#c62828"

root = tk.Tk()
root.title("Kalkulator Geometri")
root.geometry("1250x780")
root.minsize(1050, 680)
root.configure(bg=APP_BG)

# -------------------------- STYLE --------------------------
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("TNotebook", background=APP_BG, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    background=PANEL,
    foreground=TEXT,
    padding=(18, 10),
    font=("Segoe UI", 10, "bold"),
)

style.map(
    "TNotebook.Tab",
    background=[("selected", ACCENT)],
    foreground=[("selected", "#06111a")],
)

style.configure(
    "TCombobox",
    fieldbackground=CARD,
    background=CARD2,
    foreground=TEXT,
    arrowcolor=TEXT,
)


# -------------------------- FUNGSI KEMBALI --------------------------
def kembali_ke_menu():
    root.destroy()

    # Buka file lain (sesuaikan dengan nama file kamu, misal: kalkulator_geometri.py)
    subprocess.Popen([sys.executable, "menul.py"])

# -------------------------- HELPERS --------------------------
def fmt(x):
    if abs(x) < 1e-10:
        x = 0
    return f"{x:.6f}".rstrip("0").rstrip(".")


def get_num(entry, label, allow_zero=False):
    try:
        x = float(entry.get().replace(",", "."))
    except Exception:
        raise ValueError(f"{label} harus berupa angka.")
    if allow_zero:
        if x < 0:
            raise ValueError(f"{label} tidak boleh negatif.")
    else:
        if x <= 0:
            raise ValueError(f"{label} harus lebih dari 0.")
    return x


def safe_calc(fn, result_widget):
    try:
        result_widget.config(text=fn())
    except Exception as e:
        messagebox.showerror("Input belum benar", str(e))


def label(parent, text, size=10, color=TEXT, bold=False, bg=None):
    return tk.Label(
        parent,
        text=text,
        bg=bg or CARD,
        fg=color,
        font=("Segoe UI", size, "bold" if bold else "normal"),
    )


def entry_row(parent, text):
    row = tk.Frame(parent, bg=CARD)
    row.pack(fill="x", pady=5)
    tk.Label(row, text=text, bg=CARD, fg=TEXT, font=("Segoe UI", 10)).pack(
        side="left"
    )
    ent = tk.Entry(
        row,
        bg="#f1f8e9",
        fg="#173b1a",
        insertbackground="#173b1a",
        relief="flat",
        font=("Segoe UI", 10),
        width=16,
    )
    ent.pack(side="right", ipady=6, padx=2)
    return ent


def button(parent, text, command, bg=ACCENT, fg="#ffffff"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=12,
        pady=9,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
    )


# ============================================================
# 3D ENGINE SEDERHANA
# ============================================================


class Shape3DViewer:

    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg="#12351b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.shape = "Kubus"
        self.params = {}
        self.angle = 0.0
        self.running = True
        self.dragging = False
        self.last_x = 0
        self.last_y = 0
        self.pitch = -0.28
        self.zoom = 1.0

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<MouseWheel>", self.wheel)
        self.canvas.bind("<Button-4>", lambda e: self.change_zoom(1.08))
        self.canvas.bind("<Button-5>", lambda e: self.change_zoom(0.92))

        self.animate()

    def start_drag(self, event):
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y

    def drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.angle += dx * 0.012
        self.pitch += dy * 0.006
        self.pitch = max(-1.1, min(0.4, self.pitch))
        self.last_x, self.last_y = event.x, event.y

    def wheel(self, event):
        self.change_zoom(1.08 if event.delta > 0 else 0.92)

    def change_zoom(self, factor):
        self.zoom *= factor
        self.zoom = max(0.55, min(2.0, self.zoom))

    def set_shape(self, shape, params):
        self.shape = shape
        self.params = params
        self.zoom = 1.0

    def project(self, p, cx, cy, scale):
        x, y, z = p
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        x1 = x * ca + z * sa
        z1 = -x * sa + z * ca

        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y2 = y * cp - z1 * sp
        z2 = y * sp + z1 * cp

        px = cx + x1 * scale
        py = cy - y2 * scale
        return px, py, z2

    def draw_line3d(self, a, b, cx, cy, scale, width=2):
        pa = self.project(a, cx, cy, scale)
        pb = self.project(b, cx, cy, scale)
        self.canvas.create_line(pa[0], pa[1], pb[0], pb[1], fill=ACCENT, width=width)

    def draw_polygon3d(self, points, cx, cy, scale, outline=ACCENT):
        pp = [self.project(p, cx, cy, scale) for p in points]
        self.canvas.create_polygon(
            [(p[0], p[1]) for p in pp], fill="#245b2a", outline=outline, width=2
        )

    def draw_cube(self, cx, cy, s):
        v = [
            (-1, -1, -1),
            (1, -1, -1),
            (1, -1, 1),
            (-1, -1, 1),
            (-1, 1, -1),
            (1, 1, -1),
            (1, 1, 1),
            (-1, 1, 1),
        ]
        faces = [
            [v[0], v[1], v[2], v[3]],
            [v[4], v[7], v[6], v[5]],
            [v[0], v[4], v[5], v[1]],
            [v[1], v[5], v[6], v[2]],
            [v[2], v[6], v[7], v[3]],
            [v[3], v[7], v[4], v[0]],
        ]
        for f in faces:
            self.draw_polygon3d(f, cx, cy, s)
        for a, b in [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]:
            self.draw_line3d(v[a], v[b], cx, cy, s, 2)

    def draw_cuboid(self, cx, cy, s, p, l, t):
        mx = max(p, l, t)
        x, z, y = p / mx, l / mx, t / mx
        v = [
            (-x, -y, -z),
            (x, -y, -z),
            (x, -y, z),
            (-x, -y, z),
            (-x, y, -z),
            (x, y, -z),
            (x, y, z),
            (-x, y, z),
        ]
        faces = [
            [v[0], v[1], v[2], v[3]],
            [v[4], v[7], v[6], v[5]],
            [v[0], v[4], v[5], v[1]],
            [v[1], v[5], v[6], v[2]],
            [v[2], v[6], v[7], v[3]],
            [v[3], v[7], v[4], v[0]],
        ]
        for f in faces:
            self.draw_polygon3d(f, cx, cy, s)
        for a, b in [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]:
            self.draw_line3d(v[a], v[b], cx, cy, s, 2)

    def draw_cylinder(self, cx, cy, s, r=1, h=1.5):
        n = 48
        rr = 1.0
        hh = h / max(2 * r, 0.0001)
        top, bottom = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            top.append((rr * math.cos(a), hh, rr * math.sin(a)))
            bottom.append((rr * math.cos(a), -hh, rr * math.sin(a)))

        self.draw_polygon3d(top, cx, cy, s)
        self.draw_polygon3d(list(reversed(bottom)), cx, cy, s)

        for i in range(n):
            self.draw_line3d(bottom[i], bottom[(i + 1) % n], cx, cy, s, 1)
            self.draw_line3d(top[i], top[(i + 1) % n], cx, cy, s, 1)
            if i % 6 == 0:
                self.draw_line3d(bottom[i], top[i], cx, cy, s, 1)

    def draw_cone(self, cx, cy, s, h=1.5):
        n = 48
        hh = h / 2
        base = [
            (math.cos(2 * math.pi * i / n), -hh, math.sin(2 * math.pi * i / n))
            for i in range(n)
        ]
        apex = (0, hh, 0)
        self.draw_polygon3d(list(reversed(base)), cx, cy, s)
        for i in range(n):
            self.draw_line3d(base[i], base[(i + 1) % n], cx, cy, s, 1)
            if i % 3 == 0:
                self.draw_line3d(base[i], apex, cx, cy, s, 1)

    def draw_pyramid(self, cx, cy, s):
        base = [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)]
        apex = (0, 1.3, 0)
        self.draw_polygon3d(base, cx, cy, s)
        for i in range(4):
            self.draw_line3d(base[i], base[(i + 1) % 4], cx, cy, s, 2)
            self.draw_line3d(base[i], apex, cx, cy, s, 2)

    def draw_sphere(self, cx, cy, s):
        n = 18
        m = 24
        for i in range(1, n):
            lat = -math.pi / 2 + math.pi * i / n
            ring = []
            for j in range(m + 1):
                lon = 2 * math.pi * j / m
                ring.append((
                    math.cos(lat) * math.cos(lon),
                    math.sin(lat),
                    math.cos(lat) * math.sin(lon),
                ))
            for j in range(m):
                self.draw_line3d(ring[j], ring[j + 1], cx, cy, s, 1)
        for j in range(m):
            lon = 2 * math.pi * j / m
            pts = []
            for i in range(n + 1):
                lat = -math.pi / 2 + math.pi * i / n
                pts.append((
                    math.cos(lat) * math.cos(lon),
                    math.sin(lat),
                    math.cos(lat) * math.sin(lon),
                ))
            for i in range(n):
                self.draw_line3d(pts[i], pts[i + 1], cx, cy, s, 1)

    def draw_prism(self, cx, cy, s):
        a = 1.15
        z1 = -0.8
        z2 = 0.8
        tri = [(-a, -0.8, z1), (a, -0.8, z1), (0, 0.9, z1)]
        tri2 = [(-a, -0.8, z2), (a, -0.8, z2), (0, 0.9, z2)]
        self.draw_polygon3d(tri, cx, cy, s)
        self.draw_polygon3d(tri2, cx, cy, s)
        for i in range(3):
            self.draw_line3d(tri[i], tri[(i + 1) % 3], cx, cy, s, 2)
            self.draw_line3d(tri2[i], tri2[(i + 1) % 3], cx, cy, s, 2)
            self.draw_line3d(tri[i], tri2[i], cx, cy, s, 2)

    def render(self):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 300)
        h = max(self.canvas.winfo_height(), 300)
        cx, cy = w / 2, h / 2 + 15
        scale = min(w, h) * 0.25 * self.zoom

        for x in range(0, w, 40):
            self.canvas.create_line(x, h - 35, x + 40, h, fill="#2d6333")
        self.canvas.create_text(
            cx,
            25,
            text=self.shape.upper() + " • VISUALISASI 3D",
            fill=TEXT,
            font=("Segoe UI", 13, "bold"),
        )
        self.canvas.create_text(
            cx,
            h - 18,
            text="Drag mouse untuk memutar • Scroll untuk zoom",
            fill=MUTED,
            font=("Segoe UI", 9),
        )

        if self.shape == "Kubus":
            self.draw_cube(cx, cy, scale)
        elif self.shape == "Balok":
            self.draw_cuboid(
                cx,
                cy,
                scale,
                self.params.get("p", 2),
                self.params.get("l", 1.5),
                self.params.get("t", 1),
            )
        elif self.shape == "Tabung":
            self.draw_cylinder(
                cx, cy, scale, self.params.get("r", 1), self.params.get("h", 2)
            )
        elif self.shape == "Kerucut":
            self.draw_cone(cx, cy, scale, self.params.get("h", 2))
        elif self.shape == "Bola":
            self.draw_sphere(cx, cy, scale)
        elif self.shape == "Limas Segiempat":
            self.draw_pyramid(cx, cy, scale)
        elif self.shape == "Prisma Segitiga":
            self.draw_prism(cx, cy, scale)

    def animate(self):
        if self.running:
            self.angle += 0.018
            self.render()
        self.parent.after(35, self.animate)


viewer = None

# ============================================================
# HEADER
# ============================================================
header = tk.Frame(root, bg=APP_BG)
header.pack(fill="x", padx=24, pady=(15, 6))

title_frame = tk.Frame(header, bg=APP_BG)
title_frame.pack(side="left")

tk.Label(
    title_frame,
    text="KALKULATOR GEOMETRI",
    bg=APP_BG,
    fg=ACCENT,
    font=("Segoe UI", 22, "bold"),
).pack(anchor="w")
tk.Label(
    title_frame,
    text="  Kalkulator 2D • Kalkulator 3D • Rumus • Visualisasi",
    bg=APP_BG,
    fg=MUTED,
    font=("Segoe UI", 10),
).pack(anchor="w")

# Tombol Kembali ke Menu Utama di Header sebelah kanan
button(
    header,
    text="⬅ KEMBALI KE MENU",
    command=kembali_ke_menu,
    bg=RED,
    fg="#ffffff",
).pack(side="right", padx=5)

# ============================================================
# NOTEBOOK
# ============================================================
tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=16, pady=10)

# ============================================================
# TAB KALKULATOR 2D
# ============================================================
tab2 = tk.Frame(tabs, bg=APP_BG)
tabs.add(tab2, text=" 📐 2D ")

left = tk.Frame(tab2, bg=CARD, width=360)
left.pack(side="left", fill="y", padx=(10, 5), pady=10)
left.pack_propagate(False)

right = tk.Frame(tab2, bg=PANEL)
right.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

tk.Label(
    left,
    text="KALKULATOR 2D",
    bg=CARD,
    fg=TEXT,
    font=("Segoe UI", 17, "bold"),
).pack(pady=16)

shape2 = ttk.Combobox(
    left,
    state="readonly",
    width=28,
    values=["Persegi", "Persegi Panjang", "Segitiga", "Lingkaran"],
)
shape2.current(0)
shape2.pack()

inputs2 = tk.Frame(left, bg=CARD)
inputs2.pack(fill="x", padx=18, pady=12)
e2 = {}


def rebuild2(event=None):
    for w in inputs2.winfo_children():
        w.destroy()
    e2.clear()
    specs = {
        "Persegi": ["Sisi"],
        "Persegi Panjang": ["Panjang", "Lebar"],
        "Segitiga": ["Alas", "Tinggi"],
        "Lingkaran": ["Jari-jari"],
    }
    for x in specs[shape2.get()]:
        e2[x] = entry_row(inputs2, x)


shape2.bind("<<ComboboxSelected>>", rebuild2)
rebuild2()

res2 = tk.Label(
    left,
    text="Hasil akan tampil di sini",
    bg="#f1f8e9",
    fg=GREEN,
    justify="left",
    anchor="w",
    padx=12,
    pady=10,
    font=("Consolas", 10, "bold"),
)
res2.pack(fill="x", padx=18, pady=8)


def calc2():
    s = shape2.get()
    e = e2
    if s == "Persegi":
        a = get_num(e["Sisi"], "Sisi")
        return f"Luas     = {fmt(a*a)} satuan²\nKeliling  = {fmt(4*a)} satuan"
    if s == "Persegi Panjang":
        p = get_num(e["Panjang"], "Panjang")
        l = get_num(e["Lebar"], "Lebar")
        return (
            f"Luas     = {fmt(p*l)} satuan²\nKeliling  ="
            f" {fmt(2*(p+l))} satuan"
        )
    if s == "Segitiga":
        a = get_num(e["Alas"], "Alas")
        t = get_num(e["Tinggi"], "Tinggi")
        return f"Luas     = {fmt(a*t/2)} satuan²"
    if s == "Lingkaran":
        r = get_num(e["Jari-jari"], "Jari-jari")
        return (
            f"Luas     = {fmt(math.pi*r*r)} satuan²\nKeliling  ="
            f" {fmt(2*math.pi*r)} satuan"
        )


button(left, "HITUNG", lambda: safe_calc(calc2, res2)).pack(
    fill="x", padx=18, pady=4
)
button(
    left,
    "RESET",
    lambda: (rebuild2(), res2.config(text="Hasil akan tampil di sini")),
    bg=CARD2,
    fg=TEXT,
).pack(fill="x", padx=18, pady=4)

tk.Label(
    right,
    text="Pilih bangun lalu masukkan ukurannya.",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 20, "bold"),
).pack(anchor="w", padx=25, pady=(25, 10))
tk.Label(
    right,
    text=(
        "Rumus dihitung otomatis. Satuan mengikuti input.\nContoh: jika"
        " panjang memakai cm, luas akan menjadi cm²."
    ),
    bg=PANEL,
    fg=MUTED,
    justify="left",
    font=("Segoe UI", 11),
).pack(anchor="w", padx=25)

# ============================================================
# SOAL LATIHAN SETIAP BANGUN DATAR
# ============================================================

quiz_frame = tk.Frame(right, bg=CARD)
quiz_frame.pack(fill="x", padx=25, pady=18)

tk.Label(
    quiz_frame,
    text="📝 SOAL LATIHAN",
    bg=CARD,
    fg=ACCENT,
    font=("Segoe UI", 15, "bold"),
).pack(anchor="w", padx=15, pady=(12, 4))

tk.Label(
    quiz_frame,
    text="Kerjakan soal sesuai bangun datar yang dipilih.",
    bg=CARD,
    fg=MUTED,
    font=("Segoe UI", 10),
).pack(anchor="w", padx=15, pady=(0, 8))

quiz_question = tk.Label(
    quiz_frame,
    text="",
    bg=CARD,
    fg=TEXT,
    justify="left",
    anchor="w",
    wraplength=600,
    font=("Segoe UI", 11, "bold"),
)
quiz_question.pack(fill="x", padx=15, pady=5)

quiz_answer = tk.Entry(
    quiz_frame,
    bg="#f1f8e9",
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    font=("Segoe UI", 10),
    width=18,
)
quiz_answer.pack(anchor="w", padx=15, pady=5, ipady=6)

quiz_result = tk.Label(
    quiz_frame,
    text="Masukkan jawaban lalu tekan CEK JAWABAN.",
    bg=CARD,
    fg=MUTED,
    font=("Segoe UI", 10, "bold"),
)
quiz_result.pack(anchor="w", padx=15, pady=5)

quiz_data = {
    "Persegi": {
        "question": (
            "Sebuah persegi memiliki sisi 8 cm. Berapa luas dan kelilingnya?"
            " Tulis: luas, keliling"
        ),
        "answers": (64, 32),
    },
    "Persegi Panjang": {
        "question": (
            "Sebuah persegi panjang memiliki panjang 12 cm dan lebar 5 cm. Berapa"
            " luas dan kelilingnya? Tulis: luas, keliling"
        ),
        "answers": (60, 34),
    },
    "Segitiga": {
        "question": (
            "Sebuah segitiga memiliki alas 10 cm dan tinggi 6 cm. Berapa"
            " luasnya?"
        ),
        "answers": (30,),
    },
    "Lingkaran": {
        "question": (
            "Sebuah lingkaran memiliki jari-jari 7 cm. Gunakan π = 22/7. Berapa"
            " luas dan kelilingnya? Tulis: luas, keliling"
        ),
        "answers": (154, 44),
    },
}


def tampilkan_soal():
    nama = shape2.get()
    data = quiz_data[nama]

    quiz_question.config(text="Soal: " + data["question"])
    quiz_answer.delete(0, tk.END)
    quiz_result.config(text="Masukkan jawaban lalu tekan CEK JAWABAN.", fg=MUTED)


def cek_jawaban():
    nama = shape2.get()
    data = quiz_data[nama]

    teks = quiz_answer.get().replace(",", " ").strip()

    try:
        jawaban_user = [float(x) for x in teks.split()]
    except ValueError:
        quiz_result.config(
            text="❌ Jawaban harus berupa angka. Contoh: 64 32", fg=RED
        )
        return

    benar = len(jawaban_user) == len(data["answers"])

    if benar:
        for user, kunci in zip(jawaban_user, data["answers"]):
            if abs(user - kunci) > 0.01:
                benar = False
                break

    if benar:
        quiz_result.config(text="✅ BENAR! Jawaban kamu tepat.", fg=GREEN)
    else:
        if len(data["answers"]) == 2:
            petunjuk = "Urutan jawaban: luas lalu keliling."
        else:
            petunjuk = "Masukkan satu jawaban luas."

        quiz_result.config(text="❌ Belum tepat. " + petunjuk, fg=RED)


button(quiz_frame, "CEK JAWABAN", cek_jawaban, bg=GREEN, fg="#ffffff").pack(
    anchor="w", padx=15, pady=(4, 12)
)

shape2.bind(
    "<<ComboboxSelected>>", lambda event: tampilkan_soal(), add="+"
)

tampilkan_soal()

# ============================================================
# TAB KALKULATOR 3D
# ============================================================
tab3 = tk.Frame(tabs, bg=APP_BG)
tabs.add(tab3, text=" 🧊 3D ")

left3 = tk.Frame(tab3, bg=CARD, width=370)
left3.pack(side="left", fill="y", padx=(10, 5), pady=10)
left3.pack_propagate(False)

right3 = tk.Frame(tab3, bg=PANEL)
right3.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

tk.Label(
    left3,
    text="KALKULATOR 3D",
    bg=CARD,
    fg=TEXT,
    font=("Segoe UI", 17, "bold"),
).pack(pady=15)

shape3 = ttk.Combobox(
    left3,
    state="readonly",
    width=28,
    values=["Kubus", "Balok", "Tabung", "Bola", "Kerucut"],
)
shape3.current(0)
shape3.pack()

inputs3 = tk.Frame(left3, bg=CARD)
inputs3.pack(fill="x", padx=18, pady=12)
e3 = {}


def rebuild3(event=None):
    for w in inputs3.winfo_children():
        w.destroy()
    e3.clear()
    specs = {
        "Kubus": ["Sisi"],
        "Balok": ["Panjang", "Lebar", "Tinggi"],
        "Tabung": ["Jari-jari", "Tinggi"],
        "Bola": ["Jari-jari"],
        "Kerucut": ["Jari-jari", "Tinggi"],
    }
    for x in specs[shape3.get()]:
        e3[x] = entry_row(inputs3, x)
    update_view()


shape3.bind("<<ComboboxSelected>>", rebuild3)

res3 = tk.Label(
    left3,
    text="Hasil akan tampil di sini",
    bg="#f1f8e9",
    fg=GREEN,
    justify="left",
    anchor="w",
    padx=12,
    pady=10,
    font=("Consolas", 10, "bold"),
)
res3.pack(fill="x", padx=18, pady=8)


def calc3():
    s = shape3.get()
    e = e3
    if s == "Kubus":
        a = get_num(e["Sisi"], "Sisi")
        return (
            f"Volume       = {fmt(a**3)} satuan³\nLuas permukaan ="
            f" {fmt(6*a*a)} satuan²"
        )
    if s == "Balok":
        p = get_num(e["Panjang"], "Panjang")
        l = get_num(e["Lebar"], "Lebar")
        t = get_num(e["Tinggi"], "Tinggi")
        return (
            f"Volume       = {fmt(p*l*t)} satuan³\nLuas permukaan ="
            f" {fmt(2*(p*l+p*t+l*t))} satuan²"
        )
    if s == "Tabung":
        r = get_num(e["Jari-jari"], "Jari-jari")
        t = get_num(e["Tinggi"], "Tinggi")
        return (
            f"Volume       = {fmt(math.pi*r*r*t)} satuan³\nLuas alas     ="
            f" {fmt(math.pi*r*r)} satuan²"
        )
    if s == "Bola":
        r = get_num(e["Jari-jari"], "Jari-jari")
        return (
            f"Volume       = {fmt(4*math.pi*r**3/3)} satuan³\nLuas permukaan ="
            f" {fmt(4*math.pi*r*r)} satuan²"
        )
    if s == "Kerucut":
        r = get_num(e["Jari-jari"], "Jari-jari")
        t = get_num(e["Tinggi"], "Tinggi")
        garis = math.sqrt(r * r + t * t)
        return (
            f"Volume       = {fmt(math.pi*r*r*t/3)} satuan³\nGaris pelukis ="
            f" {fmt(garis)} satuan\nLuas permukaan = {fmt(math.pi*r*(r+garis))}"
            " satuan²"
        )


def update_view():
    if viewer is None:
        return
    s = shape3.get()
    p = {}
    try:
        if s == "Balok":
            p = {
                "p": float(e3["Panjang"].get() or 2),
                "l": float(e3["Lebar"].get() or 1.5),
                "t": float(e3["Tinggi"].get() or 1),
            }
        elif s == "Tabung":
            p = {
                "r": float(e3["Jari-jari"].get() or 1),
                "h": float(e3["Tinggi"].get() or 2),
            }
        elif s == "Kerucut":
            p = {
                "r": float(e3["Jari-jari"].get() or 1),
                "h": float(e3["Tinggi"].get() or 2),
            }
    except Exception:
        p = {}
    viewer.set_shape(s, p)


button(left3, "HITUNG 3D", lambda: safe_calc(calc3, res3)).pack(
    fill="x", padx=18, pady=4
)
button(left3, "TAMPILKAN 3D", update_view, bg=YELLOW, fg="#ffffff").pack(
    fill="x", padx=18, pady=4
)

tk.Label(
    right3,
    text="MODEL 3D + ANIMASI",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 16, "bold"),
).pack(anchor="w", padx=15, pady=8)
viewer = Shape3DViewer(right3)
rebuild3()

# ============================================================
# TAB BENTUK 3D TAMBAHAN
# ============================================================
tabextra = tk.Frame(tabs, bg=APP_BG)
tabs.add(tabextra, text=" 🔷 Model 3D ")

leftx = tk.Frame(tabextra, bg=CARD, width=320)
leftx.pack(side="left", fill="y", padx=(10, 5), pady=10)
leftx.pack_propagate(False)

rightx = tk.Frame(tabextra, bg=PANEL)
rightx.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

tk.Label(
    leftx, text="BENTUK 3D", bg=CARD, fg=TEXT, font=("Segoe UI", 17, "bold")
).pack(pady=20)

extra = ttk.Combobox(
    leftx,
    state="readonly",
    width=25,
    values=[
        "Kubus",
        "Balok",
        "Tabung",
        "Bola",
        "Kerucut",
        "Limas Segiempat",
        "Prisma Segitiga",
    ],
)
extra.current(0)
extra.pack(pady=10)


def show_extra():
    viewer_extra.set_shape(extra.get(), {})


show_extra_btn = button(leftx, "TAMPILKAN & ANIMASIKAN", show_extra)
show_extra_btn.pack(fill="x", padx=20, pady=10)

tk.Label(
    leftx,
    text=(
        "Semua model dapat diputar otomatis.\nGunakan mouse untuk memutar"
        " model\ndan scroll untuk memperbesar."
    ),
    bg=CARD,
    fg=MUTED,
    justify="left",
    font=("Segoe UI", 10),
).pack(anchor="w", padx=20, pady=15)

tk.Label(
    rightx,
    text="GALERI MODEL 3D",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 16, "bold"),
).pack(anchor="w", padx=15, pady=8)
viewer_extra = Shape3DViewer(rightx)
show_extra()

# ============================================================
# TAB RUMUS
# ============================================================
tabrumus = tk.Frame(tabs, bg=PANEL)
tabs.add(tabrumus, text=" 📚 Kumpulan Rumus ")

rumus_text = """
RUMUS GEOMETRI

2D
- Persegi        : L = s²                    | K = 4s
- Persegi panjang: L = p × l                 | K = 2(p+l)
- Segitiga       : L = ½ × a × t
- Lingkaran      : L = πr²                   | K = 2πr

3D
- Kubus          : V = s³                    | LP = 6s²
- Balok          : V = p × l × t             | LP = 2(pl+pt+lt)
- Tabung         : V = πr²t
- Bola           : V = ⁴⁄₃πr³                | LP = 4πr²
- Kerucut        : V = ⅓πr²t

Keterangan:
L = luas, K = keliling, V = volume,
LP = luas permukaan, s = sisi, p = panjang,
l = lebar, t = tinggi, a = alas, r = jari-jari.
π digunakan sekitar 3,141592653589793.
"""

tk.Label(
    tabrumus,
    text=rumus_text,
    bg=PANEL,
    fg=TEXT,
    justify="left",
    font=("Consolas", 12),
).pack(anchor="w", padx=40, pady=25)

# ============================================================
# TAB PETUNJUK
# ============================================================
tababout = tk.Frame(tabs, bg=PANEL)
tabs.add(tababout, text=" ℹ Petunjuk ")

tk.Label(
    tababout,
    text="KALKULATOR GEOMETRI",
    bg=PANEL,
    fg=ACCENT,
    font=("Segoe UI", 28, "bold"),
).pack(pady=(45, 10))

about = (
    "Aplikasi kalkulator geometri berbasis Python + Tkinter untuk"
    " pembelajaran.\n\nCara menggunakan:\n1. Pilih menu 2D atau 3D.\n2. Pilih"
    " jenis bangun.\n3. Masukkan ukuran sesuai kolom.\n4. Tekan HITUNG untuk"
    " melihat hasil.\n5. Pada menu 3D, bentuk akan tampil dan berputar"
    " otomatis.\n6. Drag model dengan mouse untuk melihat sisi lain.\n7. Scroll"
    " mouse untuk zoom.\n\nCatatan: ukuran model 3D divisualisasikan secara"
    " proporsional.\nNilai volume dan luas permukaan dihitung menggunakan"
    " rumus\nmatematika, bukan berdasarkan ukuran gambar di layar."
)
tk.Label(
    tababout, text=about, bg=PANEL, fg=TEXT, justify="left", font=("Segoe UI", 12)
).pack(anchor="w", padx=80)

# ============================================================
# TAB TENTANG / KELOMPOK (BARU)
# ============================================================
tabkelompok = tk.Frame(tabs, bg=PANEL)
tabs.add(tabkelompok, text=" 👥 Tentang Kelompok ")

tk.Label(
    tabkelompok,
    text="TENTANG KELOMPOK",
    bg=PANEL,
    fg=ACCENT,
    font=("Segoe UI", 28, "bold"),
).pack(pady=(45, 15))

# Frame untuk daftar anggota kelompok
frame_anggota = tk.Frame(tabkelompok, bg=CARD, padx=20, pady=20)
frame_anggota.pack(padx=80, anchor="w", fill="x")

tk.Label(
    frame_anggota,
    text="Anggota Kelompok:",
    bg=CARD,
    fg=TEXT,
    font=("Segoe UI", 14, "bold"),
).pack(anchor="w", pady=(0, 10))

# Silakan ubah nama-nama di bawah ini sesuai dengan anggota kelompok Anda
daftar_nama = [
    "1. Muhammad David Aldiansyah (03)",
    "2. muhammad danang pratama (04)",
    "3. Muhammad dendi setiawan (05)",
    "4. M.izzul Haq ramadhan (07)",
    "5. Muhammad niko bimantoro (08)",
    "6. Muahammad Ulul al-bab isomudin(10)",
    "7. Riska Rahmawati putri muda'i rumagoran (28)",
    "8. Sandy mayesa (32)",
    "9. Vitalia Ayu Marisa (40)",
    "10.Wulan fahma arie anggraini (41)",
   
]

for nama in daftar_nama:
    tk.Label(
        frame_anggota,
        text=nama,
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 12),
    ).pack(anchor="w", pady=2)

# ============================================================
# FOOTER
# ============================================================
tk.Label(
    root,
    text="Kalkulator Geometri • Python Tkinter • Untuk pembelajaran",
    bg=APP_BG,
    fg=MUTED,
    font=("Segoe UI", 9),
).pack(pady=(0, 5))

root.mainloop()
