(function () {
  "use strict";
  var DA = window.DA;
  DA.widgets["chart-picker"] = function (element) {
    var body = DA.$(".widget-body", element);
    var scenarios = [
      { question: "每个月销售额怎么变化？", chart: "折线图", reason: "横轴是有先后顺序的月份，重点看趋势。月份先排序，不用柱子的视觉面积判断增长。", trap: "没有上一年数据，就不能写同比增长。", code: 'ax.plot(months, sales)\nax.set_ylabel("销售额（元）")', svg: '<polyline points="30,140 80,154 130,106 180,116 230,50 280,66" fill="none" stroke="currentColor" stroke-width="4" />' },
      { question: "哪个品类卖得更多？", chart: "柱形图 / 条形图", reason: "比较离散类别的汇总大小。按值排序，长名称可使用水平条形图。", trap: "柱形图数值轴从 0 开始；类别多时不勉强挤成饼图。", code: 'ax.barh(categories, sales)\nax.set_xlabel("销售额（元）")', svg: '<path d="M45 168V110H80V168 M115 168V66H150V168 M185 168V32H220V168 M255 168V130H290V168" fill="currentColor" opacity="0.75" />' },
      { question: "大多数订单的金额在哪一段？", chart: "直方图", reason: "按连续金额的区间计数，观察分布、偏斜与长尾。每一柱不是一个商品类别。", trap: "分箱宽度会改变外观，说明口径；均值不足以描述长尾。", code: 'ax.hist(amounts, bins=15)\nax.set_xlabel("订单金额（元）")', svg: '<path d="M32 168V130H70V168 M70 168V74H108V168 M108 168V36H146V168 M146 168V62H184V168 M184 168V100H222V168 M222 168V136H260V168 M260 168V154H298V168" fill="currentColor" opacity="0.75" />' },
      { question: "账单金额和小费有关吗？", chart: "散点图", reason: "一笔账单一个点，横纵轴是两个数值变量。看到同向趋势可以描述相关，不能直接归因。", trap: "相关性不等于因果，还可能受人数、时段等因素影响。", code: 'ax.scatter(bills, tips, alpha=0.6)\nax.set_xlabel("账单金额（美元）")', svg: '<g fill="currentColor"><circle cx="55" cy="152" r="5"/><circle cx="77" cy="133" r="5"/><circle cx="112" cy="143" r="5"/><circle cx="140" cy="104" r="5"/><circle cx="160" cy="122" r="5"/><circle cx="189" cy="84" r="5"/><circle cx="211" cy="109" r="5"/><circle cx="240" cy="48" r="5"/><circle cx="265" cy="66" r="5"/></g>' }
    ];
    body.innerHTML = '<p class="w-note">点击业务问题看选图理由。图形是小样本示意，不是课程业务结果；不执行 Python。</p>' +
      '<div class="w-button-row">' + scenarios.map(function (s, i) { return '<button class="w-btn" type="button" data-index="' + i + '" aria-pressed="false">' + s.question + '</button>'; }).join("") +
      '</div><div class="w-result" aria-live="polite"></div>';
    function render(index) {
      var scenario = scenarios[index];
      DA.$all(".w-btn", body).forEach(function (button, i) { button.classList.toggle("active", i === index); button.setAttribute("aria-pressed", String(i === index)); });
      var result = DA.$(".w-result", body);
      result.innerHTML = '<div class="w-chart-answer"><svg class="w-mini-chart" viewBox="0 0 330 190" role="img" aria-label="' + DA.esc(scenario.chart) +
        '示意"><path d="M25 20V168H310" fill="none" stroke="currentColor" opacity="0.35" stroke-width="2"/>' + scenario.svg +
        '</svg><div><h4>推荐：' + scenario.chart + '</h4><p>' + scenario.reason + '</p><p class="w-warning">注意：' + scenario.trap +
        '</p></div></div><pre><code class="language-python">' + DA.esc(scenario.code) + '</code></pre>';
      DA.enhanceCode(result);
    }
    DA.$all(".w-btn", body).forEach(function (button) { button.addEventListener("click", function () { render(Number(button.getAttribute("data-index"))); }); });
    render(0);
  };
})();
