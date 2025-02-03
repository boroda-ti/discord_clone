import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import flet as ft

from ui.router import router

def main(page: ft.Page):

    page.theme_mode = "dark"

    page.on_route_change = router.route_change
    router.page = page
    page.add(
        router.body,
        ft.Text("123")
    )

    page.go('/')

ft.app(target=main)