import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Container, Typography, Grid, Paper, CircularProgress, Alert, List, ListItem, ListItemText, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { getScans, getReports, getResourceMetrics } from '../services/api';
import { ScansByDayChart, ScanModeDistributionChart } from '../components/Charts';

const StatCard = ({ title, value, unit }) => (
    <Paper elevation={3} sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">{title}</Typography>
        <Typography variant="h4" component="p">{value} <Typography variant="caption">{unit}</Typography></Typography>
    </Paper>
);

const Dashboard = () => {
    const { data: scans, isLoading: isLoadingScans, isError: isErrorScans } = useQuery({
        queryKey: ['scans'],
        queryFn: () => getScans(),
        refetchInterval: 10000, // Refetch every 10 seconds
    });

    const { data: reports, isLoading: isLoadingReports, isError: isErrorReports } = useQuery({
        queryKey: ['reports'],
        queryFn: () => getReports(),
    });

    const { data: metrics, isLoading: isLoadingMetrics, isError: isErrorMetrics } = useQuery({
        queryKey: ['resourceMetrics'],
        queryFn: () => getResourceMetrics(),
        refetchInterval: 5000, // Refetch every 5 seconds
    });

    return (
        <Container maxWidth="lg">
            <Typography variant="h4" gutterBottom component="h1">
                System Dashboard
            </Typography>
            
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {isLoadingMetrics ? <CircularProgress /> : isErrorMetrics ? <Alert severity="error">Error loading metrics</Alert> : (
                    <>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="CPU Usage" value={metrics.system_cpu_percent} unit="%" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="Memory Usage" value={metrics.system_memory.percent_used} unit="%" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="Disk Usage" value={metrics.system_disk.percent_used} unit="%" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                           <StatCard title="App Memory" value={metrics.application_process.memory_mb} unit="MB" />
                        </Grid>
                    </>
                )}
            </Grid>

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <ScansByDayChart scans={scans} />
                </Grid>
                <Grid item xs={12} md={4}>
                    <ScanModeDistributionChart scans={scans} />
                </Grid>
            </Grid>

            <Grid container spacing={3} sx={{mt: 1}}>
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 2 }}>
                        <Typography variant="h5" gutterBottom>Recent Scans</Typography>
                        {isLoadingScans ? <CircularProgress /> : isErrorScans ? <Alert severity="error">Error loading scans.</Alert> : (
                             <List>
                                {scans?.slice(0, 5).map((scan, index) => (
                                    <React.Fragment key={scan.id}>
                                        <ListItem button component={RouterLink} to={`/scan/${scan.scan_id}`}>
                                            <ListItemText 
                                                primary={scan.target}
                                                secondary={`Status: ${scan.status} | Mode: ${scan.scan_mode}`}
                                            />
                                        </ListItem>
                                        {index < scans.slice(0, 5).length - 1 && <Divider />}
                                    </React.Fragment>
                                ))}
                            </List>
                        )}
                    </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                     <Paper elevation={3} sx={{ p: 2 }}>
                        <Typography variant="h5" gutterBottom>Latest Reports</Typography>
                         {isLoadingReports ? <CircularProgress /> : isErrorReports ? <Alert severity="error">Error loading reports.</Alert> : (
                             <List>
                                {reports?.slice(0, 5).map((report, index) => (
                                     <React.Fragment key={report.id}>
                                        <ListItem>
                                            <ListItemText 
                                                primary={`Report for Scan #${report.scan_id.substring(0, 8)}`}
                                                secondary={`Type: ${report.report_type} | Severity: ${report.severity} (${report.risk_score})`}
                                            />
                                        </ListItem>
                                        {index < reports.slice(0, 5).length - 1 && <Divider />}
                                    </React.Fragment>
                                ))}
                            </List>
                         )}
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Dashboard;
