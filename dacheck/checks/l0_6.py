"""第 0-6 课：不依赖真实 Windows 系统的独立入门练习。"""
from dacheck.core import expect_equal, expect_type, register


@register("0-6.1", hint="把 ... 换成 2 + 3，不需要加引号。", title="运行简单计算")
def check_result(answer):
    expect_equal(answer, 2 + 3, "计算结果")


@register("0-6.2", hint='把 ... 换成 "我能运行代码"，英文直引号中放中文文字。', title="中文文字")
def check_message(answer):
    expect_type(answer, str, "消息")
    expect_equal(answer, "我能运行代码", "消息内容")


@register("0-6.3", hint='pd.DataFrame({"任务": ["读取", "检查", "保存"]}).shape[0] 是行数。', title="三项任务的行数")
def check_task_rows(answer):
    import pandas as pd
    sample = pd.DataFrame({"任务": ["读取", "检查", "保存"]})
    expect_equal(answer, sample.shape[0], "任务行数")
