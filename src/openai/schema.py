"""
/src/openai/schema.py
OpenAI Functions
"""
from abc import ABC, abstractmethod
from typing import Any, List, Type, TypeVar

from pydantic import BaseModel, Field  # pylint: disable=E0611

F = TypeVar("F", bound="OpenAIFunction")


class FunctionCall(BaseModel):
    """Function call response"""
    name: str
    data: Any


class OpenAIFunction(BaseModel, ABC):
    """Base class for OpenAI functions"""
    class Metadata:
        subclasses: List[Type[F]] = []

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        _schema = cls.schema()
        if cls.__doc__ is None:
            raise ValueError(
                f"OpenAIFunction subclass {cls.__name__} must have a docstring"
            )
        cls.openaischema = {
            "name": cls.__name__,
            "description": cls.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    k: v for k, v in _schema["properties"].items() if k != "self"
                },
                "required": [
                    k
                    for k, v in _schema["properties"].items()
                    if v.get("required", False)
                ],
            },
        }
        cls.Metadata.subclasses.append(cls)

    async def __call__(self, **kwargs: Any) -> FunctionCall:
        response = await self.run(**kwargs)
        return FunctionCall(name=self.__class__.__name__, data=response)

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        ...
