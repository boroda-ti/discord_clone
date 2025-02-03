from typing import Callable
from enum import Enum

import flet as ft


class Router:
    def __init__(self):
        self.data = dict()
        self.routes = {}
        self.body = ft.Container()

    def set_route(self, endpoint: str, view: Callable):
        self.routes[endpoint] = view
    
    def set_routes(self, route_dictionary: dict):
        self.routes.update(route_dictionary)

    def route_change(self, route):
        _page = route.route.split("?")[0]
        queries = route.route.split("?")[1].split("&") # old [1:]

        for item in queries:
            key = item.split("=")[0]
            value = item.split("=")[1]
            self.data[key] = value #.replace('+', ' ')

        self.body.content = self.routes[_page](self)
        self.body.update()

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)