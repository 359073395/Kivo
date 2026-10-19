import unittest
from warehouse_sku_aliases import apply_confirmed_warehouse_aliases as apply,normalize

class AliasTests(unittest.TestCase):
    def test_two_confirmed_aliases(self):
        r=apply({normalize('Face LIFT01=Pink FAY'):42000,normalize('NUGEN Bloom'):48000})
        self.assertEqual(r[normalize('Face LIFT01= Pink FAY')],42000)
        self.assertEqual(r[normalize('NUGEN BIoom')],48000)
    def test_exact_original_wins(self):
        r=apply({normalize('NUGEN Bloom'):48000,normalize('NUGEN BIoom'):49000})
        self.assertEqual(r[normalize('NUGEN BIoom')],49000)
    def test_missing_target_stays_missing(self):
        self.assertNotIn(normalize('NUGEN BIoom'),apply({}))
    def test_no_general_whitespace_or_letter_replacement(self):
        r=apply({normalize('Face LIFT02=GLAD CODE'):42000,normalize('Other Bloom'):48000})
        self.assertNotIn(normalize('Face LIFT02= GLAD CODE'),r)
        self.assertNotIn(normalize('Other BIoom'),r)

if __name__=='__main__':unittest.main()
