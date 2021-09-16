import pypinyin
import time
import sys


class DFA:
    def __init__(self):
        self.s_word = dict()
        self.alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.skip_word = ['<', '>', '?', '"', '}', '{', '|', ' ', '！', '@', '#', '￥', '%', '…', '&', '*', '$', '(', ')', '-', '_', '+', '=', '？', '“', '”', '；', ':', '^', '!', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.spelling = dict()
        self.pinyin = dict()
        self.answer = list()
        self.count_num = 0

    def add_word(self, words):
        f = open(words, 'r', encoding='utf-8')
        for keyword in f:
            char = keyword.strip()
            char = char.lower()
            i_word = self.s_word
            for i in range(len(char)):
                if char[i] not in self.alpha:
                    py = pypinyin.pinyin(char[i], style=pypinyin.NORMAL).pop().pop()
                    self.pinyin[py] = char[i]
                    j_word = self.spelling
                    for j in range(len(py)):
                        j_word['is_end'] = False
                        if py[j] not in j_word:
                            new_node = dict()
                            j_word[py[j]] = new_node
                            j_word = j_word[py[j]]
                        else:
                            j_word = j_word[py[j]]
                        if j == len(py) - 1:
                            j_word['ans'] = char[i]
                            j_word['is_end'] = True
                            break
                i_word['is_end'] = False
                if char[i] not in i_word :
                    new_node = dict()
                    i_word[char[i]] = new_node
                    i_word[py[0].upper()] = char[i]
                    i_word = i_word[char[i]]
                else:
                    i_word = i_word[char[i]]
                if i == len(char) - 1:
                    i_word['is_end'] = True
                    break
        f.close()

    def match_word(self, org):
        f = open(org, 'r', encoding='utf-8')
        line_num = 0
        self.count_num = 0
        for keyword in f:
            i_word = self.s_word
            truth = keyword.strip()
            char = truth.lower()
            line_num += 1
            start_num = 0
            time_num = 0
            tmp_char = ""
            wrong_char = ""
            for i in range(len(char)):
                if time_num != 0:
                    time_num -= 1
                    continue
                j_word = self.spelling
                if char[i] in self.spelling:
                    mini_start = 0
                    mini_wrong = ""
                    for j in range(i, len(char)):
                        time_num += 1
                        if char[j] in self.skip_word:
                            if mini_start != 0:
                                mini_wrong = mini_wrong + truth[j]
                            continue
                        if char[j] in j_word:
                            j_word = j_word[char[j]]
                            if mini_start == 0:
                                mini_wrong = wrong_char + truth[j]
                                mini_start += 1
                            else:
                                mini_wrong = mini_wrong + truth[j]
                                mini_start += 1
                            if j_word['is_end']:
                                ans = j_word['ans']
                                if ans in i_word:
                                    i_word = i_word[ans]
                                elif ans in self.s_word:
                                    i_word = self.s_word[ans]
                                    tmp_char = ""
                                    start_num = 0
                                tmp_char = tmp_char + ans
                                mini_start -= mini_start
                                wrong_char = mini_wrong
                                start_num += 1
                                time_num -= 1
                                if i_word['is_end']:
                                    i_word = self.s_word
                                    start_num = 0
                                    self.count_num += 1
                                    final_ans = "Line" + str(line_num) + ": <" + tmp_char +"> " + mini_wrong
                                    self.answer.append(final_ans)
                                    tmp_char = ""
                                    wrong_char = ""
                                break
                        else:
                            time_num = 0
                            break
                if char[i] in self.alpha:
                    if char[i].upper() in i_word:
                        flag_num = 0
                        tmp_word = i_word
                        num = i
                        big_char = tmp_char
                        mini_wrong = wrong_char
                        mini_start = 0
                        abb_word = self.spelling
                        while True:
                            big = char[num].upper()
                            if flag_num != 0:
                                flag_num -= 1
                                num += 1
                                continue
                            if big.lower() in self.spelling:
                                for j in range(num, len(char)):
                                    flag_num += 1
                                    if char[j] in self.skip_word:
                                        if mini_start != 0:
                                            mini_wrong = mini_wrong + char[j]
                                        continue
                                    if char[j] in abb_word:
                                        mini_start += 1
                                        abb_word = abb_word[char[j]]
                                        if abb_word['is_end']:
                                            ans = abb_word['ans']
                                            if ans in tmp_word:
                                                tmp_word = tmp_word[ans]
                                            elif ans in self.s_word:
                                                tmp_word = self.s_word[ans]
                                                big_char = ""
                                                start_num = 0
                                            big_char = big_char + ans
                                            start_num += 1
                                            flag_num -= 1
                                            num += flag_num + 1
                                            flag_num = 0
                                            mini_start = 0
                                            if num != len(char):
                                                big = char[num].upper()
                                            abb_word = self.spelling
                                            if tmp_word['is_end']:
                                                tmp_word = self.s_word
                                                start_num = 0
                                                self.count_num += 1
                                                print("line" + str(line_num) + ':' + big_char + mini_wrong)
                                                final_ans = "Line" + str(line_num) + ": <" + big_char + "> " + mini_wrong
                                                self.answer.append(final_ans)
                                                big_char = ""
                                    else:
                                        abb_word = self.spelling
                                        flag_num = 0
                                        if start_num == 0:
                                            mini_wrong = ""
                                        mini_start = 0
                                        break
                            if num == len(char):
                                break
                            if big in tmp_word:
                                if big.lower() in self.alpha:
                                    x = tmp_word[big]
                                else:
                                    x = big
                                tmp_word = tmp_word[x]
                                big_char = big_char + x
                                mini_wrong = mini_wrong + truth[num]
                                if tmp_word['is_end']:
                                    start_num = 0
                                    self.count_num += 1
                                    final_ans = "Line" + str(line_num) + ": <" + big_char +"> " + mini_wrong
                                    self.answer.append(final_ans)
                                    tmp_char = ""
                                    i_word = self.s_word
                                    time_num = num - i
                                    break
                            else:
                                time_num = num - i - 1
                                break
                            if num == len(char):
                                time_num = num - i - 1
                                break
                            num += 1
                if char[i] not in self.alpha and char[i] not in self.skip_word:
                    py = pypinyin.pinyin(char[i], style=pypinyin.NORMAL).pop().pop()
                    if py in self.pinyin.keys():
                        x = self.pinyin[py]
                    else:
                        x = char[i]
                else:
                    x = char[i]
                if x in i_word:
                    if start_num == 0:
                        wrong_char = truth[i]
                        tmp_char = x
                        start_num += 1
                    else:
                        wrong_char = wrong_char + truth[i]
                        tmp_char = tmp_char + x
                        start_num += 1
                    i_word = i_word[x]
                    if i_word['is_end']:
                        i_word = self.s_word
                        start_num = 0
                        self.count_num += 1
                        final_ans = "Line" + str(line_num) + ": <" + tmp_char + "> " + wrong_char
                        self.answer.append(final_ans)
                        tmp_char = ""
                        wrong_char = ""
                elif time_num == 0:
                    if char[i] not in self.skip_word:
                        i_word = self.s_word
                        start_num = 0
                        tmp_char = ""
                        wrong_char = ""
                    elif char[i] in self.skip_word and start_num != 0:
                        wrong_char = wrong_char + char[i]
        f.close()

    def write_file(self, ano_ans):
        fw = open(ano_ans, 'w', encoding="utf-8")
        fw.write("Total: " + str(self.count_num))
        fw.write('\n')
        for key in self.answer:
            fw.write(key)
            fw.write('\n')
        print(self.count_num)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("error")
        exit(-1)
    words = sys.argv[1]
    org = sys.argv[2]
    ans = sys.argv[3]
    a1 = time.time()
    pro = DFA()
    pro.add_word(words)
    pro.match_word(org)
    pro.write_file(ans)
    a2 = time.time()
    print(a2-a1)
