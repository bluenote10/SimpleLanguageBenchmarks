

function visualizeCsv(csvFile, selector) {
  console.log("Rendering " + csvFile + " into " + selector);

  var numSizes = 3;
  var numRuns = 3;

  var markersize = 4;
  var rowHeight = 20;
  var colLang = "lang";

  var margins = { l: 150, r: 30, t: 30, b: 60 };

  var clientBoundingRect = document.querySelector(selector).getBoundingClientRect()
  var widthRecommended = clientBoundingRect.right - clientBoundingRect.left;
  console.log("Recommended width: " + widthRecommended)

  function render(data) {

    var numRows = data.length;
    console.log(data);
    console.log(numRows);

    var height = (data.length * rowHeight) + margins.t + margins.b;
    var canvasSizeOuter = { w: widthRecommended, h: height };
    var canvasSizeInner = {
      w: canvasSizeOuter.w - margins.l - margins.r,
      h: canvasSizeOuter.h - margins.t - margins.b
    };

    // determine min/max
    var min = +Number.MAX_VALUE;
    var max = -Number.MAX_VALUE;
    for (i = 0; i < numRows; i++) {
      var row = data[i];
      for (j = 0; j < numSizes * numRuns; j++) {
        var colname = "run_" + (j+1);
        if (row[colname] < min) {
          min = row[colname];
        }
        if (row[colname] > max) {
          max = row[colname];
        }
      }
    }

    var xScale = d3
      .scaleLinear()
      .range([0, canvasSizeInner.w])
      .domain([min, max]);
    var yScale = d3
      .scaleLinear()
      .range([0, canvasSizeInner.h])
      .domain([0, numRows-1]);

    var svg = d3
      .select(selector)
      .append("svg")
      .attr("width", canvasSizeOuter.w)
      .attr("height", canvasSizeOuter.h);

    var g = svg.append("g")
      .attr("transform", "translate(" + margins.l + ", " + margins.r + ")");

    // add tool tip
    tip = d3.tip().attr('class', 'd3-tip').html(function(d) {
      return "Language: " + d["lang"];
    });
    g.call(tip);

    // axis
    var xAxis = d3.axisBottom()
      .scale(xScale);

    g.append("g")
     .attr("transform", "translate(0," + (canvasSizeInner.h + rowHeight) + ")")
     .call(xAxis);

    // add language labels
    var labels = g.selectAll(".labels")
      .data(data)
      .enter()
      .append("text")
      .attr("x", -margins.l)
      .attr("y", function (d, i) { return yScale(i); })
      .attr("class", "langlabels")
      .text(function (d) { return d[colLang]; });

    // plot run columns
    for (i = 0; i < numSizes * numRuns; i++) {
      var colname = "run_" + (i+1);
      g.selectAll("circlerun" + i)
       .data(data)
       .enter()
       .append("circle")
       .attr("cx", function (d, i) { return xScale(d[colname]); })
       .attr("cy", function (d, i) { return yScale(i); })
       .attr("r", markersize)
       .attr("class", "circlerun circlerun" + (Math.floor(i / numRuns) + 1))
       .on('mouseover', tip.show)
       .on('mouseout', tip.hide);
    }
  }

  // https://github.com/d3/d3-request/blob/master/README.md#csv
  // https://github.com/d3/d3-dsv#dsv_parse
  d3.request(csvFile)
    .mimeType("text/csv")
    .response(function(xhr) { return d3.dsvFormat(";").parse(xhr.responseText); })
    .get(render);
}

