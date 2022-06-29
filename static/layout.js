function displayLayout(params) {
    new Layout("layout", params);
}


class Layout {
    constructor(layoutId, params) {

        let container = document.getElementById(layoutId);

        let that = this;

        let MARGIN = 10,
            VIEW_WIDTH = Math.min(container.offsetHeight, container.offsetWidth) - 2 * MARGIN,
            HEIGHT = VIEW_WIDTH,
            WIDTH = VIEW_WIDTH;

        this.LINK_WIDTH = 2;

        this.nodes = params["nodes"];
        this.links = params["links"];

        console.log(this.nodes);
        console.log(this.links);

        // Create an SVG container to hold the visualization

        let svg = d3.select(container)
            .append('svg')
            .classed('example-svg', true)
            .attr('width', WIDTH)
            .attr('height', HEIGHT);

        // Draw the links

        let link = svg.selectAll('.link')
            .data(this.links)
            .enter()
            .append('line')
            .classed('link', true);

        // Draw the nodes

        let node = svg.selectAll('.node')
            .data(this.nodes)
            .enter()
            .append('circle')
            .classed('node', true)
            .attr('r', WIDTH / 100)
            .classed("fixed", d => d.fx !== undefined);


        // Create a force layout object

        let force = d3.forceSimulation()
            .nodes(this.nodes)
            .force("link", d3.forceLink().id(link => link.id))
            .force("center", d3.forceCenter(WIDTH / 2, WIDTH / 2))
            .on("tick", tick)

        let drag = d3
            .drag()
            .on("start", dragstart)
            .on("drag", dragged);

        node.call(drag).on("click", click);

        function tick() {
            link.attr("x1", function (d) {
                return d.source.x;
            })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node.attr("cx", function (d) {
                return d.x;
            })
                .attr("cy", function (d) {
                    return d.y;
                });
        }

        function click(event, d) {
            delete d.fx;
            delete d.fy;
            d3.select(this).classed("fixed", false);
            simulation.alpha(1).restart();
        }

        function dragstart() {
            d3.select(this).classed("fixed", true);
        }

        function dragged(event, d) {
            d.fx = clamp(event.x, 0, WIDTH);
            d.fy = clamp(event.y, 0, HEIGHT);
            simulation.alpha(1).restart();
        }

        function clamp(x, lo, hi) {
            return x < lo ? lo : x > hi ? hi : x;
        }
    }
}

