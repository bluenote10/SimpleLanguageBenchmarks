
function powerOfTen(d) {
  return d / Math.pow(10, Math.ceil(Math.log(d) / Math.LN10 - 1e-12)) === 1;
}

function curry(fn) {
     var slice = Array.prototype.slice,
        stored_args = slice.call(arguments, 1);
     return function () {
        var new_args = slice.call(arguments),
              args = stored_args.concat(new_args);
        return fn.apply(null, args);
     };
}

function uniqueMaintainOrder(data, getter) {
  var arr = [];
  var arrayLength = data.length;
  for (var i = 0; i < arrayLength; i++) {
    var value = getter(data[i]);
    if (arr.length == 0) {
      arr.push(value);
    } else {
      var last_element = arr[arr.length - 1];
      if (last_element != value) {
        arr.push(value);
      }
    }
  }
  return arr;
}

function extractLangAndSuffix(data, colLang, colSuffix) {
  var arrLang = [];
  var arrSffx = [];
  var arrayLength = data.length;
  for (var i = 0; i < arrayLength; i++) {
    var lang = data[i][colLang];
    var sffx = data[i][colSuffix];
    if (arrLang.length == 0) {
      arrLang.push(lang);
      arrSffx.push(sffx);
    } else {
      var lastElementLang = arrLang[arrLang.length - 1];
      var lastElementSffx = arrSffx[arrSffx.length - 1];
      if (lastElementLang != lang || lastElementSffx != sffx) {
        arrLang.push(lang);
        arrSffx.push(sffx);
      }
    }
  }
  return [arrLang, arrSffx];
}


function visualizeCsv(csvFile, selector, scaleLinear) {
  console.log("Rendering " + csvFile + " into " + selector);

  var numSizes = 3;
  var numRuns = 3;

  var markersize = 5;
  var rowHeight = 20;

  var colLang = "label"; // TODO: rename to colLabel as soon as we need actual colLang
  var colTime = "time";
  var colSize = "size";
  var colSuffix = "descr";

  var margins = { l: 150, r: 30, t: 30, b: 90 };

  var clientBoundingRect = document.querySelector(selector).getBoundingClientRect()
  var widthRecommended = clientBoundingRect.right - clientBoundingRect.left;
  console.log("Recommended width: " + widthRecommended)

  function render(data) {

    // var dataLangAndSuffix = extractLangAndSuffix(data, colLang, colSuffix);
    // var dataLang = dataLangAndSuffix[0];
    // var dataSffx = dataLangAndSuffix[1];
    var dataLang = uniqueMaintainOrder(data, (d) => d[colLang]);

    var numRows = dataLang.length;
    console.log(dataLang);
    console.log(data);
    console.log(numRows);

    var height = (numRows * rowHeight) + margins.t + margins.b;
    var canvasSizeOuter = { w: widthRecommended, h: height };
    var canvasSizeInner = {
      w: canvasSizeOuter.w - margins.l - margins.r,
      h: canvasSizeOuter.h - margins.t - margins.b
    };

    // determine min/max
    var min = d3.min(data, (d) => d["time"]);
    var max = d3.max(data, (d) => d["time"]);
    console.log("min: " + min);
    console.log("max: " + max);

    if (scaleLinear) {
      var xScale = d3
        .scaleLinear()
        .range([0, canvasSizeInner.w])
        .domain([min, max]);
    } else {
      var xScale = d3
        .scaleLog()
        .range([0, canvasSizeInner.w])
        .domain([min, max]);
    }
    var yScale = d3
      .scalePoint()
      .range([0, canvasSizeInner.h])
      .domain(dataLang);

    var svg = d3
      .select(selector)
      .append("svg")
      .attr("width", canvasSizeOuter.w)
      .attr("height", canvasSizeOuter.h);

    var g = svg.append("g")
      .attr("transform", "translate(" + margins.l + ", " + margins.r + ")");

    // add tool tip
    function toolTopRenderBinder(dataarg) {
      // let globaldata = dataarg;
      // console.log("Binding data: " + globaldata[0][colTime] + " " + globaldata[1][colTime] + " " + globaldata[1][colTime]);
      return function toolTipRender(d, globaldata) {
        // console.log("this = " + this);
        var size = d[colSize];
        var bestTime = Number.MAX_VALUE;
        for (var i = 0; i < globaldata.length; i++) {
          if (globaldata[i][colSize] == size && globaldata[i][colTime] < bestTime) {
            bestTime = globaldata[i][colTime];
          }
        }
        // console.log("Using data: " + globaldata.length + " " + globaldata[0][colTime] + " " + globaldata[1][colTime] + " " + globaldata[1][colTime]);
        var relativePerformance = (bestTime == d[colTime]) ?
          "This is the fastest run in class " + size :
          "Slower than fastest run: " + ((100 * d[colTime] / bestTime) - 100).toFixed(1) + " %"; // + bestTime;
        return "Language: " + d[colLang] + "</br>" +
          "Runtime: " + d[colTime].toFixed(3) + " sec" + "</br>" +
          relativePerformance;
      }
    }
    tip = d3.tip()
            .attr('class', 'd3-tip')
            .direction('e')
            .offset([-2, 15])
            .html(toolTopRenderBinder(data));
    g.call(tip);

    // axis
    var xAxis = d3.axisBottom()
      .scale(xScale);

    g.append("g")
     .attr("class", "x axis")
     .attr("transform", "translate(0," + (canvasSizeInner.h + rowHeight) + ")")
     .call(xAxis);

    // only for log scale: switch to power-of-ten labelling http://bl.ocks.org/mbostock/6738229
    if (!scaleLinear) {
      g.selectAll(".tick text")
       .attr("transform", "translate(0, 4)")
       .text(null)
       .filter(powerOfTen)
       .text(10)
       .append("tspan")
       .attr("dy", "-.7em")
       .text(function(d) { return Math.round(Math.log(d) / Math.LN10); });
    }

    g.append("text")
     .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
     .attr("transform",
       "translate("+ (canvasSizeInner.w/2) + "," + (canvasSizeInner.h + 3*rowHeight) + ")"
     )
     .text("Runtime [sec]");

    // add language labels
    var labels = g.selectAll(".labels")
      .data(dataLang)
      .enter()
      .append("text")
      .attr("x", -margins.l)
      .attr("y", function (lang) { return yScale(lang); })
      .attr("class", "langlabels")
      .text(function (lang, i) {
        return lang;
      });

    var sizesLookup = {
      S: "circlerun1",
      M: "circlerun2",
      L: "circlerun3",
    }

    // plot run columns
    g.selectAll("circlerun")
     .data(data)
     .enter()
     .append("circle")
     .attr("cx", function (d, i) { return xScale(d[colTime]); })
     .attr("cy", function (d, i) { return yScale(d[colLang]); })
     .attr("r", markersize)
     .attr("class", (d) => "circlerun " + sizesLookup[d[colSize]])
     /*
     .on('mouseover', (d, i) => {
       console.log("mouseover");
       tip.show(d, i);
       g.selectAll("circlerun")
        .filter((e) => e[colSize] != d[colSize])
        .transition()
        .style("opacity", 0.2);
      })
      */
     .on('mouseover', function (d) {
       tip.show(d, data);
       g.selectAll(".circlerun")
        .filter((e) => e[colSize] != d[colSize])
        .transition()
        .style("opacity", 0.2);
      })
     .on('mouseout', function (d) {
       tip.hide(d);
       g.selectAll(".circlerun")
        .transition()
        .style("opacity", 1.0);
     });
  }

  function rowFormatter(row) {
    row[colTime] = +row[colTime];
    return row;
  }

  // https://github.com/d3/d3-request/blob/master/README.md#csv
  // https://github.com/d3/d3-dsv#dsv_parse
  d3.request(csvFile)
    .mimeType("text/csv")
    .response(function(xhr) { return d3.dsvFormat(";").parse(xhr.responseText, rowFormatter); })
    .get(render);
}


function visualizeCsvStageSummary(csvFile, selector) {
  console.log("Rendering stage summary " + csvFile + " into " + selector);

  var markersize = 5;
  var rowHeight = 20;

  var colLang = "label"; // TODO: rename to colLabel as soon as we need actual colLang
  var colTime = "time";
  var colSize = "size";
  var colSuffix = "descr";
  var colStage = "stage";

  var margins = { l: 150, r: 30, t: 30, b: 90 };

  var clientBoundingRect = document.querySelector(selector).getBoundingClientRect()
  var widthRecommended = clientBoundingRect.right - clientBoundingRect.left;
  console.log("Recommended width: " + widthRecommended)

  function render(data) {

    var dataLang = uniqueMaintainOrder(data, (d) => d[colLang]);
    var dataStages = d3.map(data, (d) => d[colStage]).keys()

    var numRows = dataLang.length;
    var numStages = dataStages.length;
    console.log(dataLang);
    console.log(dataStages);
    console.log(data);
    console.log(numRows);

    var height = (numRows * numStages * rowHeight) + margins.t + margins.b;
    var canvasSizeOuter = { w: widthRecommended, h: height };
    var canvasSizeInner = {
      w: canvasSizeOuter.w - margins.l - margins.r,
      h: canvasSizeOuter.h - margins.t - margins.b
    };

    // determine min/max
    var min = d3.min(data, (d) => d["time"]) * 0.9; // allowing to see a small bar even for the min
    var max = d3.max(data, (d) => d["time"]);
    console.log("min: " + min);
    console.log("max: " + max);

    var xScale = d3
      .scaleLog()
      .range([0, canvasSizeInner.w])
      .domain([min, max]);
    var yScaleLang = d3
      .scaleBand()
      .rangeRound([0, canvasSizeInner.h])
      .paddingInner(0.4)
      .domain(dataLang);
    var yScaleStages = d3
      .scaleBand()
      .rangeRound([0, yScaleLang.bandwidth()])
      .padding(0.4)
      .domain(dataStages);

    var svg = d3
      .select(selector)
      .append("svg")
      .attr("width", canvasSizeOuter.w)
      .attr("height", canvasSizeOuter.h);

    var g = svg.append("g")
      .attr("transform", "translate(" + margins.l + ", " + margins.r + ")");

    // add tool tip
    function toolTipRender(d, globaldata) {
      return "Stage: " + d[colStage] + "</br>" +
        "Runtime: " + d[colTime].toFixed(3) + " sec";
    }
    tip = d3.tip()
            .attr('class', 'd3-tip')
            .direction('e')
            .offset([-2, 15])
            .html(toolTipRender);
    g.call(tip);

    // axis
    var xAxis = d3.axisBottom()
      .scale(xScale);

    g.append("g")
     .attr("class", "x axis")
     .attr("transform", "translate(0," + (canvasSizeInner.h + rowHeight) + ")")
     .call(xAxis);

    // only for log scale: switch to power-of-ten labelling http://bl.ocks.org/mbostock/6738229
    g.selectAll(".tick text")
     .attr("transform", "translate(0, 4)")
     .text(null)
     .filter(powerOfTen)
     .text(10)
     .append("tspan")
     .attr("dy", "-.7em")
     .text(function(d) { return Math.round(Math.log(d) / Math.LN10); });

    g.append("text")
     .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
     .attr("transform",
       "translate("+ (canvasSizeInner.w/2) + "," + (canvasSizeInner.h + 3*rowHeight) + ")"
     )
     .text("Runtime [sec]");

    // add language labels
    var labels = g.selectAll(".labels")
      .data(dataLang)
      .enter()
      .append("text")
      .attr("x", -margins.l)
      .attr("y", function (lang) { return yScaleLang(lang); })
      .attr("class", "langlabels")
      .attr("dominant-baseline", "baseline")
      .text(function (lang, i) {
        return lang;
      });

    // plot run columns
    g.selectAll("stagebar")
     .data(data)
     .enter()
     .append("rect")
     .attr("x", 0)
     .attr("y", function (d, i) { return yScaleLang(d[colLang]) + yScaleStages(d[colStage]) - yScaleLang.bandwidth()/2; })
     .attr("width", function (d, i) { return xScale(d[colTime]); })
     .attr("height", yScaleStages.bandwidth())
     .attr("class", (d) => "stagebar")
     .on('mouseover', function (d) {
       //tip.show(d, data);
       g.selectAll(".stagebar")
        .filter((e) => e[colStage] != d[colStage])
        .transition()
        .style("opacity", 0.2);
      })
     .on('mouseout', function (d) {
       //tip.hide(d);
       g.selectAll(".stagebar")
        .transition()
        .style("opacity", 1.0);
     });
  }

  function rowFormatter(row) {
    row[colTime] = +row[colTime];
    return row;
  }

  // https://github.com/d3/d3-request/blob/master/README.md#csv
  // https://github.com/d3/d3-dsv#dsv_parse
  d3.request(csvFile)
    .mimeType("text/csv")
    .response(function(xhr) { return d3.dsvFormat(";").parse(xhr.responseText, rowFormatter); })
    .get(render);
}


/*
function visualizeCsvOldSchema(csvFile, selector) {
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
*/

