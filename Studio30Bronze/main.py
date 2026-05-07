import flet as ft
import sqlite3
import os
import webbrowser

SESSION_FILE = "session.txt"

# ══════════════════════════════════════════════
#  PALETA DE CULORI
# ══════════════════════════════════════════════
BG_DEEP       = "#0D1F1B"
BG_CARD       = "#162921"
BG_INPUT      = "#1E3830"
GOLD_BRIGHT   = "#E8C840"
GOLD_SOFT     = "#C9A227"
GOLD_DIM      = "#7A6010"
TEAL_ACCENT   = "#00BFA5"
TEXT_WHITE    = "#F0EDE6"
TEXT_MUTED    = "#8A9E99"
DANGER        = "#E57373"

# Culori cadru telefon
PHONE_OUTER   = "#1A1A1A"
PHONE_INNER   = "#111111"
PHONE_SCREEN  = "#000000"
PHONE_BTN     = "#2A2A2A"
PHONE_BTN_HL  = "#333333"


def with_opacity(hex_color: str, opacity: float) -> str:
    hex_color = hex_color.lstrip("#")
    alpha = int(opacity * 255)
    return f"#{alpha:02X}{hex_color}"


GOLD_OVR_08   = with_opacity(GOLD_BRIGHT, 0.08)
GOLD_OVR_12   = with_opacity(GOLD_BRIGHT, 0.12)
GOLD_OVR_15   = with_opacity(GOLD_BRIGHT, 0.15)
GOLD_OVR_20   = with_opacity(GOLD_BRIGHT, 0.20)
TEAL_OVR_12   = with_opacity(TEAL_ACCENT, 0.12)
TEAL_OVR_15   = with_opacity(TEAL_ACCENT, 0.15)
TEAL_OVR_40   = with_opacity(TEAL_ACCENT, 0.40)
TEAL_OVR_50   = with_opacity(TEAL_ACCENT, 0.50)
DANGER_OVR_12 = with_opacity(DANGER, 0.12)
DANGER_OVR_15 = with_opacity(DANGER, 0.15)
DANGER_OVR_40 = with_opacity(DANGER, 0.40)
DANGER_OVR_50 = with_opacity(DANGER, 0.50)
MUTED_OVR_40  = with_opacity(TEXT_MUTED, 0.40)


def init_db():
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS utilizatori 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nume TEXT, email TEXT UNIQUE, telefon TEXT, 
                    parola TEXT, abonament TEXT DEFAULT 'Niciunul',
                    minute INTEGER DEFAULT 0)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS prezente
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    locatie TEXT,
                    checkin_time TEXT)''')
    conn.commit()
    conn.close()


def db_checkin(user_id, locatie):
    from datetime import datetime
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO prezente (user_id, locatie, checkin_time) VALUES (?, ?, ?)",
        (user_id, locatie, datetime.now().strftime("%H:%M"))
    )
    conn.commit()
    conn.close()


def db_checkout(user_id):
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM prezente WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def db_get_prezenta_user(user_id):
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("SELECT locatie FROM prezente WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def db_get_ocupare():
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("SELECT locatie, COUNT(*) FROM prezente GROUP BY locatie")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def save_session(user_id):
    with open(SESSION_FILE, "w") as f:
        f.write(str(user_id))


def get_saved_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return f.read().strip()
    return None


def delete_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


# ══════════════════════════════════════════════
#  COMPONENTE REUTILIZABILE
# ══════════════════════════════════════════════

def gold_divider():
    return ft.Container(
        height=1, width=260, bgcolor=GOLD_DIM,
        margin=ft.margin.symmetric(vertical=8),
    )


def section_title(text: str):
    return ft.Text(text, size=11, color=GOLD_BRIGHT, weight="bold")


def styled_field(label: str, password: bool = False) -> ft.TextField:
    return ft.TextField(
        label=label, password=password,
        label_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=14),
        border_color=GOLD_DIM, focused_border_color=GOLD_BRIGHT,
        cursor_color=GOLD_BRIGHT, bgcolor=BG_INPUT, border_radius=12,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )


def primary_button(text: str, on_click) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text, on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=GOLD_BRIGHT, color=BG_DEEP, overlay_color=GOLD_SOFT,
            shape=ft.RoundedRectangleBorder(radius=14),
            padding=ft.padding.symmetric(horizontal=40, vertical=16),
            text_style=ft.TextStyle(size=13, weight="bold"),
        ),
    )


def ghost_button(text: str, on_click) -> ft.TextButton:
    return ft.TextButton(
        text, on_click=on_click,
        style=ft.ButtonStyle(
            color=TEXT_MUTED, overlay_color=GOLD_OVR_08,
            text_style=ft.TextStyle(size=12),
        ),
    )


def logo_block(subtitle: str = "BRONZARE PROFESIONALĂ") -> ft.Column:
    sun = ft.Stack(
        controls=[
            ft.Container(width=80, height=80, border_radius=40,
                         border=ft.border.all(2, GOLD_DIM)),
            ft.Container(
                width=64, height=64, border_radius=32,
                bgcolor=GOLD_OVR_15, margin=8,
                content=ft.Icon(ft.Icons.WB_SUNNY_ROUNDED, color=GOLD_BRIGHT, size=36),
                alignment=ft.Alignment(0, 0),
            ),
        ],
        width=80, height=80,
    )
    return ft.Column(
        [
            sun,
            ft.Container(height=10),
            ft.Text("STUDIO", size=28, color=GOLD_BRIGHT, weight="bold"),
            ft.Row(
                [
                    ft.Container(width=30, height=1, bgcolor=GOLD_DIM),
                    ft.Text("30", size=40, color=TEXT_WHITE, weight="bold"),
                    ft.Container(width=30, height=1, bgcolor=GOLD_DIM),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            ft.Text(subtitle, size=9, color=TEXT_MUTED),
        ],
        horizontal_alignment=ft.MainAxisAlignment.CENTER,
        spacing=2,
    )


def stat_pill(label: str, value: str, icon) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, color=GOLD_BRIGHT, size=20),
                ft.Column(
                    [
                        ft.Text(value, size=16, color=TEXT_WHITE, weight="bold"),
                        ft.Text(label, size=10, color=TEXT_MUTED),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        bgcolor=BG_CARD,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        border_radius=14,
        border=ft.border.all(1, GOLD_DIM),
        expand=True,
    )


def only_digits_spaces(e, field, max_len=None):
    val = "".join(c for c in e.control.value if c.isdigit() or c == " ")
    if max_len:
        val = val[:max_len]
    field.value = val
    field.update()


def only_digits_slash(e, field, max_len=None):
    val = "".join(c for c in e.control.value if c.isdigit() or c == "/")
    if max_len:
        val = val[:max_len]
    field.value = val
    field.update()


def only_digits(e, field, max_len=None):
    val = "".join(c for c in e.control.value if c.isdigit())
    if max_len:
        val = val[:max_len]
    field.value = val
    field.update()


def only_letters_spaces(e, field):
    val = "".join(c for c in e.control.value if not c.isdigit())
    field.value = val
    field.update()


# ══════════════════════════════════════════════
#  APLICATIA PRINCIPALA
# ══════════════════════════════════════════════

def main(page: ft.Page):
    # ── Dimensiunea ferestrei = cadru telefon + conținut ──
    PHONE_W = 430   # lățimea totală a ferestrei (include cadrul)
    PHONE_H = 870   # înălțimea totală a ferestrei
    SCREEN_W = 390  # ecranul propriu-zis
    SCREEN_H = 720  # ecranul propriu-zis

    page.window_width       = PHONE_W
    page.window_height      = PHONE_H
    page.window_resizable   = False
    page.window_maximizable = False
    page.adaptive  = True
    page.padding   = 0
    page.spacing   = 0
    page.bgcolor   = "#1C1C1E"   # fundal exterior gri închis
    page.title     = "Studio 30 Bronze"

    init_db()

    saved_id = get_saved_session()
    state = {"user_id": saved_id}

    # ── Zona de conținut scrollabilă (ecranul virtual) ──
    scroll_view = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.MainAxisAlignment.CENTER,
    )

    screen_content = ft.Container(
        content=scroll_view,
        expand=True,
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        bgcolor=BG_DEEP,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    # ── Navigation bar (în interiorul ecranului) ──
    nav_bar_ref = ft.Ref[ft.NavigationBar]()

    def set_content(controls):
        scroll_view.controls = controls
        page.update()

    # ══════════════════════════════════════════
    #  VALIDARE EMAIL
    # ══════════════════════════════════════════

    DOMENII_ACCEPTATE = [
        "gmail.com", "yahoo.com", "yahoo.ro",
        "hotmail.com", "outlook.com", "icloud.com",
        "protonmail.com", "me.com",
    ]

    def email_valid(email_raw):
        """Returnează (True, '') sau (False, mesaj_eroare)."""
        email = (email_raw or "").strip().lower()
        if "@" not in email or email.startswith("@"):
            return False, "Emailul trebuie sa contina @ (ex: nume@gmail.com)"
        parte_locala, _, domeniu = email.partition("@")
        if not parte_locala:
            return False, "Lipseste numele inainte de @"
        if domeniu not in DOMENII_ACCEPTATE:
            return False, "Domeniu invalid. Acceptam: gmail.com, yahoo.com, outlook.com etc."
        return True, ""

    # ══════════════════════════════════════════
    #  TOATE ECRANELE
    # ══════════════════════════════════════════

    def show_login(e=None):
        nav_bar_ref.current.visible = False
        email_f = styled_field("Email")
        pass_f  = styled_field("Parola", password=True)

        def login_click(e):
            valid, eroare = email_valid(email_f.value)
            if not valid:
                email_f.error_text = eroare
                email_f.update()
                return
            email_f.error_text = None
            email_f.update()

            conn = sqlite3.connect("studio30.db")
            cur  = conn.cursor()
            cur.execute("SELECT id FROM utilizatori WHERE email=? AND parola=?",
                        (email_f.value.strip().lower(), pass_f.value))
            user = cur.fetchone()
            conn.close()
            if user:
                save_session(user[0])
                state["user_id"] = user[0]
                nav_bar_ref.current.visible = True
                nav_bar_ref.current.selected_index = 0
                show_home()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Date incorecte!"))
                page.snack_bar.open = True
                page.update()

        set_content([
            ft.Container(height=30),
            logo_block(),
            ft.Container(height=36),
            section_title("AUTENTIFICARE"),
            ft.Container(height=14),
            email_f, ft.Container(height=10), pass_f,
            ft.Container(height=22),
            primary_button("INTRA IN CONT", login_click),
            ft.Container(height=10),
            gold_divider(),
            ghost_button("Nu ai cont? Inregistreaza-te ->", show_register),
            ft.Container(height=20),
        ])

    def show_register(e=None):
        nav_bar_ref.current.visible = False
        nume   = styled_field("Nume complet")
        email  = styled_field("Email")
        tel    = styled_field("Telefon")
        parola = styled_field("Parola", password=True)

        def reg_click(e):
            eroare_gasita = False

            if not (nume.value or "").strip():
                nume.error_text = "Numele este obligatoriu"
                eroare_gasita = True
            else:
                nume.error_text = None

            valid, eroare_email = email_valid(email.value)
            if not valid:
                email.error_text = eroare_email
                eroare_gasita = True
            else:
                email.error_text = None

            if not (tel.value or "").strip():
                tel.error_text = "Telefonul este obligatoriu"
                eroare_gasita = True
            else:
                tel.error_text = None

            if not parola.value or len(parola.value) < 6:
                parola.error_text = "Parola trebuie sa aiba minim 6 caractere"
                eroare_gasita = True
            else:
                parola.error_text = None

            nume.update(); email.update(); tel.update(); parola.update()

            if eroare_gasita:
                return

            try:
                conn = sqlite3.connect("studio30.db")
                cur  = conn.cursor()
                cur.execute(
                    "INSERT INTO utilizatori (nume, email, telefon, parola) VALUES (?,?,?,?)",
                    (nume.value.strip(), email.value.strip().lower(),
                     tel.value.strip(), parola.value)
                )
                conn.commit()
                conn.close()
                show_login()
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("Email deja inregistrat!"))
                page.snack_bar.open = True
                page.update()

        set_content([
            ft.Container(height=20),
            logo_block("CONT NOU"),
            ft.Container(height=28),
            section_title("DETALII PERSONALE"),
            ft.Container(height=14),
            nume,   ft.Container(height=10),
            email,  ft.Container(height=10),
            tel,    ft.Container(height=10),
            parola, ft.Container(height=22),
            primary_button("CREEAZA CONT", reg_click),
            ft.Container(height=8),
            ghost_button("<- Inapoi la login", show_login),
            ft.Container(height=20),
        ])

    def show_home():
        tip_cards = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.THERMOSTAT_ROUNDED, color=GOLD_BRIGHT, size=28),
                            ft.Container(height=6),
                            ft.Text("BRONZARE", size=10, color=GOLD_BRIGHT, weight="bold"),
                            ft.Text("UVA + UVB", size=12, color=TEXT_WHITE),
                        ],
                        horizontal_alignment=ft.MainAxisAlignment.CENTER, spacing=2,
                    ),
                    bgcolor=BG_CARD, padding=16, border_radius=14,
                    border=ft.border.all(1, GOLD_DIM),
                    expand=True, alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SPA_ROUNDED, color=TEAL_ACCENT, size=28),
                            ft.Container(height=6),
                            ft.Text("COLLAGEN", size=10, color=TEAL_ACCENT, weight="bold"),
                            ft.Text("Rejuvenare", size=12, color=TEXT_WHITE),
                        ],
                        horizontal_alignment=ft.MainAxisAlignment.CENTER, spacing=2,
                    ),
                    bgcolor=BG_CARD, padding=16, border_radius=14,
                    border=ft.border.all(1, TEAL_OVR_40),
                    expand=True, alignment=ft.Alignment(0, 0),
                ),
            ],
            spacing=12,
        )

        set_content([
            ft.Container(height=10),
            logo_block("CRAIOVA"),
            ft.Container(height=28),
            gold_divider(),
            ft.Container(height=16),
            section_title("SERVICII"),
            ft.Container(height=12),
            tip_cards,
            ft.Container(height=20),
            section_title("DE CE NOI?"),
            ft.Container(height=12),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([ft.Icon(ft.Icons.STAR_ROUNDED, color=GOLD_BRIGHT, size=16),
                                ft.Text("Echipamente premium de ultima generatie",
                                        size=12, color=TEXT_WHITE)], spacing=8),
                        ft.Row([ft.Icon(ft.Icons.STAR_ROUNDED, color=GOLD_BRIGHT, size=16),
                                ft.Text("Personal calificat si prietenos",
                                        size=12, color=TEXT_WHITE)], spacing=8),
                        ft.Row([ft.Icon(ft.Icons.STAR_ROUNDED, color=GOLD_BRIGHT, size=16),
                                ft.Text("3 saloane in Craiova",
                                        size=12, color=TEXT_WHITE)], spacing=8),
                    ],
                    spacing=10,
                ),
                bgcolor=BG_CARD, padding=18, border_radius=14,
                border=ft.border.all(1, GOLD_DIM),
            ),
            ft.Container(height=30),
        ])

    def show_profile():
        conn = sqlite3.connect("studio30.db")
        cur  = conn.cursor()
        cur.execute("SELECT nume, abonament, minute FROM utilizatori WHERE id=?",
                    (state["user_id"],))
        user = cur.fetchone()
        conn.close()

        if user is None:
            delete_session()
            show_login()
            return

        initials = user[0][:2].upper() if user[0] else "??"
        avatar = ft.Container(
            content=ft.Text(initials, size=28, color=BG_DEEP, weight="bold"),
            width=72, height=72, border_radius=36,
            bgcolor=GOLD_BRIGHT, alignment=ft.Alignment(0, 0),
        )

        set_content([
            ft.Container(height=16),
            ft.Column([avatar], horizontal_alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Text(user[0], size=20, color=TEXT_WHITE, weight="bold",
                    text_align="center"),
            ft.Container(height=4),
            ft.Container(
                content=ft.Text(f"+ {user[1]}", size=11, color=BG_DEEP, weight="bold"),
                bgcolor=GOLD_BRIGHT,
                padding=ft.padding.symmetric(horizontal=14, vertical=4),
                border_radius=20,
            ),
            ft.Container(height=24),
            gold_divider(),
            ft.Container(height=16),
            section_title("STATISTICI"),
            ft.Container(height=12),
            ft.Row(
                [
                    stat_pill("MINUTE", str(user[2]), ft.Icons.TIMER_ROUNDED),
                    stat_pill("STATUS", "ACTIV", ft.Icons.VERIFIED_ROUNDED),
                ],
                spacing=10,
            ),
            ft.Container(height=28),
            gold_divider(),
            ft.Container(height=16),
            ft.ElevatedButton(
                "DECONECTARE",
                icon=ft.Icons.LOGOUT_ROUNDED,
                on_click=lambda _: (db_checkout(state["user_id"]),
                                    delete_session(), show_login()),
                style=ft.ButtonStyle(
                    bgcolor=DANGER_OVR_12, color=DANGER,
                    side=ft.BorderSide(1, DANGER_OVR_40),
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.padding.symmetric(horizontal=30, vertical=14),
                    text_style=ft.TextStyle(size=12, weight="bold"),
                ),
            ),
            ft.Container(height=30),
        ])

    def show_subscriptions():
        pay_state = {"metoda": None}

        def show_payment_ui():
            metoda = pay_state["metoda"]

            def method_card(icon, titlu, descriere, valoare, accent):
                selectat     = (metoda == valoare)
                icon_bg      = accent if selectat else with_opacity(accent, 0.12)
                icon_color   = BG_DEEP if selectat else accent
                border_col   = accent if selectat else MUTED_OVR_40
                check_bg     = accent if selectat else with_opacity(BG_CARD, 0.0)

                return ft.GestureDetector(
                    on_tap=lambda _: select_metoda(valoare),
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(icon, color=icon_color, size=22),
                                    bgcolor=icon_bg, width=44, height=44,
                                    border_radius=12, alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(
                                    [
                                        ft.Text(titlu, size=13, color=TEXT_WHITE, weight="bold"),
                                        ft.Text(descriere, size=10, color=TEXT_MUTED),
                                    ],
                                    spacing=2, expand=True,
                                ),
                                ft.Container(
                                    width=20, height=20, border_radius=10,
                                    bgcolor=check_bg,
                                    border=ft.border.all(2, border_col),
                                    content=ft.Icon(ft.Icons.CHECK_ROUNDED,
                                                    color=BG_DEEP, size=12,
                                                    ) if selectat else None,
                                    alignment=ft.Alignment(0, 0),
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=BG_CARD,
                        padding=ft.padding.symmetric(horizontal=16, vertical=14),
                        border_radius=14,
                        border=ft.border.all(2 if selectat else 1, border_col),
                    ),
                )

            def select_metoda(val):
                pay_state["metoda"] = val
                show_payment_ui()

            card_form = []
            if metoda == "card":
                nr_card = ft.TextField(
                    label="Numar card",
                    label_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
                    border_color=GOLD_DIM, focused_border_color=GOLD_BRIGHT,
                    cursor_color=GOLD_BRIGHT, bgcolor=BG_INPUT, border_radius=12,
                    content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="1234 5678 9012 3456",
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    max_length=19,
                )
                nr_card.on_change = lambda e: only_digits_spaces(e, nr_card, max_len=19)

                expiry = ft.TextField(
                    label="Exp. (LL/AA)",
                    label_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
                    border_color=GOLD_DIM, focused_border_color=GOLD_BRIGHT,
                    cursor_color=GOLD_BRIGHT, bgcolor=BG_INPUT, border_radius=12,
                    content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="12/27",
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    expand=True, max_length=5,
                )
                expiry.on_change = lambda e: only_digits_slash(e, expiry, max_len=5)

                cvv = ft.TextField(
                    label="CVV",
                    label_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
                    border_color=GOLD_DIM, focused_border_color=GOLD_BRIGHT,
                    cursor_color=GOLD_BRIGHT, bgcolor=BG_INPUT, border_radius=12,
                    content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    password=True,
                    hint_text="***",
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    expand=True, max_length=4,
                )
                cvv.on_change = lambda e: only_digits(e, cvv, max_len=4)

                titular = ft.TextField(
                    label="Titular card",
                    label_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
                    border_color=GOLD_DIM, focused_border_color=GOLD_BRIGHT,
                    cursor_color=GOLD_BRIGHT, bgcolor=BG_INPUT, border_radius=12,
                    content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    hint_text="PRENUME NUME",
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                    capitalization=ft.TextCapitalization.CHARACTERS,
                )
                titular.on_change = lambda e: only_letters_spaces(e, titular)

                card_form = [
                    ft.Container(height=4),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CREDIT_CARD_ROUNDED,
                                                color=GOLD_BRIGHT, size=16),
                                        ft.Text("DATE CARD", size=10,
                                                color=GOLD_BRIGHT, weight="bold"),
                                        ft.Container(expand=True),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.LOCK_ROUNDED,
                                                        color=TEXT_MUTED, size=12),
                                                ft.Text("Securizat SSL",
                                                        size=10, color=TEXT_MUTED),
                                            ],
                                            spacing=4,
                                        ),
                                    ],
                                    spacing=6,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Container(height=12),
                                nr_card,
                                ft.Container(height=8),
                                titular,
                                ft.Container(height=8),
                                ft.Row([expiry, ft.Container(width=10), cvv]),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.SHIELD_ROUNDED,
                                                    color=TEAL_ACCENT, size=13),
                                            ft.Text(
                                                "Datele cardului sunt criptate si "
                                                "procesate securizat. Nu sunt stocate.",
                                                size=10, color=TEXT_MUTED,
                                            ),
                                        ],
                                        spacing=6,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                    ),
                                    bgcolor=with_opacity(TEAL_ACCENT, 0.06),
                                    padding=10, border_radius=10,
                                    border=ft.border.all(1, TEAL_OVR_40),
                                ),
                            ],
                            spacing=0,
                        ),
                        bgcolor=with_opacity(GOLD_BRIGHT, 0.04),
                        padding=16, border_radius=14,
                        border=ft.border.all(1, with_opacity(GOLD_BRIGHT, 0.2)),
                    ),
                ]

            def make_package(name, minutes, price, is_premium, accent):
                badge_text = "+ POPULAR" if is_premium else "STARTER"
                disabled   = (pay_state["metoda"] is None)
                btn_bg     = accent if not disabled else with_opacity(accent, 0.3)
                brd_op     = 0.5 if not disabled else 0.2

                def on_buy(_):
                    if pay_state["metoda"] is None:
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Selecteaza mai intai metoda de plata!")
                        )
                        page.snack_bar.open = True
                        page.update()
                        return

                    conn = sqlite3.connect("studio30.db")
                    cur  = conn.cursor()
                    cur.execute(
                        "UPDATE utilizatori SET abonament=?, minute=? WHERE id=?",
                        (name, minutes, state["user_id"])
                    )
                    conn.commit()
                    conn.close()

                    metoda_text = ("card online" if pay_state["metoda"] == "card"
                                   else "plata la salon")
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Abonament {name} activat! Plata: {metoda_text}."),
                        duration=3000,
                    )
                    page.snack_bar.open = True
                    nav_bar_ref.current.selected_index = 1
                    show_profile()

                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(name, size=16, color=TEXT_WHITE, weight="bold"),
                                    ft.Container(
                                        content=ft.Text(badge_text, size=9,
                                                        color=BG_DEEP, weight="bold"),
                                        bgcolor=accent,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=20,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(height=6),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.TIMER_OUTLINED, color=accent, size=16),
                                    ft.Text(f"{minutes} minute incluse",
                                            size=12, color=TEXT_MUTED),
                                ],
                                spacing=6,
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.PAYMENTS_OUTLINED, color=accent, size=16),
                                    ft.Text("3 LEI / minut suplimentar",
                                            size=12, color=TEXT_MUTED),
                                ],
                                spacing=6,
                            ),
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.Text(price, size=26, color=accent, weight="bold"),
                                    ft.Container(expand=True),
                                    ft.ElevatedButton(
                                        "CUMPARA",
                                        on_click=on_buy,
                                        disabled=disabled,
                                        style=ft.ButtonStyle(
                                            bgcolor=btn_bg, color=BG_DEEP,
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=ft.padding.symmetric(
                                                horizontal=20, vertical=10),
                                            text_style=ft.TextStyle(size=11, weight="bold"),
                                        ),
                                    ),
                                ],
                                vertical_alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                    ),
                    bgcolor=BG_CARD, padding=20, border_radius=16,
                    border=ft.border.all(1, with_opacity(accent, brd_op)),
                    width=340,
                )

            nota = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=TEXT_MUTED, size=16),
                        ft.Text("Minutele sunt valabile 30 de zile de la achizitie.",
                                size=11, color=TEXT_MUTED),
                    ],
                    spacing=8,
                ),
                bgcolor=BG_CARD, padding=14, border_radius=12,
            )

            set_content([
                ft.Container(height=10),
                section_title("PACHETE & PRETURI"),
                ft.Container(height=6),
                ft.Text("Alege abonamentul potrivit pentru tine",
                        size=13, color=TEXT_MUTED),
                ft.Container(height=20),
                section_title("METODA DE PLATA"),
                ft.Container(height=10),
                method_card(ft.Icons.STORE_ROUNDED, "Plata la salon",
                            "Achita abonamentul direct la receptie", "salon", TEAL_ACCENT),
                ft.Container(height=8),
                method_card(ft.Icons.CREDIT_CARD_ROUNDED, "Card online",
                            "Plata securizata cu cardul, de acasa", "card", GOLD_BRIGHT),
                *card_form,
                ft.Container(height=20),
                section_title("ALEGE PACHETUL"),
                ft.Container(height=12),
                make_package("BRONZE", 60, "99 RON", False, TEAL_ACCENT),
                ft.Container(height=12),
                make_package("GOLD",   90, "179 RON", True,  GOLD_BRIGHT),
                ft.Container(height=20),
                nota,
                ft.Container(height=30),
            ])

        show_payment_ui()

    SALOANE = [
        ("Salon 1 Mai",         "Str. Unirii nr.160"),
        ("Salon George Enescu", "Str. George Enescu nr.60"),
        ("Salon Rovine",        "Str. Campului nr.13"),
    ]

    def show_locations():
        ocupare          = db_get_ocupare()
        prezenta_curenta = db_get_prezenta_user(state["user_id"])
        cards = []

        for name, addr in SALOANE:
            count     = ocupare.get(name, 0)
            este_aici = (prezenta_curenta == name)

            if count == 0:
                dot_color    = TEAL_ACCENT
                ocupare_text = "Liber"
            elif count <= 2:
                dot_color    = GOLD_BRIGHT
                ocupare_text = f"{count} {'client' if count == 1 else 'clienti'}"
            else:
                dot_color    = DANGER
                ocupare_text = f"{count} clienti"

            btn_bg   = DANGER_OVR_15 if este_aici else TEAL_OVR_15
            btn_col  = DANGER if este_aici else TEAL_ACCENT
            btn_side = DANGER_OVR_50 if este_aici else TEAL_OVR_50
            brd_col  = TEAL_ACCENT if este_aici else GOLD_DIM

            def make_checkin_handler(salon_name):
                def handler(_):
                    if db_get_prezenta_user(state["user_id"]) == salon_name:
                        db_checkout(state["user_id"])
                    else:
                        db_checkin(state["user_id"], salon_name)
                    show_locations()
                return handler

            url  = f"https://www.google.com/maps/search/{addr}+Craiova"
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.LOCATION_ON_ROUNDED,
                                                    color=BG_DEEP, size=18),
                                    bgcolor=GOLD_BRIGHT, width=36, height=36,
                                    border_radius=10, alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(
                                    [
                                        ft.Text(name, size=14, color=TEXT_WHITE, weight="bold"),
                                        ft.Text(addr, size=11, color=TEXT_MUTED),
                                    ],
                                    spacing=1, expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                                    icon_color=GOLD_BRIGHT, icon_size=18,
                                    on_click=lambda _, u=url: webbrowser.open(u),
                                    tooltip="Deschide in Maps",
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=10),
                        ft.Container(height=1, bgcolor=GOLD_DIM),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Container(width=8, height=8,
                                                     border_radius=4, bgcolor=dot_color),
                                        ft.Text(ocupare_text, size=12, color=dot_color),
                                    ],
                                    spacing=6,
                                ),
                                ft.ElevatedButton(
                                    "CHECK-OUT" if este_aici else "CHECK-IN",
                                    icon=(ft.Icons.LOGOUT_ROUNDED if este_aici
                                          else ft.Icons.LOGIN_ROUNDED),
                                    on_click=make_checkin_handler(name),
                                    style=ft.ButtonStyle(
                                        bgcolor=btn_bg, color=btn_col,
                                        side=ft.BorderSide(1, btn_side),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.padding.symmetric(
                                            horizontal=14, vertical=8),
                                        text_style=ft.TextStyle(size=11, weight="bold"),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                ),
                bgcolor=BG_CARD, padding=16, border_radius=16,
                border=ft.border.all(2 if este_aici else 1, brd_col),
                width=340,
            )
            cards.append(card)
            cards.append(ft.Container(height=10))

        nota = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=TEXT_MUTED, size=14),
                    ft.Text("Ocuparea se actualizeaza live la fiecare cateva secunde.",
                            size=11, color=TEXT_MUTED),
                ],
                spacing=8,
            ),
            bgcolor=BG_CARD, padding=12, border_radius=10,
        )

        set_content([
            ft.Container(height=10),
            section_title("LOCATIILE NOASTRE"),
            ft.Container(height=6),
            ft.Text("3 saloane in Craiova", size=13, color=TEXT_MUTED),
            ft.Container(height=20),
            *cards,
            nota,
            ft.Container(height=30),
        ])

    # ── Navigation bar ────────────────────────
    def on_nav(e):
        idx = int(e.data)
        [show_home, show_profile, show_subscriptions, show_locations][idx]()

    nav_bar = ft.NavigationBar(
        ref=nav_bar_ref,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,
                                        selected_icon=ft.Icons.HOME_ROUNDED,
                                        label="Acasa"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
                                        selected_icon=ft.Icons.PERSON_ROUNDED,
                                        label="Profil"),
            ft.NavigationBarDestination(icon=ft.Icons.CARD_MEMBERSHIP_OUTLINED,
                                        selected_icon=ft.Icons.CARD_MEMBERSHIP,
                                        label="Pachete"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCATION_ON_OUTLINED,
                                        selected_icon=ft.Icons.LOCATION_ON_ROUNDED,
                                        label="Locatii"),
        ],
        bgcolor=BG_CARD,
        indicator_color=GOLD_OVR_20,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        on_change=on_nav,
        visible=False,
    )

    # ══════════════════════════════════════════
    #  CADRUL DE TELEFON
    # ══════════════════════════════════════════

    # Status bar (sus, în ecran)
    import datetime
    ora = datetime.datetime.now().strftime("%H:%M")

    status_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text(ora, size=12, color=TEXT_WHITE, weight="bold"),
                ft.Container(expand=True),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SIGNAL_CELLULAR_ALT, color=TEXT_WHITE, size=14),
                        ft.Icon(ft.Icons.WIFI, color=TEXT_WHITE, size=14),
                        ft.Icon(ft.Icons.BATTERY_FULL, color=TEXT_WHITE, size=14),
                    ],
                    spacing=4,
                ),
            ],
        ),
        bgcolor=BG_DEEP,
        padding=ft.padding.symmetric(horizontal=20, vertical=6),
        height=28,
    )

    # Dynamic island / notch
    dynamic_island = ft.Container(
        content=ft.Row(
            [
                ft.Container(width=8, height=8, border_radius=4, bgcolor="#111111"),
                ft.Container(width=40, height=8, border_radius=4, bgcolor="#111111"),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=PHONE_INNER,
        height=20,
        alignment=ft.Alignment(0, 0),
    )

    # Ecranul virtual (conținut + nav)
    virtual_screen = ft.Container(
        content=ft.Column(
            [
                status_bar,
                dynamic_island,
                screen_content,
                nav_bar,
            ],
            spacing=0,
            expand=True,
        ),
        width=SCREEN_W,
        height=SCREEN_H,
        bgcolor=BG_DEEP,
        border_radius=ft.border_radius.all(40),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.border.all(2, "#333333"),
    )

    # Butoane laterale stânga (volum)
    btn_vol_up = ft.Container(
        width=4, height=40,
        bgcolor=PHONE_BTN_HL,
        border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
    )
    btn_vol_down = ft.Container(
        width=4, height=40,
        bgcolor=PHONE_BTN_HL,
        border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
    )
    btn_silent = ft.Container(
        width=4, height=28,
        bgcolor=PHONE_BTN_HL,
        border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
    )

    left_buttons = ft.Column(
        [
            ft.Container(height=80),
            btn_silent,
            ft.Container(height=12),
            btn_vol_up,
            ft.Container(height=10),
            btn_vol_down,
        ],
        spacing=0,
    )

    # Buton lateral dreapta (power)
    btn_power = ft.Container(
        width=4, height=60,
        bgcolor=PHONE_BTN_HL,
        border_radius=ft.border_radius.only(top_right=3, bottom_right=3),
    )

    right_buttons = ft.Column(
        [
            ft.Container(height=100),
            btn_power,
        ],
        spacing=0,
    )

    # Indicator home (bara de jos)
    home_indicator = ft.Container(
        content=ft.Container(
            width=100, height=4,
            bgcolor="#555555",
            border_radius=2,
        ),
        alignment=ft.Alignment(0, 0),
        height=20,
        bgcolor=PHONE_INNER,
    )

    # Corpul telefonului — butoanele laterale + corpul central în Row
    phone_body = ft.Container(
        content=ft.Row(
            [
                # Butoane stânga (volum + silent)
                ft.Column(
                    [
                        ft.Container(height=80),
                        ft.Container(
                            width=4, height=28,
                            bgcolor=PHONE_BTN_HL,
                            border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
                        ),
                        ft.Container(height=12),
                        ft.Container(
                            width=4, height=40,
                            bgcolor=PHONE_BTN_HL,
                            border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            width=4, height=40,
                            bgcolor=PHONE_BTN_HL,
                            border_radius=ft.border_radius.only(top_left=3, bottom_left=3),
                        ),
                    ],
                    spacing=0,
                ),
                # Corp principal
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=10),
                            virtual_screen,
                            home_indicator,
                            ft.Container(height=8),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=PHONE_OUTER,
                    border_radius=ft.border_radius.all(44),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=10),
                ),
                # Buton dreapta (power)
                ft.Column(
                    [
                        ft.Container(height=100),
                        ft.Container(
                            width=4, height=60,
                            bgcolor=PHONE_BTN_HL,
                            border_radius=ft.border_radius.only(top_right=3, bottom_right=3),
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        width=PHONE_W,
        height=PHONE_H,
        alignment=ft.Alignment(0, 0),
        bgcolor="#0A0A0A",
    )

    page.add(phone_body)

    # ── LIVE REFRESH ──────────────────────────
    import threading

    def live_refresh():
        import time
        while True:
            time.sleep(5)
            try:
                if (nav_bar_ref.current.visible and
                        nav_bar_ref.current.selected_index == 3):
                    show_locations()
            except Exception:
                pass

    t = threading.Thread(target=live_refresh, daemon=True)
    t.start()

    if state["user_id"]:
        nav_bar_ref.current.visible = True
        show_home()
    else:
        show_login()


if __name__ == "__main__":
    ft.app(target=main)