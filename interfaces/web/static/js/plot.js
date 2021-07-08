function transformData(data){
  return Object.keys(data).map(key=>{return{episodes: Number(key),
                                            mean: data[key].mean,
                                            lb: data[key].lower_bound,
                                            ub: data[key].upper_bound
                                            }
                                      }
                              );
}

function lineChart(container_id, data){

  var width = document.getElementById(container_id).offsetWidth;
  var height = document.getElementById(container_id).offsetHeight;
  var margins = {top: 0.025 * height, right: 0.05 * width , bottom: 0.05 * height, left: 0.125 * width};

  var sVg = d3.select("#" + container_id)
              .append("svg")
              .attr("class", "chart-content")
              .append("g")
              .attr("transform", "translate(" + margins.left + "," + margins.top + ")");

  var x = d3.scaleLinear()
            .domain(d3.extent(data, d=>{return tweakLog(d.episodes);}))
            .range([0, width - margins.left - margins.right]);
          
  sVg
    .append('g')
    .attr("transform", "translate(0," + (height - margins.bottom - margins.top)+ ")")
    .call(d3.axisBottom(x)
            .tickFormat(function(d){return d3.format(".0e")(Math.pow(10,d))})
            .ticks(8));


  var numticks = Math.floor(height/35);
  var y = d3.scaleLinear()
            .domain([d3.min(data, d=>{return d.mean})-0.15, d3.max(data, d=>{return d.mean}) + 0.15])
            .range([height - margins.bottom - margins.top, 0]);
  
  sVg
    .append("g")
    .attr("class", "grid")
    .call(d3.axisLeft(y).ticks(numticks).tickSize(-width).tickFormat(""));
  
  sVg
    .append('g')
    .call(d3.axisLeft(y).ticks(numticks));

  sVg
    .append("path")
    .datum(data)
    .attr("class","confidence")
    .attr("d", d3.area()
                .x(function(d) { return x(tweakLog(d.episodes)) })
                .y0(function(d) { return y(d.lb) })
                .y1(function(d) { return y(d.ub) })
        )

  sVg
    .append("path")
    .datum(data)
    .attr("class", "main-line")
    .attr("d", d3.line()
                 .x(function(d){return x(tweakLog(d.episodes));})
                 .y(function(d){return y(d.mean)}));
  

  sVg.selectAll("dot")
      .data(data)
      .enter().append("circle")
      .attr("r", Math.floor(height/125))
      .attr("class", "fancy-circle")
      .attr("cx", function(d) { return x(tweakLog(d.episodes)); })
      .attr("cy", function(d) { return y(d.mean); });

      document.querySelectorAll(".fancy-circle").forEach(function(element){
        element.addEventListener("mouseover", function(e){
            console.log(getXInvert(e.target.getAttribute("cx")));
        });
    });

    function getXInvert(xval){
      if (xval != 0){
        return Math.pow(10,x.invert(xval));
      } else{
        return 0;
      }
      
    }

    function getYInvert(yval){
      return y.invert(yval);
    }
}

function tweakLog(value){
  var l = Math.log10(value);
  return isFinite(l) ? l : 0;
}

