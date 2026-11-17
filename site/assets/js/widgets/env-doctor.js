(function () {
  "use strict";
  var DA = window.DA;
  DA.widgets["env-doctor"] = function (element) {
    var body = DA.$(".widget-body", element);
    var cases = {
      conda: { title: "命令窗口找不到 conda", steps: ["关闭普通 cmd / PowerShell，重新从开始菜单打开 Anaconda Prompt。", "运行 conda --version；如果这里也找不到，回安装课检查是否完成及是否有开始菜单快捷方式。", "不要为了绕过报错乱加 PATH，也不要反复再装另一个 Python。"], code: 'conda --version' },
      package: { title: "ModuleNotFoundError：缺包", steps: ["在报错的 Notebook 运行下方 Python，记录实际解释器路径。", "另开 Anaconda Prompt，激活 da-course，运行 python -m pip --version。比较路径是否在同一环境。", "若环境不同：切换 Notebook 右上角内核为 Python (da-course)，重启内核。若相同且缺包：在教程根目录按安装课安装 requirements.txt。"], code: 'import sys\nprint(sys.executable)' },
      path: { title: "FileNotFoundError：找不到文件", steps: ["先确认教程完整解压；Notebook 仍在 notebooks/ 或 solutions/，data/ 与它同级。", "运行下方代码看当前工作目录，不要把教材中的演示路径当成你电脑的真实路径。", "在 JupyterLab 左侧找到 data/ 的真实文件；不要先重装 Python，路径错误与 Python 安装通常是不同问题。"], code: 'from pathlib import Path\nprint(Path.cwd())\nprint(Path("../data/books.csv").exists())' },
      kernel: { title: "Prompt 明明装过包，Notebook 还是失败", steps: ["Prompt 的环境和 Notebook 的内核可以不同。先比较两边的 sys.executable。", "从激活的 da-course 环境注册内核，再在右上角选择 Python (da-course)。", "重启内核后从第一格重新运行；已经执行过的旧变量不会自动迁移到新内核。"], code: 'python -m ipykernel install --user --name da-course --display-name "Python (da-course)"' },
      encoding: { title: "UnicodeDecodeError 或中文乱码", steps: ["确认读取的是哪一份 CSV。课程普通 CSV 用 UTF-8，orders_gbk.csv 故意使用 GBK。", "只对已确认的 GBK 文件指定 encoding=\"gbk\"；不要随机尝试编码并静默忽略坏字符。", "中文方框若只出现在图表里，是字体问题，运行 setup_chinese_font()，并查看工具箱 A-2。"], code: 'pd.read_csv("../data/shop/orders_gbk.csv", encoding="gbk")' },
      start: { title: "Jupyter 没有打开，或网页连不上", steps: ["启动窗口必须保持打开。观察最后几行是否给出 127.0.0.1 / localhost 开头的地址。", "把终端给出的完整本地地址复制到浏览器；不要猜端口，也不要公开分享含 token 的地址。", "如果程序已经退出，先查终端报错；只有端口占用时才考虑另选端口，不要关闭安全设置来解决。"], code: 'python -m jupyter lab' }
    };
    body.innerHTML = '<p class="w-note">按症状分流的教学向导。它不会检测电脑；真正体检用 tools/check_env.py。</p>' +
      '<label class="w-control">你卡在哪里？ <select class="w-select"><option value="conda">找不到 conda</option>' +
      '<option value="package">缺包 / ModuleNotFoundError</option><option value="path">找不到文件</option>' +
      '<option value="kernel">装过包，但 Notebook 不认</option><option value="encoding">编码错误或中文方框</option>' +
      '<option value="start">Jupyter 启动或访问失败</option></select></label><div class="w-result" aria-live="polite"></div>';
    function render() {
      var key = DA.$("select", body).value, item = cases[key];
      var language = key === "conda" || key === "kernel" || key === "start" ? "terminal" : "python";
      var result = DA.$(".w-result", body);
      result.innerHTML = '<h4>' + item.title + '</h4><ol>' + item.steps.map(function (step) { return '<li>' + DA.esc(step) + '</li>'; }).join("") +
        '</ol><pre><code class="language-' + language + '">' + DA.esc(item.code) + '</code></pre>';
      DA.enhanceCode(result);
    }
    DA.$("select", body).addEventListener("change", render);
    render();
  };
})();
