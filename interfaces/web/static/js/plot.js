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
      .attr("id", function(d){return d.episodes})
      .attr("cx", function(d) { return x(tweakLog(d.episodes)); })
      .attr("cy", function(d) { return y(d.mean); });

      document.querySelectorAll(".fancy-circle").forEach(function(element){
        element.addEventListener("mouseover", function(e){
           var target = filterArrayObjs(data, e.target.getAttribute("id"))[0];
           var tooltip = renderTooltip(target);

           tooltip.style.top = e.layerY + "px";
           var tooltipWidth = Number(getComputedStyle(tooltip).maxWidth.replace(/px$/, ''));
           var pagepos = e.layerX + 200;
           var screenWidth = width*0.95;
           var ratio = (function(){
             var minMax = (screen.width-364)/(1672-364);
             return 0.6 + (0.75-0.6)*minMax;
           })();
           if (pagepos < screenWidth){
              tooltip.style.left = e.layerX + "px";
           }else if(pagepos >= screenWidth){
            tooltip.style.left = (e.layerX*ratio) + "px";
           }
            
           
           document.getElementById(container_id).appendChild(tooltip);

           
        });

        element.addEventListener("mouseout", function(e){
            document.querySelectorAll(".tooltip").forEach(function(element){
              var ratio = (function(){
                var minMax = (screen.width-364)/(1672-364);
                return minMax;
              })();
              element.addEventListener("click",function(e){element.remove()});
              setTimeout(()=>{element.remove()}, 500/ratio);});
        });

    });
}

function tweakLog(value){
  var l = Math.log10(value);
  return isFinite(l) ? l : 0;
}

function renderTooltip(obj) {
  var container = document.createElement("div");
  container.setAttribute("class", "tooltip");
  var textNodes = document.createElement("div");

  var episodesText = document.createElement("p");
  episodesText.innerText = "Num. Episodes:";
  var meanText = document.createElement("p");
  meanText.innerText = "Mean(€):";
  var lbText = document.createElement("p");
  lbText.innerText = "CI LB(95%)(€):";
  var ubText = document.createElement("p");
  ubText.innerText = "CI UB(95%)(€):"

  textNodes.appendChild(episodesText);
  textNodes.appendChild(meanText);
  textNodes.appendChild(lbText);
  textNodes.appendChild(ubText);
  
  var ValueNodes = document.createElement("div");

  var episodesValue = document.createElement("p");
  episodesValue.innerText = niceNumber(obj.episodes, 0);
  var meanValue = document.createElement("p");
  meanValue.innerText = niceNumber(obj.mean, 4);
  var lbValue = document.createElement("p");
  lbValue.innerText = niceNumber(obj.lb, 4);
  var ubValue = document.createElement("p");
  ubValue.innerText = niceNumber(obj.ub,4);         
  
  ValueNodes.appendChild(episodesValue);
  ValueNodes.appendChild(meanValue);
  ValueNodes.appendChild(lbValue);
  ValueNodes.appendChild(ubValue);

  container.appendChild(textNodes);
  container.appendChild(ValueNodes);

  return container;
}

function filterArrayObjs(data, value){
  return data.filter(function (el){return el.episodes == value;})
}
