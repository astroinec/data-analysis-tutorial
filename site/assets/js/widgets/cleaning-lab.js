(function () {
  "use strict";
  var DA = window.DA;
  DA.widgets["cleaning-lab"] = function (element) {
    var body = DA.$(".widget-body", element);
    var rows = [
      { id: "A01", quantity: 1, rating: 5 },
      { id: "A02", quantity: 2, rating: null },
      { id: "A03", quantity: 1, rating: 4 },
      { id: "A03", quantity: 1, rating: 4 },
      { id: "A04", quantity: null, rating: 5 },
      { id: "A05", quantity: -1, rating: 3 },
      { id: "A06", quantity: 3, rating: 5 }
    ];
    body.innerHTML = '<p class="w-note">独立示意数据 · 不执行 Python。先判断规则的含义，再看数量变化。</p>' +
      '<div class="w-controls"><label><input type="checkbox" class="w-dedup"> 去掉整行重复</label>' +
      '<label><input type="checkbox" class="w-isolate"> 隔离数量缺失或小于 1 的行（本示例规则）</label>' +
      '<label><input type="checkbox" class="w-dropall"> 反例：把任何缺失的行都删除</label></div>' +
      '<div class="w-result" aria-live="polite"></div>';
    var result = DA.$(".w-result", body);
    function showTable(items) {
      if (!items.length) return '<p class="empty-result">没有保留行。</p>';
      return '<div class="table-wrap"><table><thead><tr><th>订单</th><th>数量</th><th>评分</th></tr></thead><tbody>' + items.map(function (r) {
        return '<tr><td>' + r.id + '</td><td>' + (r.quantity === null ? '<span class="w-missing">缺失</span>' : r.quantity) +
          '</td><td>' + (r.rating === null ? '<span class="w-missing">未评价</span>' : r.rating) + '</td></tr>';
      }).join("") + '</tbody></table></div>';
    }
    function render() {
      var current = rows.slice(), duplicates = 0, isolated = [], deleted = [];
      if (DA.$(".w-dedup", body).checked) {
        var seen = {};
        current = current.filter(function (r) {
          var key = JSON.stringify(r);
          if (seen[key]) { duplicates += 1; return false; }
          seen[key] = true; return true;
        });
      }
      if (DA.$(".w-isolate", body).checked) {
        isolated = current.filter(function (r) { return r.quantity === null || r.quantity < 1; });
        current = current.filter(function (r) { return r.quantity !== null && r.quantity >= 1; });
      }
      if (DA.$(".w-dropall", body).checked) {
        deleted = current.filter(function (r) { return r.quantity === null || r.rating === null; });
        current = current.filter(function (r) { return r.quantity !== null && r.rating !== null; });
      }
      var rated = current.filter(function (r) { return r.rating !== null; });
      var average = rated.length ? (rated.reduce(function (s, r) { return s + r.rating; }, 0) / rated.length).toFixed(2) : "无法计算";
      result.innerHTML = '<p class="w-status">原始 7 行 → 重复移除 ' + duplicates + ' 行 → 隔离 ' + isolated.length +
        ' 行 → “全列删缺失”再删 ' + deleted.length + ' 行 → 保留 ' + current.length + ' 行。</p><h4>保留数据</h4>' + showTable(current) +
        '<p>有评分 ' + rated.length + ' 行，已有评分的均值为 ' + average + '。缺失评分没有被填成 0。</p>' +
        (isolated.length ? '<details class="fold"><summary>待核对的隔离记录</summary>' + showTable(isolated) + '</details>' : '') +
        (DA.$(".w-dropall", body).checked ? '<p class="w-warning">“未评价”不是无效订单。全列删除会把 A02 这样的有效订单丢掉；不同规则的结果不能直接比较为业务变化。</p>' :
          '<p class="w-note">真实项目应另存原始数据与清洗日志。隔离是等待核对，不等于已证实无效。</p>');
    }
    DA.$all("input", body).forEach(function (field) { field.addEventListener("change", render); });
    render();
  };
})();
