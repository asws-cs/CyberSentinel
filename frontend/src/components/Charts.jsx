import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export const ScansByDayChart = ({ scans }) => {
    const data = scans?.reduce((acc, scan) => {
        const date = new Date(scan.created_at).toLocaleDateString();
        acc[date] = (acc[date] || 0) + 1;
        return acc;
    }, {});

    const chartData = {
        labels: Object.keys(data || {}),
        datasets: [{
            label: '# of Scans',
            data: Object.values(data || {}),
            backgroundColor: 'rgba(63, 81, 181, 0.5)',
            borderColor: 'rgba(63, 81, 181, 1)',
            borderWidth: 1,
        }],
    };

    return (
        <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6">Scans per Day</Typography>
            <Bar data={chartData} />
        </Paper>
    );
};

export const ScanModeDistributionChart = ({ scans }) => {
    const data = scans?.reduce((acc, scan) => {
        acc[scan.scan_mode] = (acc[scan.scan_mode] || 0) + 1;
        return acc;
    }, {});

    const chartData = {
        labels: Object.keys(data || {}),
        datasets: [{
            label: 'Scan Mode Distribution',
            data: Object.values(data || {}),
            backgroundColor: [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
            ],
            borderWidth: 1,
        }],
    };
    
    return (
         <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6">Scan Modes</Typography>
            <Box sx={{height: 300, display: 'flex', justifyContent: 'center'}}>
                <Pie data={chartData} options={{ maintainAspectRatio: false }}/>
            </Box>
        </Paper>
    )
}
