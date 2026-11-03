import unittest

from fastapi import HTTPException

from src import app


class SignupCapacityTests(unittest.TestCase):
    def setUp(self):
        self.activity = app.activities["Chess Club"]
        self.original_participants = self.activity["participants"]
        self.original_max_participants = self.activity["max_participants"]
        self.activity["participants"] = ["existing@example.edu"]
        self.activity["max_participants"] = 2

    def tearDown(self):
        self.activity["participants"] = self.original_participants
        self.activity["max_participants"] = self.original_max_participants

    def test_signup_below_capacity_succeeds(self):
        result = app.signup_for_activity("Chess Club", "new@example.edu")

        self.assertEqual(
            result,
            {"message": "Signed up new@example.edu for Chess Club"},
        )
        self.assertEqual(
            self.activity["participants"],
            ["existing@example.edu", "new@example.edu"],
        )

    def test_signup_at_capacity_is_rejected_without_changing_participants(self):
        self.activity["participants"].append("another@example.edu")
        participants_before_signup = self.activity["participants"].copy()

        with self.assertRaises(HTTPException) as raised:
            app.signup_for_activity("Chess Club", "new@example.edu")

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "Activity is full")
        self.assertEqual(self.activity["participants"], participants_before_signup)

    def test_duplicate_signup_validation_is_preserved_at_capacity(self):
        self.activity["participants"].append("another@example.edu")

        with self.assertRaises(HTTPException) as raised:
            app.signup_for_activity("Chess Club", "existing@example.edu")

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "Student is already signed up")


if __name__ == "__main__":
    unittest.main()
