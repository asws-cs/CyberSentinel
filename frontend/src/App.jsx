import React from 'react';
import { Routes, Route, Link as RouterLink } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import { QueryStats, Description, BugReport } from '@mui/icons-material';

import Dashboard from './pages/Dashboard';
import Scan from './pages/Scan';
import Reports from './pages/Reports';

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <BugReport sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            CyberSentinel
          </Typography>
          <nav>
            <Button component={RouterLink} to="/" sx={{ color: 'white' }} startIcon={<QueryStats />}>
              Dashboard
            </Button>
            <Button component={RouterLink} to="/scan" sx={{ color: 'white' }} startIcon={<BugReport />}>
              New Scan
            </Button>
            <Button component={RouterLink} to="/reports" sx={{ color: 'white' }} startIcon={<Description />}>
              Reports
            </Button>
          </nav>
        </Toolbar>
      </AppBar>
      
      <Container component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;
