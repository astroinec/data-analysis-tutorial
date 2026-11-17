"""
dacheck：本教程的练习检查工具。

在练习本（notebook）里这样用：

    import sys; sys.path.insert(0, "..")   # 让 Python 找到上一级文件夹里的 dacheck
    from dacheck import check, hint

    answer = ...          # 把 ... 换成你的代码
    check("2-1.1", answer)

    hint("2-1.1")         # 卡住了？看提示
"""
from .core import (  # noqa: F401
    DATA_DIR,
    ROOT_DIR,
    CheckFail,
    check,
    expect,
    expect_close,
    expect_df,
    expect_equal,
    expect_series,
    expect_type,
    fail,
    hint,
    load,
    progress,
    register,
    reset_progress,
    setup_chinese_font,
)

__version__ = "1.0"
