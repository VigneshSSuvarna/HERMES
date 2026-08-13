from abc import ABC, abstractmethod

class HermesConnector(ABC):
    @abstractmethod
    def get_supported_actions(self) -> list:
        """Returns a list of action_types this connector can handle."""
        pass

    @abstractmethod
    def execute(self, action_type: str, target: str) -> str:
        """Executes the action and returns a status/result string."""
        pass