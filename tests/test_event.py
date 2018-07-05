import unittest

from mlbase.event import EventManager


class EventManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_something(self):
        """
        イベントが登録でき実行できることのテスト
        """
        em = EventManager()
        x = []

        @em.on("test")
        def _():
            x.append(0)

        em.emit("test")
        self.assertEqual(x, [0])


if __name__ == '__main__':
    unittest.main()
