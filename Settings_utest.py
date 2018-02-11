import unittest
import tempfile
import os

from Helper.Settings import Settings as Settings


class TestSettings(unittest.TestCase):
    def test_copy(self):
        s = Settings(defaults={'test': {'a': 'b'}}, ignored_sections=['test'])
        s.set('test', 'a', 'foo', temporary=True)
        s.get('test', 'a', fallback=True)
        t = s.copy()
        self.assertEqual(str(s), str(t))

    def test_defaults(self):
        s = Settings(defaults={'test': {'a': 'b'}}, ignored_sections=[])
        self.assertEqual('b', s.get('test', 'a'))

    def test_set(self):
        s = Settings(defaults={}, ignored_sections=[])
        s.set('test', 'a', 1)
        self.assertEqual('1', s.get('test', 'a'))
        self.assertEqual(1, s.getint('test', 'a'))
        self.assertEqual(1.0, s.getfloat('test', 'a'))

    def test_fallbacks(self):
        s = Settings(defaults={}, ignored_sections=[])
        s.set('test', 'a', 'foo')
        self.assertEqual('foo', s.get('test', 'a', fallback='bar'))
        self.assertEqual('bar', s.get('test', 'b', fallback='bar'))
        self.assertEqual(1, s.getint('test', 'c', fallback=1))
        self.assertEqual(1.1, s.getfloat('test', 'f', fallback=1.1))
        self.assertTrue(s.getboolean('test', 'd', fallback=True))
        self.assertFalse(s.getboolean('test', 'e', fallback=False))
        self.assertFalse(s.getboolean('test', 'e', fallback=False))
        with self.assertRaises(ValueError):
            s.getboolean('test', 'e', fallback=True)

    def test_write(self):
        s = Settings(defaults={'test': {'a': 'b'}, 'nothing': {'a': 'b'}}, ignored_sections=['anothertest'])
        t = Settings()
        s.set('anothertest', 'b', 'bar')
        s.set('test', 'b', 'c')
        s.set('test', 'b', 'foo', temporary=True)
        s.set('test', 'b', 'bar', temporary=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config')
            s.write(path)
            t.read(path)

        self.assertEqual('c', t.get('test', 'b'))
        self.assertEqual('fallback', t.get('anothertest', 'b', fallback='fallback'))
        self.assertEqual('fallback', t.get('test', 'a', fallback='fallback'))


if __name__ == '__main__':
    unittest.main()
