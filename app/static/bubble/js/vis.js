let root = typeof exports !== 'undefined' && exports !== null ? exports : this;

let Bubbles = function() {
  // standard variables accessible to
  // the rest of the functions inside Bubbles
  let width = 980;
  let height = 510;
  let data = [];
  let node = null;
  let label = null;
  let margin = {top: 5, right: 0, bottom: 0, left: 0};
  // largest size for our bubbles
  let maxRadius = 65;
  // this scale will be used to size our bubbles
  let rScale = d3.scale.sqrt().range([0,maxRadius]);
  // I've abstracted the data value used to size each
  // into its own function. This should make it easy
  // to switch out the underlying dataset
  let rValue = d => parseInt(d.count);
  // function to define the 'id' of a data element
  //  - used to bind the data uniquely to the force nodes
  //   and for url creation
  //  - should make it easier to switch out dataset
  //   for your own
  let idValue = d => d.name;

  // function to define what to display in each bubble
  //  again, abstracted to ease migration to 
  //  a different dataset if desired
  let textValue = d => d.name;

  // constants to control how
  // collision look and act
  let collisionPadding = 4;
  let minCollisionRadius = 12;

  // variables that can be changed
  // to tweak how the force layout
  // acts
  // - jitter controls the 'jumpiness'
  //  of the collisions
  let jitter = 0.5;

  // ---
  // tweaks our dataset to get it into the
  // format we want
  // - for this dataset, we just need to
  //  ensure the count is a number
  // - for your own dataset, you might want
  //  to tweak a bit more
  // ---
  let transformData = function(rawData) {
    rawData.forEach(function(d) {
      d.count = parseInt(d.count);
      return rawData.sort(() => 0.5 - Math.random());
    });
    return rawData;
  };

  // ---
  // tick callback function will be executed for every
  // iteration of the force simulation
  // - moves force nodes towards their destinations
  // - deals with collisions of force nodes
  // - updates visual bubbles to reflect new force node locations
  // ---
  let tick = function(e) {
    let dampenedAlpha = e.alpha * 0.1;
    
    // Most of the work is done by the gravity and collide
    // functions.
    node
      .each(gravity(dampenedAlpha))
      .each(collide(jitter))
      .attr("transform", d => `translate(${d.x},${d.y})`);

    // As the labels are created in raw html and not svg, we need
    // to ensure we specify the 'px' for moving based on pixels
    return label
      .style("left", d => ((margin.left + d.x) - (d.dx / 2)) + "px")
      .style("top", d => ((margin.top + d.y) - (d.dy / 2)) + "px");
  };

  // The force variable is the force layout controlling the bubbles
  // here we disable gravity and charge as we implement custom versions
  // of gravity and collisions for this visualization
  let force = d3.layout.force()
    .gravity(0)
    .charge(0)
    .size([width, height])
    .on("tick", tick);

  // ---
  // Creates new chart function. This is the 'constructor' of our
  //  visualization
  // Check out http://bost.ocks.org/mike/chart/ 
  //  for a explanation and rational behind this function design
  // ---
  let chart = selection =>
    selection.each(function(rawData) {
      // first, get the data in the right format
      data = transformData(rawData);
      // setup the radius scale's domain now that
      // we have some data
      let maxDomainValue = d3.max(data, d => rValue(d));
      rScale.domain([0, maxDomainValue]);
      // a fancy way to setup svg element
      let svg = d3.select(this).selectAll("svg").data([data]);
      let svgEnter = svg.enter().append("svg");
      svg.attr("width", width + margin.left + margin.right );
      svg.attr("height", height + margin.top + margin.bottom );
      
      // node will be used to group the bubbles
      node = svgEnter.append("g").attr("id", "bubble-nodes")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // clickable background rect to clear the current selection
      node.append("rect")
        .attr("id", "bubble-background")
        .attr("width", width)
        .attr("height", height)
        .on("click", clear);

      // label is the container div for all the labels that sit on top of 
      // the bubbles
      // - remember that we are keeping the labels in plain html and 
      //  the bubbles in svg
      label = d3.select(this).selectAll("#bubble-labels").data([data])
        .enter()
        .append("div")
        .attr("id", "bubble-labels");

      update();

      // see if url includes an id already 
      hashchange();

      // automatically call hashchange when the url has changed
      return d3.select(window)
        .on("hashchange", hashchange);
    })
  ;

  // ---
  // update starts up the force directed layout and then
  // updates the nodes and labels
  // ---
  var update = function() {
    // add a radius to our data nodes that will serve to determine
    // when a collision has occurred. This uses the same scale as
    // the one used to size our bubbles, but it kicks up the minimum
    // size to make it so smaller bubbles have a slightly larger 
    // collision 'sphere'
    data.forEach((d,i) => d.forceR = Math.max(minCollisionRadius, rScale(rValue(d))));

    // start up the force layout
    force.nodes(data).start();

    // call our update methods to do the creation and layout work
    updateNodes();
    return updateLabels();
  };

  // ---
  // updateNodes creates a new bubble for each node in our dataset
  // ---
  var updateNodes = function() {
	  
    // here we are using the idValue function to uniquely bind our
    // data to the (currently) empty 'bubble-node selection'.
    // if you want to use your own data, you just need to modify what
    // idValue returns
    node = node.selectAll(".bubble-node").data(data, d => idValue(d));
    // we don't actually remove any nodes from our data in this example 
    // but if we did, this line of code would remove them from the
    // visualization as well
    node.exit().remove();

    // nodes are just links with circles inside.
    // the styling comes from the css
    return node.enter()
      .append("a")
      .attr("class", "bubble-node")
      .attr("xlink:href", d => `#${encodeURIComponent(idValue(d))}`)
      .call(force.drag)
      .call(connectEvents)
      .append("circle")
      .attr("r", d => rScale(rValue(d)));
  };

  // ---
  // updateLabels is more involved as we need to deal with getting the sizing
  // to work well with the font size
  // ---
  var updateLabels = function() {
    // as in updateNodes, we use idValue to define what the unique id for each data 
    // point is
    label = label.selectAll(".bubble-label").data(data, d => idValue(d));

    label.exit().remove();

    // labels are anchors with div's inside them
    // labelEnter holds our enter selection so it 
    // is easier to append multiple elements to this selection
    let labelEnter = label.enter().append("a")
      .attr("class", "bubble-label")
      .attr("href", d => `#${encodeURIComponent(idValue(d))}`)
      .call(force.drag)
      .call(connectEvents);

    labelEnter.append("div")
      .attr("class", "bubble-label-name")
      .text(d => textValue(d));

    labelEnter.append("div")
      .attr("class", "bubble-label-value")
      .text(d => rValue(d));

    // label font size is determined based on the size of the bubble
    // this sizing allows for a bit of overhang outside of the bubble
    // - remember to add the 'px' at the end as we are dealing with 
    //  styling divs
    label
      .style("font-size", d => Math.max(8, rScale(rValue(d) / 2)) + "px")
      .style("width", d => (2.5 * rScale(rValue(d))) + "px");

    // interesting hack to get the 'true' text width
    // - create a span inside the label
    // - add the text to this span
    // - use the span to compute the nodes 'dx' value
    //  which is how much to adjust the label by when
    //  positioning it
    // - remove the extra span
    label.append("span")
      .text(d => textValue(d))
      .each(function(d) { return d.dx = Math.max(2.5 * rScale(rValue(d)), this.getBoundingClientRect().width); })
      .remove();

    // reset the width of the label to the actual width
    label
      .style("width", d => d.dx + "px");
  
    // compute and store each nodes 'dy' value - the 
    // amount to shift the label down
    // 'this' inside of D3's each refers to the actual DOM element
    // connected to the data node
    return label.each(function(d) { return d.dy = this.getBoundingClientRect().height; });
  };

  // ---
  // custom gravity to skew the bubble placement
  // ---
  var gravity = function(alpha) {
    // start with the center of the display
    let cx = width / 2;
    let cy = height / 2;
    // use alpha to affect how much to push
    // towards the horizontal or vertical
    let ax = alpha / 8;
    let ay = alpha;

    // return a function that will modify the
    // node's x and y values
    return function(d) {
      d.x += (cx - d.x) * ax;
      return d.y += (cy - d.y) * ay;
    };
  };

  // ---
  // custom collision function to prevent
  // nodes from touching
  // This version is brute force
  // we could use quadtree to speed up implementation
  // (which is what Mike's original version does)
  // ---
  var collide = jitter =>
    // return a function that modifies
    // the x and y of a node
    d =>
      data.forEach(function(d2) {
        // check that we aren't comparing a node
        // with itself
        if (d !== d2) {
          // use distance formula to find distance
          // between two nodes
          let x = d.x - d2.x;
          let y = d.y - d2.y;
          let distance = Math.sqrt((x * x) + (y * y));
          // find current minimum space between two nodes
          // using the forceR that was set to match the 
          // visible radius of the nodes
          let minDistance = d.forceR + d2.forceR + collisionPadding;

          // if the current distance is less then the minimum
          // allowed then we need to push both nodes away from one another
          if (distance < minDistance) {
            // scale the distance based on the jitter variable
            distance = ((distance - minDistance) / distance) * jitter;
            // move our two nodes
            let moveX = x * distance;
            let moveY = y * distance;
            d.x -= moveX;
            d.y -= moveY;
            d2.x += moveX;
            return d2.y += moveY;
          }
        }
      })
    
  ;

  // ---
  // adds mouse events to element
  // ---
  var connectEvents = function(d) {
    d.on("click", click);
    d.on("mouseover", mouseover);
    return d.on("mouseout", mouseout);
  };

  // ---
  // clears currently selected bubble
  // ---
  var clear = () => location.replace("#");

  // ---
  // changes clicked bubble by modifying url
  // ---
  var click = function(d) {
    location.replace(`#${encodeURIComponent(idValue(d))}`);
    return d3.event.preventDefault();
  };

  // ---
  // called when url after the # changes
  // ---
  var hashchange = function() {
    let id = decodeURIComponent(location.hash.substring(1)).trim();
    return updateActive(id);
  };

  // ---
  // activates new node
  // ---
  var updateActive = function(id) {
    node.classed("bubble-selected", d => id === idValue(d));
    // if no node is selected, id will be empty
    if (id.length > 0) {
      return d3.select("#status").html(`<h3>The word <span class=\"active\">${id}</span> is now active</h3>`);
    } else {
      return d3.select("#status").html("<h3>No word is active</h3>");
    }
  };

  // ---
  // hover event
  // ---
  var mouseover = d => node.classed("bubble-hover", p => p === d);

  // ---
  // remove hover class
  // ---
  var mouseout = d => node.classed("bubble-hover", false);

  // ---
  // public getter/setter for jitter variable
  // ---
  chart.jitter = function(_) {
    if (!arguments.length) {
      return jitter;
    }
    jitter = _;
    force.start();
    return chart;
  };

  // ---
  // public getter/setter for height variable
  // ---
  chart.height = function(_) {
    if (!arguments.length) {
      return height;
    }
    height = _;
    return chart;
  };

  // ---
  // public getter/setter for width variable
  // ---
  chart.width = function(_) {
    if (!arguments.length) {
      return width;
    }
    width = _;
    return chart;
  };

  // ---
  // public getter/setter for radius function
  // ---
  chart.r = function(_) {
    if (!arguments.length) {
      return rValue;
    }
    rValue = _;
    return chart;
  };
  
  // final act of our main function is to
  // return the chart function we have created
  return chart;
};

// ---
// Helper function that simplifies the calling
// of our chart with it's data and div selector
// specified
// ---
root.plotData = (selector, data, plot) =>
  d3.select(selector)
    .datum(data)
    .call(plot)
;

let texts = [
  {key:"sherlock",file:"new_file.csv",name:"The Adventures of Sherlock Holmes"},
];

// ---
// jQuery document ready.
// ---
$(function() {
  // create a new Bubbles chart
  let plot = Bubbles();

  // ---
  // function that is called when
  // data is loaded
  // ---
  let display = data => plotData("#vis", data, plot);

  // we are storing the current text in the search component
  // just to make things easy
  let key = decodeURIComponent(location.search).replace("?","");
  let text = texts.filter(t => t.key === key)[0];

  // default to the first text if something gets messed up
  if (!text) {
    text = texts[0];
  }

  // select the current text in the drop-down
  $("#text-select").val(key);

  // bind change in jitter range slider
  // to update the plot's jitter
  d3.select("#jitter")
    .on("input", function() {
      return plot.jitter(parseFloat(this.output.value));
  });

  // bind change in drop down to change the
  // search url and reset the hash url
  d3.select("#text-select")
    .on("change", function(e) {
      key = $(this).val();
      location.replace("#");
      return location.search = encodeURIComponent(key);
  });

  // set the book title from the text name
  d3.select("#book-title").html(text.name);
 
  // load our data
  return d3.csv(`static/bubble/data/${text.file}`, display);
});

