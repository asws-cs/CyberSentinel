import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient();

const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// -- Scan Endpoints --

export const startScan = async (scanData, legalAccepted) => {
    const headers = {};
    if (scanData.scan_mode === 'offensive' && legalAccepted) {
        headers['X-Legal-Accepted'] = 'true';
    }
    const { data } = await apiClient.post('/scan/', scanData, { headers });
    return data;
};

export const getScans = async () => {
    const { data } = await apiClient.get('/scan/');
    return data;
};

export const getScanById = async (scanId) => {
    const { data } = await apiClient.get(`/scan/${scanId}`);
    return data;
};

// -- Report Endpoints --

export const getReports = async () => {
    const { data } = await apiClient.get('/reports/');
    return data;
};

export const getReportsByScanId = async (scanId) => {
    const { data } = await apiClient.get(`/reports/scan/${scanId}`);
    return data;
};

export const downloadReport = async (reportId) => {
    const response = await apiClient.get(`/reports/${reportId}/download`, {
        responseType: 'blob',
    });
    // Create a URL for the blob
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const contentDisposition = response.headers['content-disposition'];
    let filename = `report-${reportId}.dat`; // default
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch.length > 1) {
            filename = filenameMatch[1];
        }
    }
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
};


// -- Tool & System Endpoints --

export const getTools = async () => {
    const { data } = await apiClient.get('/tools/');
    return data;
};

export const getLegalDisclaimer = async () => {
    const { data } = await apiClient.get('/tools/legal/disclaimer');
    return data;
};

export const getResourceMetrics = async () => {
    const { data } = await apiClient.get('/tools/monitoring/resources');
    return data;
};
