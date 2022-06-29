function displayLayout(params) {
    new Layout("layout", params);
}


class Layout {
    constructor(layoutId, params) {

        let container = document.getElementById(layoutId);

        let that = this;

        let MARGIN = 20,
            VIEW_WIDTH = Math.min(container.offsetHeight, container.offsetWidth) - 2 * MARGIN,
            HEIGHT = VIEW_WIDTH,
            WIDTH = VIEW_WIDTH;

        this.LINK_WIDTH = 2;

        this.nodes = params["nodes"];
        this.links = params["links"];

        let nodes = this.nodes.filter(d => d.size > 0)

        let y = d3.scaleLinear()
            .domain(d3.extent(nodes, d => d.y))
            .range([HEIGHT - MARGIN, MARGIN]);

        let x = d3.scaleLinear()
            .domain(d3.extent(nodes, d => d.x))
            .range([MARGIN, WIDTH - MARGIN]);

        // Create an SVG container to hold the visualization

        let svg = d3.select(container)
            .append('svg')
            .classed('example-svg', true)
            .attr('width', WIDTH)
            .attr('height', HEIGHT);

        // Draw the links

        let links = this.links.map(d => {
            let obj = {};
            let source = this.nodes.filter(e => e.id == d.source)[0];
            let target = this.nodes.filter(e => e.id == d.target)[0];
            obj['source'] = source;
            obj['target'] = target;
            return obj;
        })

        let link = svg.selectAll('.link')
            .data(links)
            .enter()
            .append('line')
            .classed('link', true)
            .attr('stroke-width', 3)
            .attr('x1', d => x(d.source.x))
            .attr('x2', d => x(d.target.x))
            .attr('y1', d => y(d.source.y))
            .attr('y2', d => y(d.target.y));

        // Draw the nodes

        let node = svg.selectAll('.node')
            .data(this.nodes)
            .enter()
            .append('circle')
            .classed('node', true)
            .attr('r', d => d.size)
            .attr('cx', d => x(d.x))
            .attr('cy', d => y(d.y));


/*
        // Create a force layout object

        let force = d3.forceSimulation()
            .nodes(this.nodes)
            .force("link", d3.forceLink().id(link => link.id))
            .force("center", d3.forceCenter(WIDTH / 2, WIDTH / 2))
            .on("tick", tick)

        let drag = d3
            .drag()
            .on("start", dragstart)

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
*/
    }
}

