import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Container, Typography, Paper, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Box, Chip } from '@mui/material';
import { DownloadForOffline } from '@mui/icons-material';
import { format } from 'date-fns';

import { getReports, downloadReport } from '../services/api';

const Reports = () => {
    const { data: reports, isLoading, isError } = useQuery({
        queryKey: ['reports'],
        queryFn: getReports,
    });

    const handleDownload = (reportId) => {
        downloadReport(reportId);
    };

    const getSeverityChipColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical':
                return 'error';
            case 'high':
                return 'warning';
            case 'medium':
                return 'info';
            case 'low':
                return 'success';
            default:
                return 'default';
        }
    };

    if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}><CircularProgress color="inherit"/></div>;
    if (isError) return <Alert severity="error">Error loading reports.</Alert>;

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
             <Typography variant="h3" gutterBottom component="h1" sx={{ fontWeight: 'bold', color: 'white' }}>
                Scan Reports
            </Typography>
            <TableContainer component={Paper} sx={{ borderRadius: '12px', backgroundColor: '#333' }}>
                <Table sx={{ color: 'white' }}>
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ color: 'lightgray', fontWeight: 'bold' }}>Scan ID</TableCell>
                            <TableCell sx={{ color: 'lightgray', fontWeight: 'bold' }}>Report Type</TableCell>
                            <TableCell sx={{ color: 'lightgray', fontWeight: 'bold' }}>Severity</TableCell>
                            <TableCell sx={{ color: 'lightgray', fontWeight: 'bold' }}>Risk Score</TableCell>
                            <TableCell sx={{ color: 'lightgray', fontWeight: 'bold' }}>Date Created</TableCell>
                            <TableCell align="center" sx={{ color: 'lightgray', fontWeight: 'bold' }}>Download</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {reports?.map((report) => (
                            <TableRow key={report.id} sx={{ '&:hover': { backgroundColor: '#444'} }}>
                                <TableCell sx={{ color: 'white' }}>{report.scan_id.substring(0,8)}...</TableCell>
                                <TableCell sx={{ color: 'white' }}>{report.report_type.toUpperCase()}</TableCell>
                                <TableCell>
                                    <Chip label={report.severity} color={getSeverityChipColor(report.severity)} size="small" />
                                </TableCell>
                                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>{report.risk_score}</TableCell>
                                <TableCell sx={{ color: 'white' }}>{format(new Date(report.created_at), 'PPpp')}</TableCell>
                                <TableCell align="center">
                                    <IconButton onClick={() => handleDownload(report.id)} sx={{ color: '#4CAF50', '&:hover': { color: '#81C784' } }}>
                                        <DownloadForOffline />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Container>
    );
};

export default Reports;
