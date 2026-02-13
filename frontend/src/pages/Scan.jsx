import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Container, Typography, Paper, TextField, Button, Grid, CircularProgress, Alert, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, Box, FormGroup, Switch } from '@mui/material';

import { startScan, getScanById, getLegalDisclaimer, getReportsByScanId } from '../services/api';
import RiskGauge from '../components/RiskGauge';
import LiveConsole from '../components/LiveConsole';

const availableTools = [
    { name: 'nmap_scan', label: 'Nmap Port Scan', offensive: false },
    { name: 'ssl_scan', label: 'SSL/TLS Analysis', offensive: false },
    { name: 'header_analysis', label: 'Header Analysis', offensive: false },
    { name: 'dir_discovery', label: 'Directory Discovery', offensive: true },
    { name: 'sqlmap_scan', label: 'SQL Injection (SQLMap)', offensive: true },
    { name: 'xsser_scan', label: 'Cross-Site Scripting (XSSer)', offensive: true },
    { name: 'nikto_scan', label: 'Nikto Scan', offensive: true },
    { name: 'sql_injection_test', label: 'SQL Injection (Basic)', offensive: true },
    { name: 'xss_test', label: 'XSS (Basic)', offensive: true },
];

const Scan = () => {
    const { scanId } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Form state
    const [target, setTarget] = useState('');
    const [scanMode, setScanMode] = useState('defensive');
    const [scanDepth, setScanDepth] = useState('normal');
    const [legalAccepted, setLegalAccepted] = useState(false);
    const [aggressiveMode, setAggressiveMode] = useState(false);
    const [enabledTools, setEnabledTools] = useState(() => {
        const initialTools = {};
        availableTools.forEach(t => initialTools[t.name] = !t.offensive); // Enable non-offensive by default
        return initialTools;
    });

    // Fetch existing scan data if scanId is present
    const { data: scanData, isLoading: isLoadingScan, isError: isErrorScan } = useQuery({
        queryKey: ['scan', scanId],
        queryFn: () => getScanById(scanId),
        enabled: !!scanId,
    });

    const { data: reportsData, isLoading: isLoadingReports } = useQuery({
        queryKey: ['reports', scanId],
        queryFn: () => getReportsByScanId(scanId),
        enabled: !!scanId && scanData?.status === 'completed',
    });

    const { data: legalDisclaimer, isLoading: isLoadingDisclaimer } = useQuery({
        queryKey: ['legalDisclaimer'],
        queryFn: getLegalDisclaimer,
        enabled: scanMode === 'offensive',
    });

    const mutation = useMutation({
        mutationFn: (scanConfig) => startScan(scanConfig, legalAccepted),
        onSuccess: (data) => {
            queryClient.invalidateQueries(['scans']);
            navigate(`/scan/${data.scan_id}`);
        },
    });

    const handleToolToggle = (toolName) => {
        setEnabledTools(prev => ({ ...prev, [toolName]: !prev[toolName] }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const selectedTools = Object.entries(enabledTools)
            .filter(([, isEnabled]) => isEnabled)
            .map(([toolName]) => toolName);
        
        mutation.mutate({ 
            target, 
            scan_mode: scanMode, 
            scan_depth: scanDepth,
            aggressive: aggressiveMode,
            tools: selectedTools
        });
    };
    
    useEffect(() => {
        if (scanMode === 'defensive') {
            setEnabledTools(currentTools => {
                const newTools = { ...currentTools };
                availableTools.forEach(tool => {
                    if (tool.offensive) {
                        newTools[tool.name] = false;
                    }
                });
                return newTools;
            });
        }
    }, [scanMode]);


    if (scanId) {
        if (isLoadingScan) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}><CircularProgress /></div>;
        if (isErrorScan) return <Alert severity="error">Error loading scan data.</Alert>;

        const riskScore = reportsData?.[0]?.risk_score || 0;

        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Paper elevation={3} sx={{ p: 3, backgroundColor: '#2c2c2c' }}>
                    <Typography variant="h4" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                        Scan Report: {scanData.target}
                    </Typography>
                    <Grid container spacing={4}>
                        <Grid item xs={12} lg={8}>
                            <LiveConsole scanId={scanId} />
                        </Grid>
                        <Grid item xs={12} lg={4}>
                            <Paper elevation={6} sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', backgroundColor: '#333' }}>
                                <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>Risk Score</Typography>
                                <RiskGauge score={scanData.status === 'completed' ? riskScore : 0} />
                                <Typography variant="body1" sx={{ color: 'lightgray', mt: 2 }}>
                                    Status: <span style={{ color: scanData.status === 'completed' ? 'lightgreen' : 'yellow', fontWeight: 'bold' }}>{scanData.status}</span>
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                </Paper>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg">
            <Paper elevation={3} sx={{ p: { xs: 2, sm: 3, md: 5 }, mt: 4, borderRadius: '15px', backgroundColor: 'rgba(45, 45, 45, 0.9)' }}>
                <Typography variant="h3" gutterBottom component="h1" align="center" sx={{ fontWeight: 'bold', color: 'white' }}>
                    Cyber Sentinel
                </Typography>
                <Typography variant="h6" align="center" sx={{ mb: 4, color: 'lightgray' }}>
                    Your automated security scanner
                </Typography>
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={4}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Target (URL, Domain, or IP)"
                                value={target}
                                onChange={(e) => setTarget(e.target.value)}
                                required
                                InputLabelProps={{ style: { color: 'white' } }}
                                InputProps={{ style: { color: 'white', backgroundColor: '#333' } }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel sx={{ color: 'white' }}>Scan Mode</InputLabel>
                                <Select value={scanMode} label="Scan Mode" onChange={(e) => setScanMode(e.target.value)} sx={{ color: 'white', backgroundColor: '#333' }}>
                                    <MenuItem value="defensive">Defensive</MenuItem>
                                    <MenuItem value="offensive">Offensive</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel sx={{ color: 'white' }}>Scan Depth</InputLabel>
                                <Select value={scanDepth} label="Scan Depth" onChange={(e) => setScanDepth(e.target.value)} sx={{ color: 'white', backgroundColor: '#333' }}>
                                    <MenuItem value="normal">Normal</MenuItem>
                                    <MenuItem value="deep">Deep</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>

                        <Grid item xs={12}>
                             <Typography variant="h5" sx={{ color: 'white', mt: 2, mb: 1 }}>Tool Selection</Typography>
                             <Paper elevation={2} sx={{ p: 2, backgroundColor: '#333', borderRadius: '8px' }}>
                                 <FormGroup row>
                                    {availableTools.map(tool => (
                                         <FormControlLabel
                                            key={tool.name}
                                            control={<Switch checked={!!enabledTools[tool.name]} onChange={() => handleToolToggle(tool.name)} color="primary" />}
                                            label={<Typography sx={{ color: 'white' }}>{tool.label}</Typography>}
                                            disabled={scanMode === 'defensive' && tool.offensive}
                                         />
                                    ))}
                                 </FormGroup>
                             </Paper>
                        </Grid>
                        
                        <Grid item xs={12}>
                             <FormControlLabel
                                control={<Switch checked={aggressiveMode} onChange={(e) => setAggressiveMode(e.target.checked)} />}
                                label={<Typography sx={{ color: 'white' }}>Aggressive Mode (More comprehensive, but may be slower and noisier)</Typography>}
                              />
                        </Grid>

                        {scanMode === 'offensive' && (
                            <Grid item xs={12}>
                                <Paper variant="outlined" sx={{ p: 2, mt: 2, borderRadius: '8px', borderColor: 'rgba(255, 82, 82, 0.5)', backgroundColor: 'rgba(255, 82, 82, 0.1)' }}>
                                    <Typography variant="h6" color="error">Legal & Ethical Use Policy</Typography>
                                    {isLoadingDisclaimer ? <div style={{ display: 'flex', justifyContent: 'center' }}><CircularProgress size={20} /></div> : <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem', color: 'lightgray' }}>{legalDisclaimer?.disclaimer}</pre>}
                                    <FormControlLabel
                                        control={<Checkbox checked={legalAccepted} onChange={(e) => setLegalAccepted(e.target.checked)} sx={{ color: 'white' }} />}
                                        label={<Typography sx={{ color: 'white' }}>I have explicit, authorized permission to perform this scan and agree to the terms.</Typography>}
                                    />
                                </Paper>
                            </Grid>
                        )}

                        <Grid item xs={12}>
                            <Button
                                type="submit"
                                variant="contained"
                                size="large"
                                fullWidth
                                disabled={mutation.isPending || (scanMode === 'offensive' && !legalAccepted)}
                                sx={{ 
                                    p: 2, 
                                    fontWeight: 'bold',
                                    fontSize: '1.2rem',
                                    background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                                    transition: 'transform 0.2s',
                                    '&:hover': {
                                        transform: 'scale(1.02)'
                                    }
                                }}
                            >
                                {mutation.isPending ? <CircularProgress size={24} color="inherit" /> : 'Start Scan'}
                            </Button>
                        </Grid>
                    </Grid>
                </form>
                {mutation.isError && (
                    <Alert severity="error" sx={{ mt: 3, borderRadius: '8px' }}>
                        Failed to start scan: {mutation.error.response?.data?.detail?.message || mutation.error.message}
                    </Alert>
                )}
            </Paper>
        </Container>
    );
};

export default Scan;
