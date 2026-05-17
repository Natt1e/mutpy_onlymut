import os
import tempfile
import unittest

from mutpy.main_mutation import generate_mutants_from_file


class MainMutationTest(unittest.TestCase):

    def test_generate_mutants_from_file_with_limit(self):
        source = "def mul(x, y):\n    return x * y\n"
        file_path = self._create_temp_python_file(source)
        try:
            mutants = generate_mutants_from_file(file_path, 2)
        finally:
            os.unlink(file_path)

        self.assertEqual(len(mutants), 2)
        self.assertEqual(mutants[0]['number'], 1)
        self.assertEqual(mutants[1]['number'], 2)
        self.assertTrue(mutants[0]['mutations'])
        self.assertTrue(mutants[0]['source'])

    def test_generate_mutants_from_file_rejects_invalid_count(self):
        source = "x = 1\n"
        file_path = self._create_temp_python_file(source)
        try:
            with self.assertRaises(ValueError):
                generate_mutants_from_file(file_path, 0)
        finally:
            os.unlink(file_path)

    def test_generate_mutants_from_code_string_with_limit(self):
        source = "def mul(x, y):\n    return x * y\n"
        mutants = generate_mutants_from_file(mutant_count=2, code_string=source)

        self.assertEqual(len(mutants), 2)
        self.assertEqual(mutants[0]['number'], 1)
        self.assertEqual(mutants[1]['number'], 2)
        self.assertTrue(mutants[0]['mutations'])
        self.assertTrue(mutants[0]['source'])

    def _create_temp_python_file(self, source):
        fd, path = tempfile.mkstemp(suffix='.py')
        try:
            with os.fdopen(fd, 'w') as temp_file:
                temp_file.write(source)
        except BaseException:
            os.unlink(path)
            raise
        return path
