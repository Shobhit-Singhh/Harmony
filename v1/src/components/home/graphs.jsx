import React from "react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const GraphCards = () => {
    // Generate last 7 days of data
    const dates = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    });

    const healthData = {
        heartRate: dates.map(date => ({
            date,
            value: Math.floor(60 + Math.random() * 30) // 60-90 bpm
        })),
        sleep: dates.map(date => ({
            date,
            value: 5 + Math.random() * 4 // 5-9 hours
        })),
        activity: dates.map(date => ({
            date,
            value: Math.floor(2000 + Math.random() * 6000) // 2000-8000 steps
        })),
        calories: dates.map(date => ({
            date,
            value: Math.floor(1800 + Math.random() * 800) // 1800-2600 calories
        })),
        weight: dates.map(date => ({
            date,
            value: (70 + Math.random()).toFixed(1) // Around 70kg with small variations
        })),
        bloodPressure: dates.map(date => ({
            date,
            systolic: Math.floor(110 + Math.random() * 30), // 110-140 systolic
            diastolic: Math.floor(70 + Math.random() * 20) // 70-90 diastolic
        }))
    };

    const graphs = [
        {
            title: "Heart Rate",
            type: "line",
            data: healthData.heartRate,
            color: "#FF6B6B",
            unit: "bpm"
        },
        {
            title: "Sleep Pattern",
            type: "bar",
            data: healthData.sleep,
            color: "#4ECDC4",
            unit: "hours"
        },
        {
            title: "Activity Level",
            type: "area",
            data: healthData.activity,
            color: "#45B7D1",
            unit: "steps"
        },
        {
            title: "Calories Burned",
            type: "line",
            data: healthData.calories,
            color: "#96CEB4",
            unit: "kcal"
        },
        {
            title: "Weight",
            type: "line",
            data: healthData.weight,
            color: "#D4A5A5",
            unit: "kg"
        },
        {
            title: "Blood Pressure",
            type: "line",
            data: healthData.bloodPressure,
            color: "#FF9999",
            unit: "mmHg"
        }
    ];

    const renderGraph = (graph) => {
        const commonProps = {
            width: "100%",
            height: "100%",
            data: graph.data,
            margin: { top: 5, right: 5, bottom: 5, left: 5 }
        };

        switch (graph.type) {
            case "line":
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'white', border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
                            formatter={(value) => [`${value} ${graph.unit}`, graph.title]}
                        />
                        {graph.title === "Blood Pressure" ? (
                            <>
                                <Line type="monotone" dataKey="systolic" stroke={graph.color} dot={false} />
                                <Line type="monotone" dataKey="diastolic" stroke={`${graph.color}88`} dot={false} />
                            </>
                        ) : (
                            <Line type="monotone" dataKey="value" stroke={graph.color} dot={false} />
                        )}
                    </LineChart>
                );
            case "bar":
                return (
                    <BarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'white', border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
                            formatter={(value) => [`${value} ${graph.unit}`, graph.title]}
                        />
                        <Bar dataKey="value" fill={graph.color} radius={[4, 4, 0, 0]} />
                    </BarChart>
                );
            case "area":
                return (
                    <AreaChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'white', border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
                            formatter={(value) => [`${value} ${graph.unit}`, graph.title]}
                        />
                        <Area type="monotone" dataKey="value" fill={`${graph.color}33`} stroke={graph.color} />
                    </AreaChart>
                );
            default:
                return null;
        }
    };

    return (
        <div className="">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-medium text-gray-800">Health Metrics</h2>
                <span className="text-gray-400">→</span>
            </div>
            <div className="grid grid-flow-col auto-cols-[minmax(350px,_1fr)] sm:grid-rows-3 md:grid-rows-2 lg:grid-rows-1 overflow-x-auto">
                {graphs.map((graph, index) => (
                    <div key={index} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
                        <h3 className=" flex flex-col text-base font-medium mb-2 text-gray-700 items-center ">{graph.title}</h3>
                        <div className="h-52">
                            <ResponsiveContainer>
                                {renderGraph(graph)}
                            </ResponsiveContainer>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GraphCards;