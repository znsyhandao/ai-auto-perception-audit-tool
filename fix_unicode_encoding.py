#!/usr/bin/env python3
"""
修复Unicode编码问题
将Unicode字符替换为ASCII等效文本
"""

import os
import re
import sys
from pathlib import Path

# Unicode字符到ASCII的映射
UNICODE_REPLACEMENTS = {
    # 表情符号
    "[OK]": "[OK]",
    "[FAIL]": "[FAIL]",
    "[WARNING]": "[WARNING]",
    "[ROCKET]": "[ROCKET]",
    "[MICROSCOPE]": "[MICROSCOPE]",
    "[SHIELD]": "[SHIELD]",
    "[CHART]": "[CHART]",
    "[CHART_UP]": "[CHART_UP]",
    "[CHART_DOWN]": "[CHART_DOWN]",
    "[WRENCH]": "[TOOL]",
    "[MAGNIFIER]": "[MAGNIFIER]",
    "[IDEA]": "[IDEA]",
    "[LIGHTNING]": "[ZAP]",
    "[FIRE]": "[FIRE]",
    "[EXPLOSION]": "[EXPLOSION]",
    "[SPARKLE]": "[SPARKLE]",
    "[STAR]": "[STAR]",
    "[TARGET]": "[TARGET]",
    "[TROPHY]": "[TROPHY]",
    "[CONSTRUCTION]": "[CONSTRUCTION]",
    "[LINK]": "[LINK]",
    "[LOCK]": "[LOCK]",
    "[UNLOCK]": "[UNLOCK]",
    "[LOCK_WITH_KEY]": "[LOCK_WITH_KEY]",
    "[KEY]": "[KEY]",
    "[CLIPBOARD]": "[CLIPBOARD]",
    "[FOLDER]": "[FOLDER]",
    "[PAGE]": "[PAGE]",
    "[NOTE]": "[NOTE]",
    "[PIN]": "[PIN]",
    "[ROUND_PIN]": "[ROUND_PIN]",
    "[PAPERCLIP]": "[PAPERCLIP]",
    "[SCISSORS]": "[SCISSORS]",
    "[RULER]": "[RULER]",
    "[TRIANGLE_RULER]": "[TRIANGLE_RULER]",
    "[HAMMER]": "[HAMMER]",
    "[NUT_AND_BOLT]": "[NUT_AND_BOLT]",
    "[GEAR]": "[GEAR]",
    "[WRENCH]": "[WRENCH]",
    "[MICROSCOPE]": "[MICROSCOPE]",
    "[TELESCOPE]": "[TELESCOPE]",
    "[SATELLITE]": "[SATELLITE]",
    "[FLOPPY]": "[FLOPPY]",
    "[CD]": "[CD]",
    "[DVD]": "[DVD]",
    "[PHONE]": "[PHONE]",
    "[PHONE_WITH_ARROW]": "[PHONE_WITH_ARROW]",
    "[TELEPHONE]": "[TELEPHONE]",
    "[TELEPHONE_RECEIVER]": "[TELEPHONE_RECEIVER]",
    "[PAGER]": "[PAGER]",
    "[FAX]": "[FAX]",
    "[TV]": "[TV]",
    "[RADIO]": "[RADIO]",
    "[MICROPHONE]": "[MICROPHONE]",
    "[LEVEL_SLIDER]": "[LEVEL_SLIDER]",
    "[CONTROL_KNOBS]": "[CONTROL_KNOBS]",
    "[COMPASS]": "[COMPASS]",
    "[STOPWATCH]": "[STOPWATCH]",
    "[TIMER_CLOCK]": "[TIMER_CLOCK]",
    "[ALARM_CLOCK]": "[ALARM_CLOCK]",
    "[MANTELPIECE_CLOCK]": "[MANTELPIECE_CLOCK]",
    "[THERMOMETER]": "[THERMOMETER]",
    "[TEST_TUBE]": "[TEST_TUBE]",
    "[PETRI_DISH]": "[PETRI_DISH]",
    "[DNA]": "[DNA]",
    "[MICROSCOPE]": "[MICROSCOPE]",
    "[TELESCOPE]": "[TELESCOPE]",
    "[SATELLITE]": "[SATELLITE]",
    
    # 箭头
    "->": "->",
    "<-": "<-",
    "^": "^",
    "v": "v",
    "/^": "/^",
    "\v": "\\v",
    "/v": "/v",
    "\^": "\\^",
    
    # 其他符号
    "*": "*",
    "->": "->",
    "<-": "<-",
    "^": "^",
    "v": "v",
    "<->": "<->",
    "^v": "^v",
    "<->": "<->",
    "^v": "^v",
    "<->": "<->",
    "<<": "<<",
    "^^": "^^",
    ">>": ">>",
    "vv": "vv",
    
    # 数学符号
    "infinity": "infinity",
    "!=": "!=",
    "<=": "<=",
    ">=": ">=",
    "~=": "~=",
    "+-": "+-",
    "*": "*",
    "/": "/",
    "sqrt": "sqrt",
    "cbrt": "cbrt",
    "fourthrt": "fourthrt",
    "sum": "sum",
    "product": "product",
    "integral": "integral",
    "partial": "partial",
    "nabla": "nabla",
    "delta": "delta",
    "propto": "propto",
    "angle": "angle",
    "parallel": "parallel",
    "perpendicular": "perpendicular",
    "intersection": "intersection",
    "union": "union",
    "in": "in",
    "notin": "notin",
    "subset": "subset",
    "superset": "superset",
    "subseteq": "subseteq",
    "superseteq": "superseteq",
    "xor": "xor",
    "tensor": "tensor",
    "odot": "odot",
    "circledot": "circledot",
    "circledast": "circledast",
    "circleddash": "circleddash",
    "boxplus": "boxplus",
    "boxminus": "boxminus",
    "boxtimes": "boxtimes",
    "boxdot": "boxdot",
    
    # 货币符号
    "EUR": "EUR",
    "GBP": "GBP",
    "JPY": "JPY",
    "RUB": "RUB",
    "INR": "INR",
    "BTC": "BTC",
    
    # 天气符号
    "[SUN]": "[SUN]",
    "[CLOUD]": "[CLOUD]",
    "[PARTLY_CLOUDY]": "[PARTLY_CLOUDY]",
    "[UMBRELLA]": "[UMBRELLA]",
    "[LIGHTNING]": "[LIGHTNING]",
    "[SNOWFLAKE]": "[SNOWFLAKE]",
    "[RAIN]": "[RAIN]",
    "[SNOW]": "[SNOW]",
    "[THUNDERSTORM]": "[THUNDERSTORM]",
    "[TORNADO]": "[TORNADO]",
    "[FOG]": "[FOG]",
    "[WIND]": "[WIND]",
    
    # 星座符号
    "[ARIES]": "[ARIES]",
    "[TAURUS]": "[TAURUS]",
    "[GEMINI]": "[GEMINI]",
    "[CANCER]": "[CANCER]",
    "[LEO]": "[LEO]",
    "[VIRGO]": "[VIRGO]",
    "[LIBRA]": "[LIBRA]",
    "[SCORPIO]": "[SCORPIO]",
    "[SAGITTARIUS]": "[SAGITTARIUS]",
    "[CAPRICORN]": "[CAPRICORN]",
    "[AQUARIUS]": "[AQUARIUS]",
    "[PISCES]": "[PISCES]",
    "[OPHIUCHUS]": "[OPHIUCHUS]",
    
    # 音乐符号
    "[QUARTER_NOTE]": "[QUARTER_NOTE]",
    "[EIGHTH_NOTE]": "[EIGHTH_NOTE]",
    "[BEAMED_EIGHTH_NOTES]": "[BEAMED_EIGHTH_NOTES]",
    "[BEAMED_SIXTEENTH_NOTES]": "[BEAMED_SIXTEENTH_NOTES]",
    "[FLAT]": "[FLAT]",
    "[NATURAL]": "[NATURAL]",
    "[SHARP]": "[SHARP]",
    
    # 棋类符号
    "[WHITE_KING]": "[WHITE_KING]",
    "[WHITE_QUEEN]": "[WHITE_QUEEN]",
    "[WHITE_ROOK]": "[WHITE_ROOK]",
    "[WHITE_BISHOP]": "[WHITE_BISHOP]",
    "[WHITE_KNIGHT]": "[WHITE_KNIGHT]",
    "[WHITE_PAWN]": "[WHITE_PAWN]",
    "[BLACK_KING]": "[BLACK_KING]",
    "[BLACK_QUEEN]": "[BLACK_QUEEN]",
    "[BLACK_ROOK]": "[BLACK_ROOK]",
    "[BLACK_BISHOP]": "[BLACK_BISHOP]",
    "[BLACK_KNIGHT]": "[BLACK_KNIGHT]",
    "[BLACK_PAWN]": "[BLACK_PAWN]",
    
    # 其他
    "(c)": "(c)",
    "(R)": "(R)",
    "(TM)": "(TM)",
    "(P)": "(P)",
    "(SM)": "(SM)",
    "TEL": "TEL",
    "No.": "No.",
    "Rx": "Rx",
    "mho": "mho",
    "ohm": "ohm",
    "K": "K",
    "A": "A",
    "e": "e",
    "fax": "fax",
    "pi": "pi",
    "gamma": "gamma",
    "Gamma": "Gamma",
    "Pi": "Pi",
    "summation": "summation",
    "G": "G",
    "L": "L",
    "L": "L",
    "Y": "Y",
    "D": "D",
    "d": "d",
    "e": "e",
    "i": "i",
    "j": "j",
}

def replace_unicode_chars(text):
    """替换文本中的Unicode字符"""
    for unicode_char, ascii_replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(unicode_char, ascii_replacement)
    return text

def fix_file_encoding(file_path):
    """修复单个文件的编码问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换Unicode字符
        fixed_content = replace_unicode_chars(content)
        
        # 如果内容有变化，保存文件
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, f"Fixed {file_path}"
        else:
            return False, f"No changes needed for {file_path}"
            
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
            
            # 转换为UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Converted {file_path} from GBK to UTF-8"
        except:
            return False, f"Failed to read {file_path}"
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"

def main():
    """主函数"""
    print("=== Fixing Unicode Encoding Issues ===")
    print()
    
    # 要处理的文件列表
    target_files = [
        "enterprise_audit_prototype.py",
        "integrate_v2_tools.py",
        "check_release_files_improved.py",
        "check_release_files_simple.py",
        "check_release_files.py",
        "final_release_verification.py",
        "improved_test_suite.py",
        "run_tool_tests.py",
        "fix_chinese_encoding.py",
        "fix_encoding_all.py",
        "fix_encoding_simple.py",
        "fix_skill_structure.py",
        "fix_unicode_encoding.py",  # 自身也要修复
    ]
    
    # 添加Python文件
    for file in Path(".").glob("*.py"):
        if file.name not in target_files:
            target_files.append(file.name)
    
    fixed_count = 0
    error_count = 0
    
    for file_name in target_files:
        if not os.path.exists(file_name):
            continue
            
        print(f"Processing: {file_name}")
        fixed, message = fix_file_encoding(file_name)
        
        if fixed:
            print(f"  [OK] {message}")
            fixed_count += 1
        else:
            print(f"  [INFO] {message}")
            
        if "Error" in message or "Failed" in message:
            error_count += 1
    
    print()
    print("=== Summary ===")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    
    if error_count == 0:
        print()
        print("[SUCCESS] All files fixed successfully!")
        return 0
    else:
        print()
        print("[WARNING] Some files had errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())