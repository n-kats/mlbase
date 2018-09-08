import io
import unittest
from collections import OrderedDict

from mlbase.utils.misc import print_tree


class UtilsTest(unittest.TestCase):
    def test_print_tree(self):
        target = {"a": 1}
        expected = "a: 1\n"
        sio = io.StringIO()
        print_tree(target, sio)
        result = sio.getvalue()
        self.assertEqual(result, expected)

    def test_print_tree2(self):
        target = OrderedDict()
        target["a"] = {"b": 2}
        target["c"] = 3
        expected = "a:\n  b: 2\nc: 3\n"
        sio = io.StringIO()
        print_tree(target, sio)
        result = sio.getvalue()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
