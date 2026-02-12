import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Container, Typography, Paper, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton } from '@mui/material';
import { Download } from '@mui/icons-material';

import { getReports, downloadReport } from '../services/api';
import { format } from 'date-fns';

const Reports = () => {
    const { data: reports, isLoading, isError } = useQuery({
        queryKey: ['reports'],
        queryFn: getReports,
    });

    const handleDownload = (reportId) => {
        downloadReport(reportId);
    };

    if (isLoading) return <CircularProgress />;
    if (isError) return <Alert severity="error">Error loading reports.</Alert>;

    return (
        <Container maxWidth="lg">
            <Typography variant="h4" gutterBottom component="h1">
                Scan Reports
            </Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Scan ID</TableCell>
                            <TableCell>Report Type</TableCell>
                            <TableCell>Severity</TableCell>
                            <TableCell>Risk Score</TableCell>
                            <TableCell>Date Created</TableCell>
                            <TableCell>Download</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {reports?.map((report) => (
                            <TableRow key={report.id}>
                                <TableCell>{report.scan_id.substring(0,8)}...</TableCell>
                                <TableCell>{report.report_type.toUpperCase()}</TableCell>
                                <TableCell>{report.severity}</TableCell>
                                <TableCell>{report.risk_score}</TableCell>
                                <TableCell>{format(new Date(report.created_at), 'Pp')}</TableCell>
                                <TableCell>
                                    <IconButton onClick={() => handleDownload(report.id)} color="primary">
                                        <Download />
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
