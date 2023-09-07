"use strict";

let container = document.getElementById("layout");

let VIEW_WIDTH = 340,
    HEIGHT = VIEW_WIDTH,
    WIDTH = VIEW_WIDTH ;

let LINK_WIDTH = 0.5;
let ANGLE_INCREMENT = 45; // only multiples of 45 are allowed for label directions
let LABEL_DIRECTIONS = 8; // resulting in 8 possible directions
let DIRECTION_OFFSET_RIGHT = 6; // Offset for rotating right aligned text. Since 0 is up in the data, but starting position is right
let DIRECTION_OFFSET_LEFT = 2 // Offset for rotating left aligned text. Since 0 is up in the data, but starting position is left
let nodes, links, node, link, force;

function displayLayout(params) {

    nodes = params["nodes"];
    links = params["links"];

    // Create an SVG container to hold the visualization

    let svg = d3.select(container)
        .append('svg')
        .classed('layout-view', true)
        .attr('viewBox', [-20, -20, WIDTH, HEIGHT]);

    // Draw the links

    links = links.map(d => {
        let obj = {};
        let source = nodes.filter(e => e.id === d.source)[0];
        let target = nodes.filter(e => e.id === d.target)[0];
        obj['source'] = source;
        obj['target'] = target;
        obj['color'] = d.color;
        return obj;
    });

    prepareLinks();

    let drag = d3.drag()
        .on("drag", dragged)
        .on("start", dragstarted)
        .on("end", dragended);

    link = svg.selectAll('.link')
        .data(links)
        .enter()
        .append('line')
        .classed('link', true)
        .attr('stroke-width', 1)
        .style('stroke', d => d.color)
        .attr('transform', d => {
            let translation = calcTranslation(d.targetDistance, d.source, d.target);
            return "translate(" + translation.dx + "," + translation.dy + ")";
        });

    // Draw the nodes
    node = svg.selectAll('.node')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => {

            return "translate(" + d.x + "," + d.y + ")";
        });

    node.append("circle")
        .attr('r', d => d.size / 2);
        //.style("fill", d.color);

    node.append("text")
        .style("font-size", d => {
            return d.label_len
        } )
        .style("text-anchor", d => {
          if ([5,6,7].includes(Number(d.label_dir))){
              return "start"
          }
          return "end";
        } )
        .style("fill", d => d.color)
        //.attr("dx", 3)
        .attr("font-weight", 300)
        .attr("letter-spacing",   0.3 + "em")
        .text(function (d) {
            if (d.label.length > 9){
                const wordarray = d.label.split(" ");
                let linebreak_label = "";
                for (let i = 0; i<wordarray.length; i++){
                    linebreak_label = linebreak_label + wordarray[i] + "\n"
                }
                return linebreak_label;
            }
            else{
                return d.label;
            }

        })
        //.attr("font-family", "sans-serif")

        .attr('transform', d => {
            let angle
            if ([5,6,7].includes(Number(d.label_dir))){
                angle = ((Number(d.label_dir) + DIRECTION_OFFSET_LEFT) % LABEL_DIRECTIONS) * ANGLE_INCREMENT

            }else {
                angle = ((Number(d.label_dir) + DIRECTION_OFFSET_RIGHT) % LABEL_DIRECTIONS) * ANGLE_INCREMENT

            }
            return "rotate("+ angle + ")";
        })

    //node.append()
    force = d3.forceSimulation()
        .nodes(nodes)
        .on("tick", tick);


    node.call(drag);
}

function tick() {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
    node
        .attr('transform', d => {

        return "translate(" + d.x + "," + d.y + ")";
        });
}

/**
 * @param {number} targetDistance
 * @param {x, y} point0
 * @param {x, y} point1, two points that define a line segment
 * @returns
 * a translation {dx, dy} from the given line segment, such that the distance between
 * the given line segment and the translated line segment equals targetDistance
 */
function calcTranslation(targetDistance, point0, point1) {
    console.log(targetDistance)
    console.log("p0.x", point0.x, "p0.y", point0.y)
    console.log("p1.x", point1.x, "p1.y", point1.y)
    //targetDistance = 1;
    let x1_x0 = point1.x - point0.x,
        y1_y0 = point1.y - point0.y,
        x2_x0, y2_y0;
    if (y1_y0 === 0) {
        x2_x0 = 0;
        y2_y0 = targetDistance;
    } else if (x1_x0 === 0) {
        x2_x0 = - targetDistance;
        y2_y0 = 0;
    } else {
        let angle = Math.atan(x1_x0 / y1_y0);
        x2_x0 = - 2 * targetDistance * Math.cos(angle);
        y2_y0 = 0;
    }
    return {
        dx: x2_x0,
        dy: y2_y0
    };
}

/**
 * @description
 * Build an index to help handle the case of multiple links between two nodes
 */
function prepareLinks() {
    let linksFromNodes = {};
    links.forEach(function(val, idx) {
        let sid = val.source.id,
            tid = val.target.id,
            key = (sid < tid ? sid + "," + tid : tid + "," + sid);
        if (linksFromNodes[key] === undefined) {
            linksFromNodes[key] = [idx];
            val.multiIdx = 1;
        } else {
            val.multiIdx = linksFromNodes[key].push(idx);
        }
        // Calculate target link distance, from the index in the multiple-links array:
        // 1 -> 0, 2 -> 2, 3 -> -2, 4 -> 4, 5 -> -4, ...
        val.targetDistance = (val.multiIdx % 2 === 0 ? val.multiIdx * LINK_WIDTH
            : (- val.multiIdx + 1) * LINK_WIDTH);
    });
}

function dragged(d) {
    let point = {x: d3.event.x, y: d3.event.y}
    let closest = nodes.reduce((p, q) => distance(point, p) < distance(point, q) ? p : q);
    d.fx = closest.x;
    d.fy = closest.y;
}

function dragstarted(d) {
    if (!d3.event.active) {
        force.alphaTarget(0.3).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
}

function dragended(d) {
    if (!d3.event.active) {
        force.alphaTarget(0);
    }
    d.fx = null;
    d.fy = null;
}

function distance(p, q) {
    return Math.sqrt(Math.pow(p.x - q.x, 2) + Math.pow(p.y - q.y, 2));
}