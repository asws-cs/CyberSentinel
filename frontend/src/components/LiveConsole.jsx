import React, { useState, useEffect, useRef } from 'react';
import { Paper, Typography, Box } from '@mui/material';

const LiveConsole = ({ scanId }) => {
    const [output, setOutput] = useState([]);
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const webSocketRef = useRef(null);
    const consoleEndRef = useRef(null);

    useEffect(() => {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Ensure the WebSocket URL correctly points to your backend's WebSocket endpoint
        // Example: ws://localhost:8000/api/scan/ws/{scanId} or wss://yourdomain.com/api/scan/ws/{scanId}
        const backendHost = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
        const wsUrl = `${wsProtocol}//${backendHost}/api/scan/ws/${scanId}`;
        
        webSocketRef.current = new WebSocket(wsUrl);

        webSocketRef.current.onopen = () => {
            setConnectionStatus('Connected');
            setOutput(prev => [...prev, { level: 'INFO', message: '--- Connection Established ---', timestamp: new Date().toISOString() }]);
        };

        webSocketRef.current.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                // Ensure the message has the expected structure
                if (message.level && message.message) {
                    setOutput(prev => [...prev, message]);
                } else {
                    console.warn("Received malformed message:", message);
                    setOutput(prev => [...prev, { level: 'DEBUG', message: `Malformed message: ${event.data}`, timestamp: new Date().toISOString() }]);
                }
            } catch (e) {
                console.error("Failed to parse WebSocket message:", event.data, e);
                setOutput(prev => [...prev, { level: 'ERROR', message: `Failed to parse message: ${event.data}`, timestamp: new Date().toISOString() }]);
            }
        };

        webSocketRef.current.onclose = () => {
            setConnectionStatus('Disconnected');
            setOutput(prev => [...prev, { level: 'INFO', message: '--- Connection Closed ---', timestamp: new Date().toISOString() }]);
        };

        webSocketRef.current.onerror = (error) => {
            setConnectionStatus('Error');
            console.error("WebSocket Error: ", error);
            setOutput(prev => [...prev, { level: 'ERROR', message: '--- An error occurred with the connection ---', timestamp: new Date().toISOString() }]);
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

    const getMessageColor = (level) => {
        switch (level) {
            case 'INFO':
                return 'lightgray';
            case 'WARNING':
                return 'yellow';
            case 'ERROR':
                return 'red';
            case 'DEBUG':
                return 'gray';
            default:
                return 'white';
        }
    };

    return (
        <Paper elevation={3} sx={{ height: '60vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#333' }}>
                <Typography variant="h6" sx={{ color: 'white' }}>Live Output</Typography>
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
                {output.map((msg, index) => (
                    <div key={index} style={{ color: getMessageColor(msg.level) }}>
                        <span style={{ color: 'gray' }}>{new Date(msg.timestamp).toLocaleTimeString()}</span>{' '}
                        <strong>[{msg.level}]</strong> {msg.message}
                    </div>
                ))}
                <div ref={consoleEndRef} />
            </Box>
        </Paper>
    );
};

export default LiveConsole;
