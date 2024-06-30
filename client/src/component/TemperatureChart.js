import { useRef, useEffect } from "react";
import * as d3 from "d3";

const TemperatureChart = ({ data }) => {
  const svgRef = useRef();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    const { width, height } = svg.node().getBoundingClientRect();

    // 設置圖表的邊距
    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // 設置x和y比例尺
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(data, d => d.time))
      .range([0, innerWidth]);

    const yScale = d3
      .scaleLinear()
      .domain([d3.min(data, d => d.temperature), d3.max(data, d => d.temperature)])
      .range([innerHeight, 0]);

    // 設置折線生成器
    const lineGenerator = d3
      .line()
      .x((d) => xScale(d.time))
      .y((d) => yScale(d.temperature))
      .curve(d3.curveMonotoneX);

    // 清空之前的內容
    svg.selectAll("*").remove();

    // 創建圖表的主群組元素
    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 添加x軸
    g.append("g")
      .call(d3.axisBottom(xScale))
      .attr("transform", `translate(0,${innerHeight})`);

    // 添加y軸
    g.append("g").call(d3.axisLeft(yScale));

    // 繪製折線
    g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 2)
      .attr("d", lineGenerator);

    // 添加數據點
    g.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("cx", (d) => xScale(d.time))
      .attr("cy", (d) => yScale(d.temperature))
      .attr("r", 5)
      .attr("fill", "steelblue")
      .on("mouseover", (event, d) => {
        d3.select(event.target).attr("r", 10).attr("fill", "red");
      })
      .on("mouseout", (event, d) => {
        d3.select(event.target).attr("r", 5).attr("fill", "steelblue");
      });
  }, [data]);

  return <svg ref={svgRef} style={{ width: "100%", height: "500px" }}></svg>;
};

export default TemperatureChart;
