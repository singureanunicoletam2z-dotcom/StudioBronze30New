import flet as ft
import sqlite3
import threading
import time

# ══════════════════════════════════════════════
#  ROLURI & PAROLE
# ══════════════════════════════════════════════
ROLURI = {
    "sef123":   "sef",
    "admin123": "administrator",
    "man123":   "manager",
}

ROLE_LABELS = {
    "sef":           "ȘEF",
    "administrator": "ADMINISTRATOR",
    "manager":       "MANAGER",
}

ROLE_COLORS = {
    "sef":           "#E8C840",   # auriu
    "administrator": "#00BFA5",   # turcoaz
    "manager":       "#B0BEC5",   # gri argintiu
}

# Prețuri abonamente (pentru stocul de bani)
PRET_ABONAMENT = {
    "GOLD":   179,
    "BRONZE":  99,
}

# ══════════════════════════════════════════════
#  PALETA
# ══════════════════════════════════════════════
BG_DEEP    = "#0D1F1B"
BG_CARD    = "#162921"
BG_INPUT   = "#1E3830"
GOLD_BRIGHT= "#E8C840"
GOLD_SOFT  = "#C9A227"
GOLD_DIM   = "#7A6010"
TEAL       = "#00BFA5"
TEXT_WHITE = "#F0EDE6"
TEXT_MUTED = "#8A9E99"
DANGER     = "#E57373"
SILVER     = "#B0BEC5"

SALOANE = ["Salon 1 Mai", "Salon George Enescu", "Salon Rovine"]


# ══════════════════════════════════════════════
#  DB HELPERS
# ══════════════════════════════════════════════

def db_get_clienti():
    try:
        conn = sqlite3.connect("studio30.db")
        cur = conn.cursor()
        cur.execute("SELECT id, nume, email, telefon, abonament, minute FROM utilizatori")
        date = cur.fetchall()
        conn.close()
        return date
    except Exception:
        return []


def db_get_prezente_detaliat():
    try:
        conn = sqlite3.connect("studio30.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT u.nume, p.locatie, p.checkin_time
            FROM prezente p
            JOIN utilizatori u ON p.user_id = u.id
            ORDER BY p.locatie
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def db_get_ocupare():
    try:
        conn = sqlite3.connect("studio30.db")
        cur = conn.cursor()
        cur.execute("SELECT locatie, COUNT(*) FROM prezente GROUP BY locatie")
        rows = cur.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
    except Exception:
        return {}


def db_scade_minute(id_c, val):
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("UPDATE utilizatori SET minute = MAX(0, minute - ?) WHERE id = ?", (val, id_c))
    conn.commit()
    conn.close()


def db_adauga_minute(id_c, val):
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("UPDATE utilizatori SET minute = minute + ? WHERE id = ?", (val, id_c))
    conn.commit()
    conn.close()


def db_sterge_client(id_c):
    conn = sqlite3.connect("studio30.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM utilizatori WHERE id=?", (id_c,))
    cur.execute("CREATE TABLE temp AS SELECT nume, email, telefon, parola, abonament, minute FROM utilizatori")
    cur.execute("DROP TABLE utilizatori")
    cur.execute(
        "CREATE TABLE utilizatori (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "nume TEXT, email TEXT UNIQUE, telefon TEXT, parola TEXT, "
        "abonament TEXT DEFAULT 'Niciunul', minute INTEGER DEFAULT 0)"
    )
    cur.execute("INSERT INTO utilizatori (nume, email, telefon, parola, abonament, minute) "
                "SELECT * FROM temp")
    cur.execute("DROP TABLE temp")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='utilizatori'")
    conn.commit()
    conn.close()


def db_calcul_stoc():
    """Returnează venitul total estimat din abonamente active."""
    clienti = db_get_clienti()
    total = 0
    gold_count = 0
    bronze_count = 0
    for c in clienti:
        abo = c[4] or "Niciunul"
        if abo == "GOLD":
            total += PRET_ABONAMENT["GOLD"]
            gold_count += 1
        elif abo == "BRONZE":
            total += PRET_ABONAMENT["BRONZE"]
            bronze_count += 1
    return total, gold_count, bronze_count


# ══════════════════════════════════════════════
#  COMPONENTE UI
# ══════════════════════════════════════════════

def styled_field(label="", password=False, width=300, hint="", on_submit=None):
    return ft.TextField(
        label=label if label else None,
        hint_text=hint if hint else None,
        password=password,
        can_reveal_password=password,
        label_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=GOLD_DIM,
        focused_border_color=GOLD_BRIGHT,
        cursor_color=GOLD_BRIGHT,
        bgcolor=BG_INPUT,
        border_radius=12,
        width=width,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        on_submit=on_submit,
    )


def badge(text, color):
    return ft.Container(
        content=ft.Text(text, size=10, color=BG_DEEP, weight="bold"),
        bgcolor=color,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=20,
    )


def stat_box(label, value, color, icon=None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [ft.Icon(icon, color=color, size=18)] if icon else [],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(str(value), size=24, color=color, weight="bold", text_align="center"),
                ft.Text(label, size=9, color=TEXT_MUTED, text_align="center"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=BG_CARD,
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        border_radius=14,
        border=ft.border.all(1, GOLD_DIM),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )


# ══════════════════════════════════════════════
#  APLICATIA PRINCIPALA
# ══════════════════════════════════════════════

def main(page: ft.Page):
    page.title = "Admin — Studio 30 Bronze"
    page.window_width  = 1060
    page.window_height = 720
    page.window_resizable = False
    page.bgcolor = BG_DEEP
    page.padding = 0
    page.spacing = 0

    state = {"rol": None, "in_panel": False}

    # ══════════════════════════════════════════
    #  ECRAN SELECTARE ROL
    # ══════════════════════════════════════════
    def show_role_select(e=None):
        state["rol"] = None
        state["in_panel"] = False
        page.vertical_alignment   = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.controls.clear()

        def choose(rol):
            show_login(rol)

        roles_ui = [
            # ȘEF
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WORKSPACE_PREMIUM_ROUNDED,
                                            color=BG_DEEP, size=30),
                            bgcolor=GOLD_BRIGHT,
                            width=60, height=60,
                            border_radius=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text("ȘEF", size=16, color=GOLD_BRIGHT, weight="bold"),
                        ft.Container(height=4),
                        ft.Text("Acces complet + stoc financiar",
                                size=11, color=TEXT_MUTED, text_align="center"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=BG_CARD,
                padding=ft.padding.symmetric(horizontal=28, vertical=24),
                border_radius=18,
                border=ft.border.all(2, GOLD_BRIGHT),
                width=200,
                alignment=ft.Alignment(0, 0),
                on_click=lambda _: choose("sef"),
                ink=True,
            ),
            # ADMINISTRATOR
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.MANAGE_ACCOUNTS_ROUNDED,
                                            color=BG_DEEP, size=30),
                            bgcolor=TEAL,
                            width=60, height=60,
                            border_radius=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text("ADMINISTRATOR", size=14, color=TEAL, weight="bold"),
                        ft.Container(height=4),
                        ft.Text("Vizualizare + modificare date",
                                size=11, color=TEXT_MUTED, text_align="center"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=BG_CARD,
                padding=ft.padding.symmetric(horizontal=28, vertical=24),
                border_radius=18,
                border=ft.border.all(1, TEAL),
                width=200,
                alignment=ft.Alignment(0, 0),
                on_click=lambda _: choose("administrator"),
                ink=True,
            ),
            # MANAGER
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.REMOVE_RED_EYE_ROUNDED,
                                            color=BG_DEEP, size=30),
                            bgcolor=SILVER,
                            width=60, height=60,
                            border_radius=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text("MANAGER", size=16, color=SILVER, weight="bold"),
                        ft.Container(height=4),
                        ft.Text("Vizualizare + modificare date",
                                size=11, color=TEXT_MUTED, text_align="center"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=BG_CARD,
                padding=ft.padding.symmetric(horizontal=28, vertical=24),
                border_radius=18,
                border=ft.border.all(1, SILVER),
                width=200,
                alignment=ft.Alignment(0, 0),
                on_click=lambda _: choose("manager"),
                ink=True,
            ),
        ]

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WB_SUNNY_ROUNDED,
                                            color=BG_DEEP, size=30),
                            bgcolor=GOLD_BRIGHT,
                            width=64, height=64,
                            border_radius=32,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=4),
                        ft.Text("STUDIO 30 BRONZE", size=22, color=GOLD_BRIGHT, weight="bold"),
                        ft.Text("Panou de administrare — Craiova",
                                size=11, color=TEXT_MUTED),
                        ft.Container(height=20),
                        ft.Container(height=1, width=360, bgcolor=GOLD_DIM),
                        ft.Container(height=20),
                        ft.Text("SELECTEAZĂ ROLUL TĂU", size=11, color=TEXT_MUTED, weight="bold"),
                        ft.Container(height=16),
                        ft.Row(roles_ui, spacing=16, alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
                bgcolor=BG_CARD,
                padding=40,
                border_radius=24,
                border=ft.border.all(1, GOLD_DIM),
                width=720,
            )
        )
        page.update()

    # ══════════════════════════════════════════
    #  ECRAN LOGIN (cu rol selectat)
    # ══════════════════════════════════════════
    def show_login(rol: str):
        page.vertical_alignment   = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.controls.clear()

        rol_color = ROLE_COLORS[rol]
        rol_label = ROLE_LABELS[rol]

        icon_map = {
            "sef":           ft.Icons.WORKSPACE_PREMIUM_ROUNDED,
            "administrator": ft.Icons.MANAGE_ACCOUNTS_ROUNDED,
            "manager":       ft.Icons.REMOVE_RED_EYE_ROUNDED,
        }

        parola_input = styled_field(
            f"Parolă — {rol_label}",
            password=True,
            width=320,
            on_submit=lambda _: verifica(None),
        )

        def verifica(e):
            val = parola_input.value or ""
            rol_gasit = ROLURI.get(val)
            if rol_gasit == rol:
                state["rol"] = rol
                show_panel()
            else:
                parola_input.error_text = "Parolă incorectă!"
                page.update()

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(icon_map[rol], color=BG_DEEP, size=28),
                            bgcolor=rol_color,
                            width=64, height=64,
                            border_radius=32,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=4),
                        ft.Text(rol_label, size=22, color=rol_color, weight="bold"),
                        ft.Text("Studio 30 Bronze — Autentificare", size=11, color=TEXT_MUTED),
                        ft.Container(height=16),
                        ft.Container(height=1, width=280, bgcolor=GOLD_DIM),
                        ft.Container(height=16),
                        parola_input,
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "INTRĂ ÎN PANOU",
                            on_click=verifica,
                            style=ft.ButtonStyle(
                                bgcolor=rol_color,
                                color=BG_DEEP,
                                overlay_color=GOLD_SOFT,
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(horizontal=40, vertical=14),
                                text_style=ft.TextStyle(size=13, weight="bold"),
                            ),
                        ),
                        ft.Container(height=6),
                        ft.TextButton(
                            "← Înapoi la selectare rol",
                            on_click=show_role_select,
                            style=ft.ButtonStyle(
                                color=TEXT_MUTED,
                                text_style=ft.TextStyle(size=11),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                bgcolor=BG_CARD,
                padding=40,
                border_radius=20,
                border=ft.border.all(1, ft.Colors.with_opacity(0.6, rol_color)),
                width=440,
            )
        )
        page.update()

    # ══════════════════════════════════════════
    #  PANEL PRINCIPAL
    # ══════════════════════════════════════════
    def show_panel():
        state["in_panel"] = True
        page.vertical_alignment   = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        page.controls.clear()

        rol = state["rol"]
        rol_color = ROLE_COLORS[rol]
        rol_label = ROLE_LABELS[rol]

        # Permisiuni
        poate_modifica = True  # toate rolurile pot modifica
        poate_vedea_stoc = (rol == "sef")

        clienti  = db_get_clienti()
        prezente = db_get_prezente_detaliat()
        ocupare  = db_get_ocupare()

        total    = len(clienti)
        gold_c   = sum(1 for c in clienti if c[4] == "GOLD")
        bronze_c = sum(1 for c in clienti if c[4] == "BRONZE")
        fara_c   = total - gold_c - bronze_c
        stoc, _, _ = db_calcul_stoc()

        # ── HEADER ────────────────────────────
        icon_map = {
            "sef":           ft.Icons.WORKSPACE_PREMIUM_ROUNDED,
            "administrator": ft.Icons.MANAGE_ACCOUNTS_ROUNDED,
            "manager":       ft.Icons.REMOVE_RED_EYE_ROUNDED,
        }

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon_map[rol], color=BG_DEEP, size=20),
                                bgcolor=rol_color,
                                width=38, height=38,
                                border_radius=10,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                [
                                    ft.Text("ADMIN PANEL", size=16, color=GOLD_BRIGHT, weight="bold"),
                                    ft.Row(
                                        [
                                            ft.Text("Studio 30 Bronze — ", size=10, color=TEXT_MUTED),
                                            ft.Container(
                                                content=ft.Text(rol_label, size=9,
                                                                color=BG_DEEP, weight="bold"),
                                                bgcolor=rol_color,
                                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                border_radius=10,
                                            ),
                                        ],
                                        spacing=4,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.ElevatedButton(
                        "IEȘIRE",
                        icon=ft.Icons.LOGOUT_ROUNDED,
                        on_click=show_role_select,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.12, DANGER),
                            color=DANGER,
                            side=ft.BorderSide(1, ft.Colors.with_opacity(0.4, DANGER)),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                            text_style=ft.TextStyle(size=12, weight="bold"),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_CARD,
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, GOLD_DIM)),
        )

        # ── STATISTICI + STOC ─────────────────
        stats_controls = [
            stat_box("TOTAL CLIENȚI", total, TEXT_WHITE, ft.Icons.PEOPLE_ROUNDED),
            stat_box("GOLD", gold_c, GOLD_BRIGHT, ft.Icons.WORKSPACE_PREMIUM_ROUNDED),
            stat_box("BRONZE", bronze_c, TEAL, ft.Icons.CARD_MEMBERSHIP_ROUNDED),
            stat_box("FĂRĂ ABAN.", fara_c, TEXT_MUTED, ft.Icons.PERSON_OFF_ROUNDED),
        ]

        if poate_vedea_stoc:
            stats_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
                                         color=GOLD_BRIGHT, size=18)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Text(f"{stoc} RON", size=22, color=GOLD_BRIGHT,
                                    weight="bold", text_align="center"),
                            ft.Text("VENITURI ABONAMENTE", size=9,
                                    color=TEXT_MUTED, text_align="center"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    bgcolor=BG_CARD,
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                    border_radius=14,
                    border=ft.border.all(2, GOLD_BRIGHT),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            )

        stats_row = ft.Row(stats_controls, spacing=10)

        # ── PREZENTE LIVE ─────────────────────
        def salon_card(salon_name):
            count = ocupare.get(salon_name, 0)
            clienti_aici = [p for p in prezente if p[1] == salon_name]
            dot = TEAL if count == 0 else (GOLD_BRIGHT if count <= 2 else DANGER)
            status_text = ("Liber" if count == 0 else
                           f"{count} {'client' if count == 1 else 'clienți'}")
            rows_cl = []
            for p in clienti_aici:
                rows_cl.append(
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PERSON_ROUNDED, color=BG_DEEP, size=12),
                                bgcolor=TEAL, width=22, height=22,
                                border_radius=11,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(p[0], size=12, color=TEXT_WHITE),
                            ft.Container(expand=True),
                            ft.Text(f"de la {p[2]}", size=10, color=TEXT_MUTED),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=dot),
                                ft.Text(salon_name, size=12, color=TEXT_WHITE, weight="bold"),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(status_text, size=10,
                                                    color=BG_DEEP, weight="bold"),
                                    bgcolor=dot,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    border_radius=10,
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        *(
                            [ft.Container(height=6)] + rows_cl
                            if rows_cl else
                            [ft.Text("Niciun client", size=11, color=TEXT_MUTED)]
                        ),
                    ],
                    spacing=4,
                ),
                bgcolor=BG_DEEP,
                padding=12,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.with_opacity(0.5, dot)),
                expand=True,
            )

        prezente_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.SENSORS_ROUNDED,
                                                color=BG_DEEP, size=16),
                                bgcolor=GOLD_BRIGHT, width=28, height=28,
                                border_radius=8, alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text("PREZENȚE LIVE", size=13,
                                    color=GOLD_BRIGHT, weight="bold"),
                            ft.Container(expand=True),
                            ft.Text("• actualizat automat", size=10, color=TEXT_MUTED),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Row([salon_card(s) for s in SALOANE], spacing=10),
                ],
            ),
            bgcolor=BG_CARD,
            padding=16,
            border_radius=14,
            border=ft.border.all(1, GOLD_DIM),
        )

        # ── TABEL CLIENȚI ─────────────────────
        def col_h(text):
            return ft.DataColumn(
                ft.Text(text, color=GOLD_BRIGHT, weight="bold", size=12)
            )

        rows_tabel = []
        for c in clienti:
            abo = c[4] or "Niciunul"
            abo_color = (GOLD_BRIGHT if abo == "GOLD" else
                         (TEAL if abo == "BRONZE" else TEXT_MUTED))
            min_color = (GOLD_BRIGHT if c[5] > 30 else
                         (TEAL if c[5] > 0 else DANGER))

            # Coloane de actiune (doar dacă poate modifica)
            if poate_modifica:
                input_scade = ft.TextField(
                    hint_text="min",
                    width=58, height=34,
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=12),
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=11),
                    border_color=GOLD_DIM,
                    focused_border_color=GOLD_BRIGHT,
                    cursor_color=GOLD_BRIGHT,
                    bgcolor=BG_INPUT,
                    border_radius=8,
                    content_padding=ft.padding.symmetric(horizontal=8, vertical=6),
                    text_align="center",
                )
                input_adauga = ft.TextField(
                    hint_text="min",
                    width=58, height=34,
                    text_style=ft.TextStyle(color=TEXT_WHITE, size=12),
                    hint_style=ft.TextStyle(color=TEXT_MUTED, size=11),
                    border_color=GOLD_DIM,
                    focused_border_color=TEAL,
                    cursor_color=TEAL,
                    bgcolor=BG_INPUT,
                    border_radius=8,
                    content_padding=ft.padding.symmetric(horizontal=8, vertical=6),
                    text_align="center",
                )

                def make_scade(ic, tf):
                    def handler(_):
                        if not tf.value:
                            return
                        try:
                            db_scade_minute(ic, int(tf.value))
                            tf.value = ""
                            show_panel()
                        except ValueError:
                            pass
                    return handler

                def make_adauga(ic, tf):
                    def handler(_):
                        if not tf.value:
                            return
                        try:
                            db_adauga_minute(ic, int(tf.value))
                            tf.value = ""
                            show_panel()
                        except ValueError:
                            pass
                    return handler

                actiune_cell = ft.DataCell(
                    ft.Row(
                        [
                            # Scade
                            input_scade,
                            ft.Container(
                                content=ft.Icon(ft.Icons.REMOVE_ROUNDED,
                                                color=BG_DEEP, size=15),
                                bgcolor=DANGER,
                                width=30, height=30,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                on_click=make_scade(c[0], input_scade),
                                tooltip="Scade minute",
                            ),
                            ft.Container(width=8),
                            # Adaugă
                            input_adauga,
                            ft.Container(
                                content=ft.Icon(ft.Icons.ADD_ROUNDED,
                                                color=BG_DEEP, size=15),
                                bgcolor=TEAL,
                                width=30, height=30,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                on_click=make_adauga(c[0], input_adauga),
                                tooltip="Adaugă minute",
                            ),
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )

                sterge_cell = ft.DataCell(
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_ROUNDED, color=BG_DEEP, size=16),
                        bgcolor=DANGER, width=32, height=32,
                        border_radius=8, alignment=ft.Alignment(0, 0),
                        on_click=lambda _, ic=c[0]: (db_sterge_client(ic), show_panel()),
                    )
                ) if rol == "sef" else ft.DataCell(
                    # Admin poate modifica minute dar nu sterge (optional - poti ajusta)
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_ROUNDED, color=BG_DEEP, size=16),
                        bgcolor=DANGER, width=32, height=32,
                        border_radius=8, alignment=ft.Alignment(0, 0),
                        on_click=lambda _, ic=c[0]: (db_sterge_client(ic), show_panel()),
                    )
                )

            else:
                # Manager - doar vizualizare
                actiune_cell = ft.DataCell(
                    ft.Container(
                        content=ft.Text("—", color=TEXT_MUTED, size=12),
                        padding=ft.padding.symmetric(horizontal=8),
                    )
                )
                sterge_cell = ft.DataCell(
                    ft.Container(
                        content=ft.Icon(ft.Icons.LOCK_ROUNDED, color=TEXT_MUTED, size=14),
                        tooltip="Acces restricționat",
                    )
                )

            rows_tabel.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(c[0]), color=TEXT_MUTED, size=12)),
                        ft.DataCell(ft.Text(c[1], color=TEXT_WHITE, size=13, weight="bold")),
                        ft.DataCell(ft.Text(c[2], color=TEXT_MUTED, size=12)),
                        ft.DataCell(ft.Text(c[3] or "—", color=TEXT_MUTED, size=12)),
                        ft.DataCell(badge(abo, abo_color)),
                        ft.DataCell(
                            ft.Text(str(c[5]), color=min_color, size=14, weight="bold")
                        ),
                        actiune_cell,
                        sterge_cell,
                    ]
                )
            )

        # Restricție vizuala pentru manager
        permisie_nota = None
        if not poate_modifica:
            permisie_nota = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCK_ROUNDED, color=SILVER, size=14),
                        ft.Text(
                            "Rol MANAGER — doar vizualizare. "
                            "Modificările sunt dezactivate.",
                            size=11, color=SILVER,
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor=ft.Colors.with_opacity(0.08, SILVER),
                padding=12,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, SILVER)),
            )

        tabel = ft.DataTable(
            bgcolor=BG_CARD,
            border=ft.border.all(1, GOLD_DIM),
            border_radius=14,
            column_spacing=16,
            horizontal_margin=14,
            heading_row_color=ft.Colors.with_opacity(0.06, GOLD_BRIGHT),
            heading_row_height=44,
            data_row_min_height=48,
            data_row_max_height=56,
            columns=[
                col_h("ID"),
                col_h("NUME"),
                col_h("EMAIL"),
                col_h("TELEFON"),
                col_h("ABON."),
                col_h("MIN."),
                col_h("MINUTE ±"),
                col_h("ȘTERGE"),
            ],
            rows=rows_tabel,
        )

        body_controls = [
            stats_row,
            ft.Container(height=10),
            prezente_panel,
            ft.Container(height=10),
        ]

        if permisie_nota:
            body_controls.append(permisie_nota)
            body_controls.append(ft.Container(height=10))

        body_controls += [
            ft.Text("CLIENȚI ÎNREGISTRAȚI", size=11,
                    color=GOLD_BRIGHT, weight="bold"),
            ft.Container(height=8),
            ft.Column(
                [tabel],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        ]

        page.add(
            ft.Column(
                [
                    header,
                    ft.Container(
                        content=ft.Column(
                            body_controls,
                            expand=True,
                            spacing=0,
                        ),
                        padding=ft.padding.all(20),
                        expand=True,
                    ),
                ],
                expand=True,
                spacing=0,
            )
        )
        page.update()

    # ══════════════════════════════════════════
    #  LIVE REFRESH
    # ══════════════════════════════════════════
    def live_refresh():
        while True:
            time.sleep(5)
            try:
                if state["in_panel"]:
                    show_panel()
            except Exception:
                pass

    t = threading.Thread(target=live_refresh, daemon=True)
    t.start()

    # Start
    show_role_select()


if __name__ == "__main__":
    ft.app(target=main)