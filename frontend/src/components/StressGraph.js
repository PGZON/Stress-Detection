import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StressGraph = ({ history, theme }) => {
  // Process history data for the graph
  const processData = () => {
    const labels = history.map(entry => {
      const date = new Date(entry.timestamp);
      return date.toLocaleTimeString();
    });

    const stressLevels = history.map(entry => {
      switch (entry.stress_level) {
        case 'Low': return 1;
        case 'Medium': return 2;
        case 'High': return 3;
        default: return 0;
      }
    });

    return {
      labels,
      datasets: [
        {
          label: 'Stress Level',
          data: stressLevels,
          borderColor: theme === 'dark' ? '#60A5FA' : '#2563EB',
          backgroundColor: theme === 'dark' ? 'rgba(96, 165, 250, 0.5)' : 'rgba(37, 99, 235, 0.5)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: theme === 'dark' ? '#fff' : '#000'
        }
      },
      title: {
        display: true,
        text: 'Stress Level Over Time',
        color: theme === 'dark' ? '#fff' : '#000'
      }
    },
    scales: {
      y: {
        min: 0,
        max: 3,
        ticks: {
          stepSize: 1,
          callback: function(value) {
            switch(value) {
              case 1: return 'Low';
              case 2: return 'Medium';
              case 3: return 'High';
              default: return '';
            }
          },
          color: theme === 'dark' ? '#fff' : '#000'
        },
        grid: {
          color: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        }
      },
      x: {
        grid: {
          color: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: theme === 'dark' ? '#fff' : '#000'
        }
      }
    }
  };

  return (
    <div className="w-full h-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
      <Line data={processData()} options={options} />
    </div>
  );
};

export default StressGraph; 