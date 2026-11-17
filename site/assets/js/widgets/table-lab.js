(function () {
  "use strict";
  var DA = window.DA;
  DA.widgets["table-lab"] = function (element, config) {
    var body = DA.$(".widget-body", element);
    var mode = config.mode || "filter";
    var rows = [
      { "订单": "O01", "品类": "文具", "平台": "淘宝", "金额": 39 },
      { "订单": "O02", "品类": "书籍", "平台": "微信小程序", "金额": 58 },
      { "订单": "O03", "品类": "文具", "平台": "淘宝", "金额": 69 },
      { "订单": "O04", "品类": "帆布包", "平台": "微信小程序", "金额": 99 },
      { "订单": "O05", "品类": "书籍", "平台": "淘宝", "金额": 36 },
      { "订单": "O06", "品类": "文具", "平台": "淘宝", "金额": 15 }
    ];
    function table(items, columns, flags) {
      if (!items.length) return '<p class="empty-result">没有匹配行。空表不代表代码出错。</p>';
      return '<div class="table-wrap"><table><thead><tr>' + columns.map(function (c) {
        return "<th>" + DA.esc(c) + "</th>";
      }).join("") + "</tr></thead><tbody>" + items.map(function (row, i) {
        return '<tr class="' + (flags ? (flags[i] ? "w-match" : "w-dim") : "") + '">' + columns.map(function (c) {
          return "<td>" + DA.esc(row[c]) + "</td>";
        }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
    }
    var control;
    if (mode === "filter") {
      control = '<label class="w-control">金额至少 <output class="w-threshold">50</output> 元' +
        '<input type="range" class="w-range" min="0" max="120" step="5" value="50" aria-label="筛选金额门槛"></label>';
    } else if (mode === "sort") {
      control = '<label class="w-control">排序方式 <select class="w-select"><option value="desc">金额从高到低</option>' +
        '<option value="asc">金额从低到高</option><option value="id">恢复订单顺序</option></select></label>';
    } else if (mode === "groupby") {
      control = '<label class="w-control">按照哪一列分组？ <select class="w-select"><option>品类</option><option>平台</option></select></label>';
    } else {
      throw new Error("不支持的 table-lab 模式：" + mode);
    }
    body.innerHTML = '<p class="w-note">6 行独立小样本 · 教学模拟，不执行 Python，也不读取你的电脑数据。</p>' + control +
      '<div class="w-input"></div><div class="w-result" aria-live="polite"></div>';
    var input = DA.$(".w-input", body);
    var result = DA.$(".w-result", body);
    function render() {
      var output, code, description, flags = null;
      if (mode === "filter") {
        var threshold = Number(DA.$(".w-range", body).value);
        DA.$(".w-threshold", body).textContent = threshold;
        flags = rows.map(function (r) { return r["金额"] >= threshold; });
        output = rows.filter(function (r, i) { return flags[i]; });
        code = 'df.loc[df["金额"] >= ' + threshold + ']';
        description = '条件结果：[' + flags.map(function (f) { return f ? "True" : "False"; }).join(", ") +
          ']。留下 ' + output.length + ' / 6 行；金额合计 ' + output.reduce(function (s, r) { return s + r["金额"]; }, 0) + ' 元。';
      } else if (mode === "sort") {
        var direction = DA.$(".w-select", body).value;
        output = rows.slice();
        if (direction !== "id") output.sort(function (a, b) { return (a["金额"] - b["金额"]) * (direction === "asc" ? 1 : -1); });
        code = direction === "id" ? 'df.sort_values("订单")' : 'df.sort_values("金额", ascending=' + (direction === "asc" ? "True" : "False") + ')';
        description = '排序改变行的先后，不改变订单数量或金额合计（仍为 316 元）。';
      } else {
        var key = DA.$(".w-select", body).value;
        var groups = {};
        rows.forEach(function (r) { groups[r[key]] = (groups[r[key]] || 0) + r["金额"]; });
        output = Object.keys(groups).map(function (k) { var r = {}; r[key] = k; r["金额"] = groups[k]; return r; });
        code = 'df.groupby("' + key + '", as_index=False)["金额"].sum()';
        description = '先按“' + key + '”放进不同组，再在每组里求和。汇总后 ' + output.length + ' 行，金额合计仍为 316 元。';
      }
      input.innerHTML = '<h4>操作前：一行一个订单</h4>' + table(rows, ["订单", "品类", "平台", "金额"], flags);
      var columns = mode === "groupby" ? [DA.$(".w-select", body).value, "金额"] : ["订单", "品类", "平台", "金额"];
      result.innerHTML = '<p class="w-status">' + DA.esc(description) + '</p><pre><code class="language-python">' + DA.esc(code) +
        '</code></pre><h4>操作后</h4>' + table(output, columns);
      DA.enhanceCode(result);
    }
    var field = DA.$("input, select", body);
    field.addEventListener(mode === "filter" ? "input" : "change", render);
    render();
  };
})();
