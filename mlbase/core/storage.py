from abc import ABC, abstractmethod
from pathlib import Path
from contextlib import contextmanager
from typing import NamedTuple, Dict, Optional
import json

_STORAGE_DICT: dict = {}


class StorageType(NamedTuple):
    name: str
    version: str
    implement: type
    args: Dict[str, type]


def register_storage(name: str, version: str, args: Optional[Dict[str, type]] = None):
    if args is None:
        args = {}

    if name not in _STORAGE_DICT:
        raise Exception(f"{name}が2度登録されています。")

    def wrap(cls):
        _STORAGE_DICT[name] = StorageType(name, version, cls, args.copy())

    return wrap


def init_storage(storage_storage_root):
    root = StorageStorage(storage_storage_root)
    root.load()


class AbstractStorage(ABC):
    def __init__(self):
        self.__parent = NoneStorage()

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent: "AbstractStorage"):
        self.__parent = parent

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    @contextmanager
    def open(self, target):
        pass


class NoneStorage(AbstractStorage):
    def load(self):
        pass

    @contextmanager
    def open(self, target):
        with open(target) as opened:
            yield opened


_STORAGE_HEAD = "mlbase_storage"
_STORAGE_LIST = "storage_list"


@register_storage("storage", "0.0.1", {"root": str})
class StorageStorage(AbstractStorage):
    """
    storageのstorage
    /path/to/storage/{_STORAGE_HEAD}: storage hash
    /path/to/storage/{_STORAGE_LIST}:
    {"hash": ..., "type": ..., "version": ..., "args": {"key": val}}
    {"hash": ..., "type": "storage", "version": ..., "args": {"root": /path/to/other_storage}}
    """

    def __init__(self, root: str) -> None:
        super().__init__()
        self.__root = Path(root)
        self.__head = _STORAGE_HEAD
        self.__list_file = _STORAGE_LIST

        self.__meta: Optional[str] = None
        self.__storages: Optional[list] = None
        self.__hash_to_storage: dict = {}

    def test(self, hash_val):
        return self.__meta == hash_val

    @contextmanager
    def open(self, path):
        path = Path(path)
        path = path if path.absolute() else Path(self.__root) / path
        with self.parent.open(path) as file_obj:
            yield file_obj

    def load(self) -> None:
        with self.open(self.__head) as head:
            self.__meta = head.read().rstrip()

        storages: list = []
        with self.open(self.__list_file) as list_file:
            for line in list_file:
                obj = json.loads(line)
                hash_val = obj["hash"]
                type_val = obj["type"]
                args = obj["args"]

                storage = _STORAGE_DICT[type_val](**args)
                storage.parent = self

                storages.append(storage)
                self.__hash_to_storage[hash_val] = storage

        self.__storages = storages


_ARXIV_LIST = "storage_list"


@register_storage("arxiv", "0.0.1", {"root": str})
class ArxivStorage(AbstractStorage):
    def __init__(self, root: str) -> None:
        super().__init__()

        self.__root = root
        self.__head = _STORAGE_HEAD
        self.__list = _ARXIV_LIST
        self.__meta = None
        self.__entries: list = []

    @contextmanager
    def open(self, target):
        with self.__find(target) as found:
            yield found

    def load(self):
        with self.parent.open(Path(self.__root) / self.__head) as head:
            self.__meta = head.read().rstrip()

        entries = []
        with self.parent.open(Path(self.__root) / self.__list) as list_file:
            for line in list_file:
                obj = json.dumps(line)
                entries.append(obj)

        self.__entries = entries
