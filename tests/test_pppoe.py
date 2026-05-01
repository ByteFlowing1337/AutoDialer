import unittest

from autodialer import is_target_asn


class TestIsTargetAsn(unittest.TestCase):
    def test_matches_with_as_prefix(self):
        self.assertTrue(
            is_target_asn(current_isp="AS9929 Chunghwa Telecom", target_asn="AS9929")
        )

    def test_matches_without_as_prefix(self):
        self.assertTrue(
            is_target_asn(current_isp="AS9929 Chunghwa Telecom", target_asn="9929")
        )

    def test_matches_with_whitespace_and_case(self):
        self.assertTrue(
            is_target_asn(current_isp="as1234 Example ISP", target_asn="  As1234 ")
        )

    def test_returns_false_for_non_matching_asn(self):
        self.assertFalse(is_target_asn(current_isp="AS4766 ISP", target_asn="AS9929"))

    def test_returns_false_for_missing_or_invalid_inputs(self):
        self.assertFalse(is_target_asn(current_isp=None, target_asn="AS9929"))
        self.assertFalse(is_target_asn(current_isp="AS9929 ISP", target_asn=None))
        self.assertFalse(is_target_asn(current_isp="", target_asn="AS9929"))
        self.assertFalse(is_target_asn(current_isp="AS9929 ISP", target_asn=""))


if __name__ == "__main__":
    unittest.main()
