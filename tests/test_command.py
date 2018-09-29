"""
Commandのテスト
"""

import unittest

from mlbase.utils.cli import Command, get_meta


class TestCommand(unittest.TestCase):
    def test_something(self):
        root = Command("root", "A_")
        cmd = root >> Command("cmd1", "cmd1") >> Command("cmd2", "cmd2")

        @cmd
        def run_test(args):
            self.assertEqual(get_meta(args).parents, ["root", "cmd1"])

        argv = ["cmd1", "cmd2"]
        root.start(argv)


if __name__ == '__main__':
    unittest.main()
