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

function transformData(data){
  return Object.keys(data).map(key=>{return{episodes: Number(key),
                                            mean: data[key].mean,
                                            lb: data[key].lower_bound,
                                            ub: data[key].upper_bound
                                            }
                                      }
                              );
}

function transformMatrix(data){
  var player_min=4, dealer_min=2;
  var new_data = data.map((v, i, a)=>{
    var player_val = player_min + i;
    var mat = v.map((val, ind, arr)=>{
      var dealer_val = dealer_min + ind;
      return [{"player": player_val,"dealer": dealer_val, "ace": false,"action":val[0]},
              {"player": player_val,"dealer": dealer_val, "ace": true,"action":val[1]}]
   });

    return mat.flat();
  });
   return new_data.flat();
}

function marginScaler(value, minMargin, maxMargin, minWidth, maxWidth){
  var p = (value-minWidth)/(maxWidth-minWidth);
  return minMargin + p * (maxMargin-minMargin)
}

function getMargins(width, height){ return {top: 0.025 * height,
                                            right: 0.05 * width ,
                                            bottom: 0.05 * height,
                                            left: width * marginScaler(width,0.1,0.125,428,1836)};
}

function lineChart(container_id, data){

  var width = document.getElementById(container_id).offsetWidth;
  var height = document.getElementById(container_id).offsetHeight * marginScaler(screen.width,0.9,0.8,1836,428);
  var margins = getMargins(width, height);

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

    sVg.append("text")             
    .attr("transform",
       "translate(" + (width/2) + " ," + 
                      (height+20) + ")")
    .style("text-anchor", "middle")
    .attr("fill", "#ffffff")
    .text("Episodes - Log scale");

}

function heatMap(container_id, data, ace){

  var data = data.filter(function(d){return d.ace == ace});
  var width = document.getElementById(container_id).offsetWidth ;
  var height = document.getElementById(container_id).offsetHeight * marginScaler(screen.width,0.9,0.8,1836,428);
  var margins = getMargins(width, height);

  var sVg = d3.select("#" + container_id)
  .append("svg")
  .attr("class", "chart-content")
  .append("g")
  .attr("transform", "translate(" + margins.left + "," + margins.top + ")");

  var Ys = [...new Set(data.map((v,i,a)=>{return v.player}))];
  var Xs = [...new Set(data.map((v,i,a)=>{return v.dealer}))];

  var x = d3.scaleBand()
            .domain(Xs)
            .range([0, width - margins.left - margins.right])
            .padding(0.01);


  sVg.append("g")
     .attr("transform", "translate(0," + (height - margins.top - margins.bottom) + ")")
     .call(d3.axisBottom(x));

  var y = d3.scaleBand()
            .domain(Ys)
            .range([height - margins.top - margins.bottom, 0])
            .padding(0.01);
  
  sVg.append("g")
     .call(d3.axisLeft(y));
  
  var colourScale = d3.scaleLinear()
                      .domain([0, 1])
                      .range(["#687bd0eb", "#800416"]);

  sVg.selectAll()
     .data(data, function(d) {return d.dealer+':'+d.player;})
     .enter()
     .append("rect")
     .attr("x", function(d) { return x(d.dealer) })
     .attr("y", function(d) { return y(d.player) })
     .attr("width", x.bandwidth())
     .attr("height", y.bandwidth())
     .attr("id",function(d){if(ace){return d.player+"-"+d.dealer+"-1";}else{return d.player+"-"+d.dealer+"-0";}})
     .style("fill", function(d) { return colourScale(d.action)}); 

     
      buildSidebar(document.getElementById(container_id));
     
    

    sVg.append("text")             
        .attr("transform",
           "translate(" + (width/2) + " ," + 
                          (height+15) + ")")
        .style("text-anchor", "middle")
        .attr("fill", "#ffffff")
        .text("Dealer's value");
     
     sVg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margins.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .attr("fill", "#ffffff")
        .style("text-anchor", "middle")
        .text("Player's value");      
}

function buildSidebar(node){
  var sidebar = document.createElement("div")
  sidebar.setAttribute("class", "sidebar h-sidebar");

  var rel_container = document.createElement("div");
  rel_container.setAttribute("class", "relbar")
  sidebar.append(rel_container);

  var hit = document.createElement("div");
  hit.setAttribute("class", "sidebar-value hit-bar");
  hit.innerHTML = '<p>HIT</p>';
  rel_container.appendChild(hit);

  var stand = document.createElement("div");
  stand.setAttribute("class", "sidebar-value stand-bar");
  stand.innerHTML = '<p>STAND</p>';
  rel_container.appendChild(stand);
  
  node.appendChild(sidebar);
  }

