import unittest
from main import DFA


class Test_DFA(unittest.TestCase):
    def setUp(self) -> None:
        self.dfa = DFA()

    def test_add(self):
        word = "test_word.txt"
        tmp_ans = {'is_end': False, '傻': {'is_end': False, '逼': {'is_end': True}, 'B': '逼'}, 'S': '傻', '脑': {'is_end': False, '残': {'is_end': True}, 'C': '残'}, 'N': '脑', '杂': {'is_end': False, '种': {'is_end': True}, 'Z': '种'}, 'Z': '杂', '禽': {'is_end': False, '兽': {'is_end': True}, 'S': '兽'}, 'Q': '禽'}
        self.dfa.add_word(word)
        self.assertEqual(self.dfa.s_word, tmp_ans)

    def test_match(self):
        org = "test_org.txt"
        self.dfa.add_word("test_word.txt")
        self.dfa.match_word(org)
        self.assertEqual(self.dfa.answer, ['Line1: <傻逼> sha逼',  'Line3: <杂种> 杂z', 'Line3: <禽兽> qinshou'])


if __name__ == '__main__':
    unittest.main()
