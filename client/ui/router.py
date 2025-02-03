from utils.router import Router, DataStrategyEnum

from ui.home_view import HomeView
from ui.chat_view import ChatView

router = Router(DataStrategyEnum.QUERY)

router.routes = {
  "/": HomeView,
  "/chat": ChatView,
}