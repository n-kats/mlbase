from pathlib import Path
from typing import NamedTuple, Dict, Optional
import json

_STORAGE_DICT: dict = {}


class StorageType(NamedTuple):
    name: str
    implement: type
    args: Dict[str, type]


def register_storage(name: str, args: Optional[Dict[str, type]] = None):
    if args is None:
        args = {}

    if name not in _STORAGE_DICT:
        raise Exception(f"{name}が2度登録されています。")

    def wrap(cls):
        _STORAGE_DICT[name] = StorageType(name, cls, args.copy())

    return wrap


STORAGE_HEAD = "mlbase_storage"
STORAGE_LIST = "storage_list"


@register_storage("storage", {"root": str})
class StorageStorage:
    """
    storageのstorage
    /path/to/storage/{STORAGE_HEAD}: storage hash
    /path/to/storage/{STORAGE_LIST}:
    {"hash": ..., "type": ..., "args": {"key": val}}
    {"hash": ..., "type": "storage", "args": {"root": /path/to/other_storage}}
    """

    def __init__(self, root: str) -> None:
        self.__root = Path(root)
        self.__head = self.__root / STORAGE_HEAD
        self.__list_file = self.__root / STORAGE_LIST

        self.__meta: Optional[str] = None
        self.__storages: Optional[list] = None
        self.__hash_to_storage: dict = {}

    def test(self, hash_val):
        return self.__meta == hash_val

    def load(self) -> None:
        with open(self.__head) as head:
            self.__meta = head.read().rstrip()

        storages: list = []
        with open(self.__list_file) as list_file:
            for line in list_file:
                obj = json.loads(line)
                hash_val = obj["hash"]
                type_val = obj["type"]
                args = obj["args"]
                storage = _STORAGE_DICT[type_val](**args)
                storages.append(storage)
                self.__hash_to_storage[hash_val] = storage

        self.__storages = storages
