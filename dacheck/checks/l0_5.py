"""第 0-5 课：环境概念与课程数据可达练习。"""
import sys

from dacheck.core import expect_equal, expect_type, load, register


@register("0-5.1", hint="sys.executable 是当前内核的真实 Python 路径；不要抄网页的示例路径。", title="确认当前解释器")
def check_python_path(answer):
    expect_type(answer, str, "解释器路径")
    expect_equal(answer, sys.executable, "当前解释器路径")


@register("0-5.2", hint='填写字符串 "python -m pip"；这题不会执行安装命令。', title="绑定 Python 的 pip")
def check_pip_command(answer):
    expect_type(answer, str, "命令文字")
    expect_equal(answer, "python -m pip", "绑定当前 Python 的写法")


@register("0-5.3", hint='pd.read_csv("../data/books.csv").shape[0] 读取本套数据的行数。', title="课程数据可达")
def check_book_rows(answer):
    expect_equal(answer, load("books.csv").shape[0], "图书数据行数")
