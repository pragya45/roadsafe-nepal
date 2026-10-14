import unittest
from app.server import stats, validate

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid = {'occurred_on':'2026-10-01','district':'Kathmandu','location':'Kalanki','severity':'High','category':'Collision','description':'Test incident'}
    def test_valid(self):
        self.assertEqual(validate(self.valid)['severity'], 'High')
    def test_bad_date(self):
        with self.assertRaises(ValueError): validate({**self.valid, 'occurred_on':'2026-02-31'})
    def test_bad_category(self):
        with self.assertRaises(ValueError): validate({**self.valid, 'category':'Unknown'})
    def test_invalid_coordinates(self):
        with self.assertRaises(ValueError): validate({**self.valid, 'latitude':100})
    def test_required_field(self):
        with self.assertRaises(ValueError): validate({**self.valid, 'description':''})
    def test_stats(self):
        rows=[{**self.valid, 'severity':'High'},{**self.valid, 'severity':'Critical', 'category':'Near miss'}]
        result=stats(rows)
        self.assertEqual(result['total'],2)
        self.assertEqual(result['high_priority'],2)
        self.assertEqual(result['districts'],1)

if __name__ == '__main__': unittest.main()
