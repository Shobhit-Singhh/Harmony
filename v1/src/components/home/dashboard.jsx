import React from 'react';
import { Heart, Users, Briefcase, GraduationCap } from 'lucide-react';

const ArcUI = ({ scores }) => {
    const GAP_DEGREES = 15;

    const createArc = (startAngle, sweepAngle, radius) => {
        const start = polarToCartesian(60, 60, radius, startAngle);
        const end = polarToCartesian(60, 60, radius, (startAngle - sweepAngle));
        const largeArcFlag = sweepAngle <= 180 ? "0" : "1";

        return [
            "M", start.x, start.y,
            "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
        ].join(" ");
    };

    const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
        const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
        return {
            x: centerX + (radius * Math.cos(angleInRadians)),
            y: centerY + (radius * Math.sin(angleInRadians))
        };
    };

    const calculateArcs = () => {
        let currentAngle = 0;
        const totalOfTotals = scores.reduce((sum, m) => sum + m.total, 0);

        return scores.map(metric => {
            const startAngle = currentAngle;
            const sweepAngle = (metric.total / totalOfTotals) * (360 - scores.length * GAP_DEGREES);
            const filledSweepAngle = (metric.value / metric.total) * sweepAngle;

            currentAngle += sweepAngle + GAP_DEGREES;

            return {
                ...metric,
                startAngle,
                sweepAngle,
                filledSweepAngle
            };
        });
    };

    const arcs = calculateArcs();
    const totalScore = scores.reduce((sum, m) => sum + m.value, 0);

    return (
        <div className="relative flex justify-center items-center">
            <svg className="w-48 h-48 md:w-64 md:h-64 lg:w-80 lg:h-80" viewBox="-40 -40 200 200">
                {arcs.map((arc) => (
                    <g key={arc.name}>
                        <path
                            d={createArc(arc.startAngle, arc.sweepAngle, 90)}
                            fill="none"
                            stroke="#fff"
                            strokeWidth="15"
                            strokeLinecap="round"
                            className="opacity-80"
                        />
                        <path
                            d={createArc(arc.startAngle, arc.filledSweepAngle, 90)}
                            fill="none"
                            stroke={arc.color}
                            strokeWidth="10"
                            strokeLinecap="round"
                        />
                    </g>
                ))}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
                <div className="text-4xl md:text-5xl lg:text-6xl font-bold">{totalScore}</div>
                <div className="text-base md:text-xl lg:text-2xl">Harmony</div>
            </div>
        </div>
    );
};

const MetricItem = ({ metric }) => (
    <div className="flex items-center justify-between text-white gap-2">
        <div className="flex items-center gap-2">
            <span className="text-primary">{metric.icon}</span>
            <span className="text-sm sm:text-base md:text-lg font-bold text-secondary-dark">{metric.name}</span>
        </div>
        <div className="text-secondary font-medium text-sm sm:text-base">
            {metric.value}/{metric.total}
        </div>
    </div>
);

const Dashboard = () => {
    const metrics = [
        { name: 'Relationship', value: 10, total: 25, icon: <Users size={20} />, color: '#22c55e' },
        { name: 'Growth', value: 15, total: 25, icon: <GraduationCap size={20} />, color: '#22c55e' },
        { name: 'Work', value: 20, total: 25, icon: <Briefcase size={20} />, color: '#22c55e' },
        { name: 'Health', value: 8, total: 25, icon: <Heart size={20} />, color: '#22c55e' },
    ];

    return (
        <div className="bg-primary/20 p-4 sm:p-6 md:p-8 
            rounded-none w-full max-w-full 
            min-h-20 border-y-2 border-primary/50">

            {/* Mobile layout (side by side) */}
            <div className="flex flex-row items-center justify-between md:hidden">
                <div className="flex-shrink-0">
                    <ArcUI scores={metrics} />
                </div>
                <div className="flex-1 space-y-2 ml-4">
                    {metrics.map((metric) => (
                        <MetricItem key={metric.name} metric={metric} />
                    ))}
                </div>
            </div>

            {/* Desktop layout (hero centered) */}
            <div className="hidden md:flex flex-col items-center justify-center">
                <div className="mb-8">
                    <ArcUI scores={metrics} />
                </div>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-4xl">
                    {metrics.map((metric) => (
                        <MetricItem key={metric.name} metric={metric} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;