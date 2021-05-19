// Baserat på:
//      https://bl.ocks.org/steveharoz/8c3e2524079a8c440df60c1ab72b5d03
//      https://observablehq.com/@d3/force-directed-graph
//      http://bl.ocks.org/jose187/4733747

const render = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;

    let svg = d3.select("#chart").append("svg")
    .attr("width", width)
    .attr("height", height);

    fetch("/data/billboard_top_100_with_writers.json")
        .then(res => res.json())
        .then(raw => {
            const data = processData(raw);
            console.log(data)
            const links = data.links.map(d => Object.create(d));
            const nodes = data.nodes.map(d => Object.create(d));

            let sim = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id))
                .force("charge", d3.forceManyBody().strength(-10))
                .force("center", d3.forceCenter(width/2, height/2))
                .force("forceY",d3.forceY().strength(0.01))
            

            let link = svg.append("g")
                .attr("stroke", "black")
                .attr("stroke-width", 1)
                .selectAll("line")
                .data(links)
                .join("line")

            let node = svg.append("g")
                .selectAll("circle")
                .data(nodes)
                .join("circle")
                .on("mouseover",(_,d) => {
                    d3.select("#what").style("opacity",1)
                    d3.select("#what").text(`${d.type} -> ${d.name}`)
                })
            
                .on("mouseout",(_,d) => {
                    d3.select("#what").style("opacity",0)
                })

                .attr("stroke", "#000000")
                .attr("fill",d => d.type == "song" ? "#000000" : "#00ff88")
                .attr("r", 6)

            sim.on("tick", () => {
                link
                    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
        
                node
                    .attr("cx", d => d.x).attr("cy", d => d.y);
            })
        })
}

// Förvandlar min data efter exemplet i graph-gallery:
// https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_network.json
const processData = (d) => {
    let nodes = []
    let links = []

    for (const n in d) {
        let o = {"name": d[n]["song"],"type":"song"}
        let ids = pushToArray(o,nodes);

        for(const w in d[n]["writers"]){
            if(!exists(nodes, d[n]["writers"][w])){
                let wo = {"name": d[n]["writers"][w],"type":"writer"}
                let id = pushToArray(wo,nodes);
                let l = {"target": ids, "source": id}
                links.push(l);
            }else{
                let l = {"target": ids, "source": getId(nodes,d[n]["writers"][w])}
                links.push(l);
            }
        }
    }

    return {"nodes": nodes, "links": links};
}

const getId = (r,n) => {
    for(const i in r){
        if(r[i]["name"] == n){
            return r[i]["id"]
        }
    }
}

// Appendar n till a o fixar automagiskt id
const pushToArray = (n,a) => {
    const i = a.push(n);
    a[i-1]["id"] = i-1;
    
    return i-1;
}

// Kollar om w finns i d
const exists = (d,w) => {
    for(const n in d){
        if(d[n] == w){
            return true;
        }
    }

    return false;
}

render();