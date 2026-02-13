import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Container, Typography, Grid, Paper, CircularProgress, Alert, List, ListItem, ListItemText, Divider, Box, Icon } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { Dns, Memory, Storage, Speed, BarChart, DonutSmall, History, Assessment } from '@mui/icons-material';

import { getScans, getReports, getResourceMetrics } from '../services/api';
import { ScansByDayChart, ScanModeDistributionChart } from '../components/Charts';

const StatCard = ({ title, value, unit, icon, color }) => (
    <Paper 
        elevation={6} 
        sx={{ 
            p: 3, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between', 
            backgroundColor: '#333',
            color: 'white',
            borderRadius: '12px'
        }}
    >
        <Box>
            <Typography variant="h6" color="text.secondary" sx={{ color: 'lightgray' }}>{title}</Typography>
            <Typography variant="h3" component="p" sx={{ fontWeight: 'bold' }}>
                {value}
                <Typography variant="h6" component="span" sx={{ ml: 0.5 }}>{unit}</Typography>
            </Typography>
        </Box>
        <Icon component={icon} sx={{ fontSize: 48, color: color || 'white' }} />
    </Paper>
);

const Dashboard = () => {
    const { data: scans, isLoading: isLoadingScans, isError: isErrorScans } = useQuery({
        queryKey: ['scans'],
        queryFn: () => getScans(),
        refetchInterval: 10000,
    });

    const { data: reports, isLoading: isLoadingReports, isError: isErrorReports } = useQuery({
        queryKey: ['reports'],
        queryFn: () => getReports(),
    });

    const { data: metrics, isLoading: isLoadingMetrics, isError: isErrorMetrics } = useQuery({
        queryKey: ['resourceMetrics'],
        queryFn: () => getResourceMetrics(),
        refetchInterval: 5000,
    });

    const renderList = (title, items, renderItem, icon) => (
        <Paper elevation={6} sx={{ p: 3, backgroundColor: '#333', color: 'white', borderRadius: '12px', height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Icon component={icon} sx={{ mr: 1.5, color: 'lightgray' }} />
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>{title}</Typography>
            </Box>
            {items ? (
                 <List>
                    {items.slice(0, 5).map((item, index) => (
                        <React.Fragment key={item.id || index}>
                            {renderItem(item)}
                            {index < items.slice(0, 5).length - 1 && <Divider sx={{ backgroundColor: '#555' }} />}
                        </React.Fragment>
                    ))}
                </List>
            ) : <CircularProgress />}
        </Paper>
    );

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, color: 'white' }}>
            <Typography variant="h3" gutterBottom component="h1" sx={{ fontWeight: 'bold', mb: 4 }}>
                System Dashboard
            </Typography>
            
            <Grid container spacing={4} sx={{ mb: 4 }}>
                {isLoadingMetrics ? <CircularProgress color="inherit" /> : isErrorMetrics ? <Alert severity="error">Error loading metrics</Alert> : (
                    <>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="CPU Usage" value={metrics.system_cpu_percent} unit="%" icon={Speed} color="#FF6B6B" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="Memory Usage" value={metrics.system_memory.percent_used} unit="%" icon={Memory} color="#4ECDC4" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <StatCard title="Disk Usage" value={metrics.system_disk.percent_used} unit="%" icon={Storage} color="#45B7D1" />
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                           <StatCard title="App Memory" value={Math.round(metrics.application_process.memory_mb)} unit="MB" icon={Dns} color="#F7B801" />
                        </Grid>
                    </>
                )}
            </Grid>

            <Grid container spacing={4}>
                <Grid item xs={12} md={7}>
                    <Paper elevation={6} sx={{ p: 2, backgroundColor: '#333', borderRadius: '12px' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <BarChart sx={{ mr: 1.5, color: 'lightgray' }} />
                            <Typography variant="h5" sx={{color: 'white' }}>Scans by Day</Typography>
                        </Box>
                        <ScansByDayChart scans={scans} />
                    </Paper>
                </Grid>
                <Grid item xs={12} md={5}>
                    <Paper elevation={6} sx={{ p: 2, backgroundColor: '#333', borderRadius: '12px' }}>
                         <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <DonutSmall sx={{ mr: 1.5, color: 'lightgray' }} />
                            <Typography variant="h5" sx={{color: 'white' }}>Scan Mode Distribution</Typography>
                        </Box>
                        <ScanModeDistributionChart scans={scans} />
                    </Paper>
                </Grid>
            </Grid>

            <Grid container spacing={4} sx={{mt: 1}}>
                <Grid item xs={12} md={6}>
                    {renderList("Recent Scans", scans, (scan) => (
                        <ListItem button component={RouterLink} to={`/scan/${scan.scan_id}`} sx={{ borderRadius: '8px', '&:hover': { backgroundColor: '#444'} }}>
                            <ListItemText 
                                primary={<Typography sx={{ color: 'white', fontWeight: 'bold' }}>{scan.target}</Typography>}
                                secondary={<Typography component="span" sx={{ color: 'lightgray' }}>Status: {scan.status} | Mode: {scan.scan_mode}</Typography>}
                            />
                        </ListItem>
                    ), History)}
                </Grid>
                <Grid item xs={12} md={6}>
                     {renderList("Latest Reports", reports, (report) => (
                         <ListItem sx={{ borderRadius: '8px' }}>
                            <ListItemText 
                                primary={<Typography sx={{ color: 'white', fontWeight: 'bold' }}>{`Report for Scan #${report.scan_id.substring(0, 8)}...`}</Typography>}
                                secondary={<Typography component="span" sx={{ color: 'lightgray' }}>Type: {report.report_type} | Severity: {report.severity} ({report.risk_score})</Typography>}
                            />
                        </ListItem>
                     ), Assessment)}
                </Grid>
            </Grid>
        </Container>
    );
};

export default Dashboard;
