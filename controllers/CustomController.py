from controllers.RouteController import RouteController
from core.Util import ConnectionInfo

class CustomController(RouteController):

  def __init__(self, connection_info: ConnectionInfo) -> None:
    super().__init__(connection_info)

  def make_decisions(self, vehicles, connection_info):
    pass