import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { motion } from 'framer-motion';

const RiskGauge = ({ score }) => {
    const scoreValue = score || 0;
    const circumference = 2 * Math.PI * 45; // r = 45
    const strokeDashoffset = circumference - (scoreValue / 100) * circumference;

    const getColor = (s) => {
        if (s > 80) return '#d32f2f'; // Critical
        if (s > 60) return '#f57c00'; // High
        if (s > 30) return '#fbc02d'; // Medium
        return '#388e3c'; // Low
    };

    return (
        <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>Overall Risk Score</Typography>
            <Box sx={{ position: 'relative', display: 'inline-flex', my: 2 }}>
                <svg width="120" height="120" viewBox="0 0 100 100">
                    <circle
                        cx="50"
                        cy="50"
                        r="45"
                        stroke="#424242"
                        strokeWidth="10"
                        fill="transparent"
                    />
                    <motion.circle
                        cx="50"
                        cy="50"
                        r="45"
                        stroke={getColor(scoreValue)}
                        strokeWidth="10"
                        fill="transparent"
                        strokeLinecap="round"
                        transform="rotate(-90 50 50)"
                        strokeDasharray={circumference}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.5, ease: "easeInOut" }}
                    />
                </svg>
                 <Box
                    sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Typography variant="h4" component="div" color="text.primary">
                        {Math.round(scoreValue)}
                    </Typography>
                </Box>
            </Box>
            <Typography variant="h5" style={{ color: getColor(scoreValue) }}>
                {scoreValue >= 81 ? "Critical" : scoreValue >= 61 ? "High" : scoreValue >= 31 ? "Medium" : "Low"}
            </Typography>
        </Paper>
    );
};

export default RiskGauge;
