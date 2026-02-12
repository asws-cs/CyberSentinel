import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Container, Typography, Paper, TextField, Button, Grid, CircularProgress, Alert, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, Box } from '@mui/material';

import { startScan, getScanById, getLegalDisclaimer, getReportsByScanId } from '../services/api';
import RiskGauge from '../components/RiskGauge';

const Scan = () => {
    const { scanId } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Form state
    const [target, setTarget] = useState('');
    const [scanMode, setScanMode] = useState('defensive');
    const [scanDepth, setScanDepth] = useState('normal');
    const [legalAccepted, setLegalAccepted] = useState(false);

    // Fetch existing scan data if scanId is present
    const { data: scanData, isLoading: isLoadingScan, isError: isErrorScan } = useQuery({
        queryKey: ['scan', scanId],
        queryFn: () => getScanById(scanId),
        enabled: !!scanId, // Only run query if scanId is present
        refetchInterval: (data) => (data?.status === 'completed' ? false : 5000),
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

    const handleSubmit = (e) => {
        e.preventDefault();
        mutation.mutate({ target, scan_mode: scanMode, scan_depth: scanDepth });
    };

    if (scanId) {
        if (isLoadingScan) return <CircularProgress />;
        if (isErrorScan) return <Alert severity="error">Error loading scan data.</Alert>;

        const riskScore = reportsData?.[0]?.risk_score || 0;

        return (
            <Container maxWidth="lg">
                <Typography variant="h4" gutterBottom>Scan Report: {scanData.target}</Typography>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={8}>
                        <LiveConsole scanId={scanId} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                         <RiskGauge score={scanData.status === 'completed' ? riskScore : 0} />
                        {/* More result details would go here */}
                    </Grid>
                </Grid>
            </Container>
        );
    }

    return (
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
                <Typography variant="h4" gutterBottom component="h1">
                    Launch New Scan
                </Typography>
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Target (URL, Domain, or IP)"
                                value={target}
                                onChange={(e) => setTarget(e.target.value)}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>Scan Mode</InputLabel>
                                <Select value={scanMode} label="Scan Mode" onChange={(e) => setScanMode(e.target.value)}>
                                    <MenuItem value="defensive">Defensive</MenuItem>
                                    <MenuItem value="offensive">Offensive</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>Scan Depth</InputLabel>
                                <Select value={scanDepth} label="Scan Depth" onChange={(e) => setScanDepth(e.target.value)}>
                                    <MenuItem value="normal">Normal</MenuItem>
                                    <MenuItem value="deep">Deep</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>

                        {scanMode === 'offensive' && (
                            <Grid item xs={12}>
                                <Paper variant="outlined" sx={{ p: 2, mt: 2, backgroundColor: 'rgba(255, 0, 0, 0.1)' }}>
                                    <Typography variant="h6" color="error">Legal & Ethical Use Policy</Typography>
                                    {isLoadingDisclaimer ? <CircularProgress size={20} /> : <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>{legalDisclaimer?.disclaimer}</pre>}
                                    <FormControlLabel
                                        control={<Checkbox checked={legalAccepted} onChange={(e) => setLegalAccepted(e.target.checked)} />}
                                        label="I have explicit, authorized permission to perform this scan and agree to the terms."
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
                            >
                                {mutation.isPending ? <CircularProgress size={24} /> : 'Start Scan'}
                            </Button>
                        </Grid>
                    </Grid>
                </form>
                {mutation.isError && (
                    <Alert severity="error" sx={{ mt: 3 }}>
                        Failed to start scan: {mutation.error.response?.data?.detail?.message || mutation.error.message}
                    </Alert>
                )}
            </Paper>
        </Container>
    );
};

export default Scan;
