import unittest
from app.models.customer import Customer


class TestCustomerModel(unittest.TestCase):
    def test_to_dict(self):
        customer = Customer(
            client_id="I985",
            address="332 Westmount Rd., Kitchener, ON B8B0G7",
            mobile="5195558691",
            produce=1,
            meat=0,
            dairy=0,
            delivery_count=2
        )
        customer.id = 7

        result = customer.to_dict()

        expected = {
            "id": 7,
            "client_id": "I985",
            "address": "332 Westmount Rd., Kitchener, ON B8B0G7",
            "mobile": "5195558691",
            "produce": 1,
            "meat": 0,
            "dairy": 0,
            "delivery_count": 2
        }

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()