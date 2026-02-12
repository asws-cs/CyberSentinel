import React, { useState, useEffect, useRef } from 'react';
import { Paper, Typography, Box } from '@mui/material';

const LiveConsole = ({ scanId }) => {
    const [output, setOutput] = useState([]);
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const webSocketRef = useRef(null);
    const consoleEndRef = useRef(null);

    useEffect(() => {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/api/scan/ws/${scanId}`;
        
        webSocketRef.current = new WebSocket(wsUrl);

        webSocketRef.current.onopen = () => {
            setConnectionStatus('Connected');
            setOutput(prev => [...prev, '--- Connection Established ---']);
        };

        webSocketRef.current.onmessage = (event) => {
            setOutput(prev => [...prev, event.data]);
        };

        webSocketRef.current.onclose = () => {
            setConnectionStatus('Disconnected');
            setOutput(prev => [...prev, '--- Connection Closed ---']);
        };

        webSocketRef.current.onerror = (error) => {
            setConnectionStatus('Error');
            console.error("WebSocket Error: ", error);
            setOutput(prev => [...prev, '--- An error occurred with the connection ---']);
        };

        return () => {
            if (webSocketRef.current) {
                webSocketRef.current.close();
            }
        };
    }, [scanId]);

    useEffect(() => {
        // Scroll to the bottom of the console
        consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [output]);

    return (
        <Paper elevation={3} sx={{ height: '60vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6">Live Output</Typography>
                <Typography variant="body2" color={connectionStatus === 'Connected' ? 'success.main' : 'error.main'}>
                    {connectionStatus}
                </Typography>
            </Box>
            <Box component="pre" sx={{
                flexGrow: 1,
                overflowY: 'auto',
                p: 2,
                m: 0,
                backgroundColor: '#000',
                color: '#fff',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
            }}>
                {output.map((line, index) => (
                    <div key={index}>{`> ${line}`}</div>
                ))}
                <div ref={consoleEndRef} />
            </Box>
        </Paper>
    );
};

export default LiveConsole;
