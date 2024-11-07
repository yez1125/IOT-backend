// Test.js
import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Header } from "../component/components";

// 模擬不同感測器的初始範圍
const SENSOR_RANGES = {
    temperature: { min: 26, max: 30 }, // 溫度範圍
    humidity: { min: 40, max: 60 }, // 濕度範圍 (%)
    pm25: { min: 0, max: 100 }, // PM2.5 範圍 (µg/m³)
    co2: { min: 400, max: 2000 }, // CO2 範圍 (ppm)
    tvoc: { min: 0, max: 500 }, // TVOC 範圍 (ppb)
};

// 隨機產生範圍內的變動數值（較大幅度變化）
const getNextValue = (currentValue, sensorType) => {
    const range = SENSOR_RANGES[sensorType];
    const variance = (range.max - range.min) * 0.3; // 10% 的變動幅度
    const randomChange = (Math.random() - 0.5) * variance; // 產生 -variance 到 +variance 的隨機變動
    let newValue = currentValue + randomChange;

    // 確保新數值不超過範圍
    if (newValue > range.max) newValue = range.max;
    if (newValue < range.min) newValue = range.min;

    return newValue;
};

// 初始化 SVG 畫布大小（調整為較小的畫布，避免溢出）
const margin = { top: 20, right: 30, bottom: 30, left: 50 };
const width = 350 - margin.left - margin.right; // 調整寬度至 450
const height = 180 - margin.top - margin.bottom; // 調整高度至 180

const Test = () => {
    const chartRefs = useRef([]);

    // 建立每個圖表的初始化
    useEffect(() => {
        const sensors = ["temperature", "humidity", "pm25", "co2", "tvoc"];

        sensors.forEach((sensor, index) => {
            const svg = d3
                .select(chartRefs.current[index])
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            // 初始化 x 軸和 y 軸
            const x = d3.scaleLinear().range([0, width]);
            const y = d3.scaleLinear().range([height, 0]);

            // 設定 x 軸與 y 軸的初始範圍
            x.domain([0, 59]); // x 軸範圍為 0 到 59 秒
            y.domain([SENSOR_RANGES[sensor].min, SENSOR_RANGES[sensor].max]); // 根據感測器範圍設定 y 軸

            // 初始化 x 軸和 y 軸的座標軸
            svg.append("g")
                .attr("class", "x-axis")
                .attr("transform", `translate(0,${height})`);
            svg.append("g").attr("class", "y-axis");

            // 設定折線生成器
            const line = d3
                .line()
                .x((d, i) => x(i))
                .y((d) => y(d));

            // 初始化資料
            const data = Array.from(
                { length: 60 },
                () =>
                    (SENSOR_RANGES[sensor].min + SENSOR_RANGES[sensor].max) / 2
            ); // 初始值為中間值

            // 繪製初始折線圖
            svg.append("path")
                .datum(data)
                .attr("class", "line")
                .attr("d", line)
                .style("fill", "none")
                .style("stroke", "steelblue")
                .style("stroke-width", 2);

            // 更新 x 軸和 y 軸
            svg.select(".x-axis").call(d3.axisBottom(x));
            svg.select(".y-axis").call(d3.axisLeft(y));

            // 每秒更新圖表
            const interval = setInterval(() => {
                // 取得最新的數值
                const newValue = getNextValue(data[data.length - 1], sensor);

                // 更新資料：刪除最舊的資料，新增新的數據
                data.shift();
                data.push(newValue);

                // 更新折線圖
                svg.select(".line").datum(data).attr("d", line);

                // 更新座標軸
                svg.select(".x-axis").call(d3.axisBottom(x));
                svg.select(".y-axis").call(d3.axisLeft(y));
            }, 1000);

            return () => clearInterval(interval);
        });
    }, []);

    return (
        <>
            <Header />
            <div className="container my-3">
                <h1 className="text-center pb-3 fw-bold">即時監控</h1>
                {[
                    "Temperature °C",
                    "Humidity %",
                    "PM2.5 µg/m³",
                    "CO2 ppm",
                    "TVOC ppb",
                ].map((label, index) => (
                    <div
                        key={index}
                        className="container border py-4 px-0 mb-4 text-center"
                        style={{ overflow: "hidden" }}
                    >
                        <h2>{label}</h2>
                        <div
                            ref={(el) => (chartRefs.current[index] = el)}
                            style={{ width: "100%", height: "auto" }}
                        />
                    </div>
                ))}
            </div>
        </>
    );
};

export default Test;
