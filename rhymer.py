# -*- coding: utf-8 -*-
from pypinyin import pinyin, Style
import re
from collections import defaultdict, Counter
from colorama import init, Fore, Style as ColorStyle

init(autoreset=True)  # 自动重置颜色

def extract_vowel(pinyin_str):
    """从拼音中提取韵母部分"""
    vowels = ['uang', 'iang', 'ang', 'eng', 'ing', 'ong', 'iao', 'ian', 'uan', 'uen', 'uai',
              'ai', 'ei', 'ao', 'ou', 'an', 'en', 'in', 'un', 'er', 'i', 'u', 'ü']
    for v in vowels:
        if pinyin_str.endswith(v):
            return v
    for c in reversed(pinyin_str):
        if c in 'aeiouü':
            return c
    return pinyin_str

def analyze_poem(poem):
    # 分句
    sentences = re.split(r'[，。；？！、\n\r]', poem.replace(' ', ''))
    sentences = [s for s in sentences if s]

    rhyme_map = defaultdict(list)

    for sentence in sentences:
        last_char = sentence[-1]
        if not re.match(r'[\u4e00-\u9fa5]', last_char):
            continue
        py_tone = pinyin(last_char, style=Style.TONE3)[0][0]
        py_plain = pinyin(last_char, style=Style.NORMAL)[0][0]
        rhyme = extract_vowel(py_plain)
        rhyme_map[rhyme].append((last_char, py_tone))

    if not rhyme_map:
        print(Fore.RED + "未检测到有效汉字，请检查输入。")
        return

    # 统计韵母出现次数
    rhyme_counts = {r: len(lst) for r, lst in rhyme_map.items()}
    main_rhyme = max(rhyme_counts, key=rhyme_counts.get)

    # 过滤：只保留出现≥2次或主韵母
    filtered_rhymes = {r: lst for r, lst in rhyme_map.items() if len(lst) >= 2 or r == main_rhyme}

    # 排序：主韵母置顶，其余按出现次数降序
    sorted_rhymes = sorted(
        filtered_rhymes.items(),
        key=lambda x: (x[0] != main_rhyme, -len(x[1]))
    )

    # 计算列宽
    col1 = "韵母"
    col2 = "出现次数"
    col3 = "对应汉字（拼音, 次数）"
    data_rows = []
    for rhyme, char_list in sorted_rhymes:
        counter = Counter(char_list)
        count = sum(counter.values())
        display = "、".join([f"{c}({p},{n}次)" for (c, p), n in sorted(counter.items())])
        data_rows.append((rhyme, str(count), display))

    col1_width = max(len(col1), max(len(r[0]) for r in data_rows)) + 4
    col2_width = max(len(col2), max(len(r[1]) for r in data_rows)) + 4
    col3_width = max(len(col3), max(len(r[2]) for r in data_rows)) + 4

    total_width = col1_width + col2_width + col3_width + 6

    # 打印表头
    print(Fore.CYAN + "\n诗词韵母分析结果（表格形式，居中对齐）\n")
    print(Fore.YELLOW + "=" * total_width)
    print(Fore.YELLOW + f"|{col1.center(col1_width)}|{col2.center(col2_width)}|{col3.center(col3_width)}|")
    print(Fore.YELLOW + "-" * total_width)

    # 打印表格内容
    for rhyme, count, display in data_rows:
        if rhyme == main_rhyme:
            # 主韵母绿色加粗高亮
            print(
                Fore.GREEN + ColorStyle.BRIGHT
                + f"|{'⭐' + rhyme.center(col1_width - 2)}|{count.center(col2_width)}|{display.center(col3_width)}|"
            )
        else:
            print(f"|{rhyme.center(col1_width)}|{count.center(col2_width)}|{display.center(col3_width)}|")

    print(Fore.YELLOW + "=" * total_width)
    print(
        f"\n👉 主韵母为：{Fore.GREEN + ColorStyle.BRIGHT}[{main_rhyme}]{ColorStyle.RESET_ALL}"
        f"，共出现 {rhyme_counts[main_rhyme]} 次。\n"
    )

if __name__ == "__main__":
    print("请输入完整诗词（可多行输入，输入空行结束）：\n")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    poem = "\n".join(lines)
    analyze_poem(poem)
