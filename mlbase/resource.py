from collections import OrderedDict
import json

from mlbase.utils.cli import Command
"""
{
    "remotes": {"origin": "/mnt/datadisk/coco/", "user": "/home/user/data/"},
}

$ _ remote create <name> <path>
$ _ remote read (<name>)
$ _ remote update <name> <path>
$ _ remote delete <name>


$ _ group create <name> <path>
$ _ group read (<name>)
$ _ group update <name> <path>
$ _ group delete <name>


remote -> group -> item

tag:group
- train2014
- val2014
- test2014
- test2015
- train2017
- val2017
- test2017
- unlabeled2017

image directory

>>> r: Group = resource.remote["hoge"]
>>> r.groups
>>> r["train"]
>>> resource["new_group"] = new_group
>>> r.load()

"""

from abc import ABC, abstractmethod


class AbstractResouceGroup(ABC):
    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, val):
        pass


class ObjectGroup(AbstractResouceGroup):
    def __init__(self):
        self.__items = OrderedDict()
        self.__freezed = False

    def __getitem__(self, key):
        return self.__items[key]

    def __setitem__(self, key, val):
        if not self.__freezed:
            self.__items[key] = val

    def freeze(self):
        self.__freezed = True


class ProtocolStore:
    def __init__(self):
        self.__items = OrderedDict()

    def add(self, name):
        def wrapper(func):
            self.__items[name] = func

        return wrapper

    def interpret(self, key, val):
        return self.__items[key](val)


_REMOTE_KEY = "remote"
_REMOTE_TYPE_KEY = "type"
_REMOTE_STORE = ProtocolStore()


class ResourceGroupRepository(AbstractResouceGroup):
    def __init__(self, remote: AbstractResouceGroup) -> None:
        self.__remote = remote

    @classmethod
    def load(cls, path):
        """
        {
            "remote": [{"type": ..., "name": ...}]
            "local": [{"type": ..., "name": ...}]
        }
        """
        with open(path) as f:
            obj = json.load(f)

        remote = ObjectGroup()
        for key, val in obj[_REMOTE_KEY]:
            remote[key] = _REMOTE_STORE.interpret(val[_REMOTE_TYPE_KEY], val)
        remote.freeze()

        return cls(remote)

    @property
    def remote(self):
        return self.__remote


class UserResourceGroup:
    """
    user_id: uuid.uuid1()
    pligins: Group
    projects: Group

    """
    pass


class LocalDirectoryResourceGroup:
    pass


from os import system


def main():
    directory = "/mnt/datadisk/coco"
    # print(directory)
    # system(f"md5sum {directory}/annotations/*")
    # import hashlib
    # m = hashlib.md5(
    #     open(f"{directory}/annotations/image_info_test2014.zip",
    #          "rb").read()).hexdigest()
    # print(m)
    # $ mlbase resource plugins add --script --name
    # ~/.local/share/mlbase/resource/plugins/${name}/${scirpt}
    # ~/.local/share/mlbase/resource/resource_list.jsonl
    # {type: "mlbase:plugin", name: "", id: "...", }
    # resource add
    # ~/.local/share/
    # -> ~/.mlbase/resource
    # -> ./.mlbase/resource/resource_list.jsonl
    # -> ./.mlbase/resource/resource_info/<group_id>/items.jsonl

    group_list = [
        "test2014", "test2015", "test2017", "train2014", "train2017",
        "unlabeled2017", "val2014", "val2017", "annotations"
    ]


if __name__ == '__main__':
    main()
