import unittest
from src.predict import predict_stock_price

class TestModel(unittest.TestCase):
    def test_predict_stock_price(self):
        # We assume AAPL works and returns a dict with 'prediction'
        result = predict_stock_price("AAPL")
        self.assertIn('predicted_price', result)
        self.assertIn('last_price', result)

if __name__ == '__main__':
    unittest.main()
