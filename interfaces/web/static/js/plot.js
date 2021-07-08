function transformData(data){
  return Object.keys(data).map(key=>{return{episodes: Number(key),
                                            mean: data[key].mean,
                                            lb: data[key].lower_bound,
                                            up: data[key].upper_bound
                                            }
                                      }
                              );
}

function lineChart(container_id, data){
  console.log(tweakLog(0));
// set the dimensions and margins of the graph
var margin = {top: 10, right: 40, bottom: 30, left: 50},
    width = 500 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom
    /*width = document.getElementById(container_id).width,
    height = document.getElementById(container_id).height*/;

// append the svg object to the body of the page
var sVg = d3.select("#" + container_id)
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  // translate this svg element to leave some margin.
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// X scale and Axis
var x = d3.scaleLinear()
    .domain(d3.extent(data, d=>{return tweakLog(d.episodes);}))        // This is the min and the max of the data: 0 to 100 if percentages
    .range([0, width]);
           // This is the corresponding value I want in Pixel
sVg
  .append('g')
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x)
          .tickFormat(d3.format(".2s"))
          .ticks(10));

// X scale and Axis
var y = d3.scaleLinear()
    .domain([d3.min(data, d=>{return d.mean})-0.15, d3.max(data, d=>{return d.mean}) + 0.15])         // This is the min and the max of the data: 0 to 100 if percentages
    .range([height, 0]);       // This is the corresponding value I want in Pixel
sVg
  .append('g')
  .call(d3.axisLeft(y).ticks(21));

sVg.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "red")
  .attr("stroke-width", 2)
  .attr("d", d3.line()
             .x(function(d){return x(tweakLog(d.episodes));})
             .y(function(d){return y(d.mean)}));

}

function tweakLog(value){
  var l = Math.log10(value);
  return isFinite(l) ? l : 0;
}
