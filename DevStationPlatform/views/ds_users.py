"""
DS_USERS — Gestão de Usuários e Perfis
Sprint 4 · Flet 0.84
Perfil mínimo: ADMIN
"""

import flet as ft
from datetime import datetime
from typing import Optional

from core.models.base import db_manager
from core.models.user import User, Profile
from core.audit_logger import audit_logger
from views.components.style import DSStyle, Size, Semantic
from views.components.badges import Badge, Avatar, ProfileChip, StatusDot
from views.components.controls import DSButton, DSField, DSTableRow, DSDetailPanel, DSFilterRow


def _fmt_ts(dt) -> str:
    if not dt:
        return "—"
    try:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt)


class UsersView(DSStyle):
    """
    Tela DS_USERS — listagem, criação e edição de usuários.
    Herda DSStyle para tokens de layout/tema.
    """

    def __init__(self, page: ft.Page, user_data: dict):
        super().__init__(page)
        self.user = user_data
        self._all_users: list = []
        self._all_profiles: list = []
        self._search_text = ""
        self._filter_active = "TODOS"

        # UI refs
        self._lv: Optional[ft.ListView] = None
        self._search_tf: Optional[ft.TextField] = None
        self._active_dd: Optional[ft.Dropdown] = None
        self._detail: Optional[ft.Container] = None
        self._count_text: Optional[ft.Text] = None

    # ── Build ─────────────────────────────────────

    def build(self) -> ft.Container:
        t = self.t
        self._all_users    = self._load_users()
        self._all_profiles = self._load_profiles()

        self._search_tf = DSField.search("Buscar usuário / email…", width=280, t=t,
                                         on_change=self._on_filter)
        self._active_dd = DSField.dropdown(
            "Status", ["TODOS", "Ativo", "Inativo"],
            width=140, on_change=self._on_filter, t=t,
        )

        self._count_text = ft.Text(
            f"{len(self._all_users)} usuários",
            size=Size.TEXT_BASE, color=t.subtext,
        )

        new_btn = DSButton.primary("+ Novo Usuário", ft.Icons.PERSON_ADD,
                                   on_click=self._show_new_dialog, t=t)

        filter_row = DSFilterRow.make(
            [self._search_tf, self._active_dd, self._count_text],
            on_refresh=self._on_refresh, t=t,
        )

        col_header = self.col_header([
            ("", 44),
            ("Usuário",   160),
            ("Email",     200),
            ("Nome Completo", None),
            ("Perfis",    200),
            ("Criado em", 130),
            ("Status",    80),
            ("Ações",     80),
        ])

        self._lv = ft.ListView(spacing=0, expand=True)
        self._rebuild_list()

        table = self.table_card(col_header, self._lv)

        self._detail = DSDetailPanel.make(t, height=130)

        return self.page_container(
            ft.Column(
                [
                    self.section(
                        "DS_USERS — Gestão de Usuários",
                        "Administração de usuários, perfis e permissões de acesso.",
                        [new_btn],
                    ),
                    self.divider(),
                    filter_row,
                    table,
                    self._detail,
                ],
                spacing=14,
                expand=True,
            )
        )

    # ── Data ──────────────────────────────────────

    def _load_users(self) -> list:
        try:
            session = db_manager.get_session()
            users = session.query(User).order_by(User.username).all()
            result = []
            for u in users:
                result.append({
                    "id":         u.id,
                    "username":   u.username,
                    "email":      u.email or "",
                    "full_name":  u.full_name or "",
                    "is_active":  u.is_active,
                    "is_system":  getattr(u, "is_system", False),
                    "created_at": _fmt_ts(getattr(u, "created_at", None)),
                    "profiles":   [p.code for p in u.profiles] if u.profiles else [],
                })
            session.close()
            return result
        except Exception as ex:
            print(f"[UsersView] _load_users: {ex}")
            return []

    def _load_profiles(self) -> list:
        try:
            session = db_manager.get_session()
            profiles = session.query(Profile).order_by(Profile.priority.desc()).all()
            result = [{"code": p.code, "name": p.name} for p in profiles]
            session.close()
            return result
        except Exception:
            return []

    # ── Row ───────────────────────────────────────

    def _build_row(self, u: dict) -> ft.Container:
        t = self.t
        profiles = u.get("profiles", [])
        active = u.get("is_active", False)
        is_sys = u.get("is_system", False)

        def on_click(e, user=u):
            self._show_detail(user)

        def on_edit(e, user=u):
            self._show_edit_dialog(user)

        def on_toggle(e, user=u):
            self._toggle_active(user)

        cells = [
            # Avatar
            ft.Container(content=Avatar.make(u["username"], size=30), width=44),
            # Username
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(u["username"], size=Size.TEXT_BASE, color=t.primary,
                                weight=ft.FontWeight.W_600),
                        *(
                            [ft.Container(
                                content=ft.Text("sistema", size=9, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.GREY_500, border_radius=3,
                                padding=ft.Padding.symmetric(horizontal=5, vertical=1),
                            )]
                            if is_sys else []
                        ),
                    ],
                    spacing=2, tight=True,
                ),
                width=160,
            ),
            # Email
            ft.Text(u["email"], size=Size.TEXT_BASE, color=t.text, width=200,
                    overflow=ft.TextOverflow.ELLIPSIS),
            # Full name
            ft.Text(u["full_name"] or "—", size=Size.TEXT_BASE, color=t.text,
                    expand=True, overflow=ft.TextOverflow.ELLIPSIS),
            # Profiles
            ft.Container(
                content=ProfileChip.row(profiles) if profiles
                else ft.Text("Sem perfil", size=Size.TEXT_XS, color=t.subtext),
                width=200,
            ),
            # Created
            ft.Text(u["created_at"], size=Size.TEXT_BASE, color=t.subtext, width=130),
            # Status
            ft.Container(
                content=StatusDot.make(active, "Ativo" if active else "Inativo"),
                width=80,
            ),
            # Actions
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=t.primary,
                        icon_size=16,
                        tooltip="Editar",
                        on_click=on_edit,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.TOGGLE_ON if active else ft.Icons.TOGGLE_OFF,
                        icon_color=t.success if active else t.subtext,
                        icon_size=16,
                        tooltip="Ativar/Desativar",
                        on_click=on_toggle,
                        disabled=is_sys,
                    ),
                ],
                spacing=0,
                width=80,
            ),
        ]

        return DSTableRow.make(cells, t, on_click=on_click)

    # ── Detail ─────────────────────────────────────

    def _show_detail(self, u: dict):
        t = self.t
        profiles = u.get("profiles", [])
        DSDetailPanel.update(
            self._detail,
            ft.Column(
                [
                    ft.Row(
                        [
                            Avatar.make(u["username"], size=40),
                            ft.Column(
                                [
                                    ft.Text(u["full_name"] or u["username"],
                                            size=Size.TEXT_LG, weight=ft.FontWeight.BOLD,
                                            color=t.text),
                                    ft.Text(u["email"], size=Size.TEXT_BASE, color=t.subtext),
                                ],
                                spacing=2, tight=True,
                            ),
                            ft.Container(expand=True),
                            ProfileChip.row(profiles),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.Text(f"ID: {u['id']}", size=Size.TEXT_XS, color=t.subtext),
                            ft.Text(f"Criado: {u['created_at']}", size=Size.TEXT_XS, color=t.subtext),
                            ft.Text(
                                "✅ Sistema" if u.get("is_system") else "👤 Usuário",
                                size=Size.TEXT_XS, color=t.subtext,
                            ),
                        ],
                        spacing=16,
                    ),
                ],
                spacing=10,
            ),
        )

    # ── Filter ────────────────────────────────────

    def _filtered(self) -> list:
        rows = self._all_users
        if self._filter_active == "Ativo":
            rows = [r for r in rows if r.get("is_active")]
        elif self._filter_active == "Inativo":
            rows = [r for r in rows if not r.get("is_active")]
        if self._search_text:
            q = self._search_text.lower()
            rows = [r for r in rows if
                    q in r.get("username","").lower()
                    or q in r.get("email","").lower()
                    or q in r.get("full_name","").lower()]
        return rows

    def _rebuild_list(self):
        filtered = self._filtered()
        self._lv.controls.clear()
        if not filtered:
            self._lv.controls.append(self.empty_state("Nenhum usuário encontrado."))
        else:
            for u in filtered:
                self._lv.controls.append(self._build_row(u))
        if self._count_text:
            self._count_text.value = f"{len(filtered)} usuário(s)"

    def _on_filter(self, e):
        self._filter_active = self._active_dd.value or "TODOS"
        self._search_text   = self._search_tf.value or ""
        self._rebuild_list()
        self._lv.update()
        self._count_text.update()

    def _on_refresh(self, e):
        self._all_users = self._load_users()
        self._rebuild_list()
        self._lv.update()
        self._count_text.update()

    # ── Toggle active ─────────────────────────────

    def _toggle_active(self, u: dict):
        if u.get("is_system"):
            return
        try:
            session = db_manager.get_session()
            user = session.query(User).filter(User.id == u["id"]).first()
            if user:
                user.is_active = not user.is_active
                session.commit()
                audit_logger.log(
                    user_id=self.user.get("id", 0),
                    user_name=self.user.get("username", "?"),
                    user_profiles=", ".join(self.user.get("profiles", [])),
                    transaction_code="DS_USERS",
                    action_type="UPDATE",
                    object_type="USER",
                    object_id=str(u["id"]),
                    object_name=u["username"],
                    diff_summary=f"is_active → {user.is_active}",
                )
            session.close()
        except Exception as ex:
            print(f"[UsersView] toggle_active: {ex}")
        self._on_refresh(None)

    # ── New User dialog ───────────────────────────

    def _show_new_dialog(self, e):
        t = self.t
        username_tf = DSField.text("Usuário *", t=t)
        email_tf    = DSField.text("Email",     t=t)
        name_tf     = DSField.text("Nome Completo", t=t)
        pass_tf     = DSField.text("Senha *",   t=t, password=True)
        pass2_tf    = DSField.text("Confirmar Senha *", t=t, password=True)

        profile_options = [p["code"] for p in self._all_profiles]
        profile_dd = DSField.dropdown("Perfil *", profile_options, t=t, width=200)

        err_text = ft.Text("", color=t.error, size=Size.TEXT_BASE)

        def save(e):
            if not username_tf.value or not pass_tf.value:
                err_text.value = "Usuário e senha são obrigatórios."
                err_text.update()
                return
            if pass_tf.value != pass2_tf.value:
                err_text.value = "As senhas não coincidem."
                err_text.update()
                return
            try:
                session = db_manager.get_session()
                # Verifica duplicata
                exists = session.query(User).filter(User.username == username_tf.value).first()
                if exists:
                    err_text.value = f"Usuário '{username_tf.value}' já existe."
                    err_text.update()
                    session.close()
                    return

                new_user = User(
                    username=username_tf.value.strip(),
                    email=email_tf.value.strip() or None,
                    full_name=name_tf.value.strip() or None,
                    is_active=True,
                )
                new_user.set_password(pass_tf.value)

                if profile_dd.value:
                    profile = session.query(Profile).filter(
                        Profile.code == profile_dd.value
                    ).first()
                    if profile:
                        new_user.profiles.append(profile)

                session.add(new_user)
                session.commit()

                audit_logger.log(
                    user_id=self.user.get("id", 0),
                    user_name=self.user.get("username", "?"),
                    user_profiles=", ".join(self.user.get("profiles", [])),
                    transaction_code="DS_USERS",
                    action_type="CREATE",
                    object_type="USER",
                    object_name=username_tf.value,
                )
                session.close()
                dlg.open = False
                self.page.update()
                self._on_refresh(None)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Usuário '{username_tf.value}' criado com sucesso!"),
                    open=True,
                )
                self.page.update()
            except Exception as ex:
                err_text.value = f"Erro: {ex}"
                err_text.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Novo Usuário", color=t.text),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([username_tf, profile_dd], spacing=12),
                        email_tf,
                        name_tf,
                        ft.Row([pass_tf, pass2_tf], spacing=12),
                        err_text,
                    ],
                    spacing=12, tight=True,
                ),
                width=500,
                bgcolor=t.card,
            ),
            actions=[
                ft.TextButton("Cancelar",
                    on_click=lambda e: (setattr(dlg, "open", False), self.page.update())),
                DSButton.primary("Criar Usuário", ft.Icons.CHECK, on_click=save, t=t),
            ],
            bgcolor=t.card,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ── Edit dialog ───────────────────────────────

    def _show_edit_dialog(self, u: dict):
        t = self.t
        name_tf  = DSField.text("Nome Completo", value=u.get("full_name",""), t=t)
        email_tf = DSField.text("Email",          value=u.get("email",""),     t=t)
        pass_tf  = DSField.text("Nova Senha (deixe vazio p/ manter)", t=t, password=True)

        profile_options = [p["code"] for p in self._all_profiles]
        current_profile = u["profiles"][0] if u["profiles"] else (profile_options[0] if profile_options else "USER")
        profile_dd = DSField.dropdown("Perfil", profile_options, value=current_profile,
                                      t=t, width=200)
        err_text = ft.Text("", color=t.error, size=Size.TEXT_BASE)

        def save(e):
            try:
                session = db_manager.get_session()
                user = session.query(User).filter(User.id == u["id"]).first()
                if not user:
                    session.close(); return

                old = {"full_name": user.full_name, "email": user.email}

                user.full_name = name_tf.value.strip() or None
                user.email     = email_tf.value.strip() or None
                if pass_tf.value:
                    user.set_password(pass_tf.value)

                if profile_dd.value:
                    user.profiles.clear()
                    profile = session.query(Profile).filter(
                        Profile.code == profile_dd.value
                    ).first()
                    if profile:
                        user.profiles.append(profile)

                session.commit()
                new = {"full_name": user.full_name, "email": user.email}
                session.close()

                audit_logger.log(
                    user_id=self.user.get("id", 0),
                    user_name=self.user.get("username", "?"),
                    user_profiles=", ".join(self.user.get("profiles", [])),
                    transaction_code="DS_USERS",
                    action_type="UPDATE",
                    object_type="USER",
                    object_id=str(u["id"]),
                    object_name=u["username"],
                    old_value=old,
                    new_value=new,
                )

                dlg.open = False
                self.page.update()
                self._on_refresh(None)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Usuário '{u['username']}' atualizado!"),
                    open=True,
                )
                self.page.update()
            except Exception as ex:
                err_text.value = f"Erro: {ex}"
                err_text.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Editar: {u['username']}", color=t.text),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([name_tf, profile_dd], spacing=12),
                        email_tf,
                        pass_tf,
                        err_text,
                    ],
                    spacing=12, tight=True,
                ),
                width=500,
                bgcolor=t.card,
            ),
            actions=[
                ft.TextButton("Cancelar",
                    on_click=lambda e: (setattr(dlg, "open", False), self.page.update())),
                DSButton.primary("Salvar", ft.Icons.SAVE, on_click=save, t=t),
            ],
            bgcolor=t.card,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
