import React from 'react';
import { Routes, Route, Link as RouterLink, useLocation } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button, CssBaseline, createTheme, ThemeProvider } from '@mui/material';
import { QueryStats, Description, BugReport, Security } from '@mui/icons-material';

import Dashboard from './pages/Dashboard';
import Scan from './pages/Scan';
import Reports from './pages/Reports';

// Create a dark theme instance
const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#90caf9',
        },
        secondary: {
            main: '#f48fb1',
        },
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
    },
    typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        h1: { fontWeight: 700 },
        h2: { fontWeight: 700 },
        h3: { fontWeight: 600 },
        h4: { fontWeight: 600 },
    },
    components: {
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: 'rgba(30, 30, 30, 0.85)',
                    backdropFilter: 'blur(10px)',
                }
            }
        }
    }
});

function App() {
  const location = useLocation();

  const navLinks = [
    { text: 'Dashboard', path: '/', icon: <QueryStats /> },
    { text: 'New Scan', path: '/scan', icon: <BugReport /> },
    { text: 'Reports', path: '/reports', icon: <Description /> }
  ];

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="sticky">
          <Toolbar>
            <Security sx={{ mr: 2, fontSize: '2rem' }} />
            <Typography variant="h5" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              CyberSentinel
            </Typography>
            <nav>
              {navLinks.map((link) => (
                <Button 
                  key={link.text} 
                  component={RouterLink} 
                  to={link.path} 
                  sx={{ 
                    color: 'white', 
                    fontWeight: 'bold',
                    borderBottom: location.pathname === link.path ? 3 : 0,
                    borderColor: 'primary.main',
                    borderRadius: 0,
                    mr: 1
                  }} 
                  startIcon={link.icon}
                >
                  {link.text}
                </Button>
              ))}
            </nav>
          </Toolbar>
        </AppBar>
        
        <Container component="main" maxWidth={false} sx={{ flexGrow: 1, p: { xs: 2, md: 4 } }}>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scan" element={<Scan />} />
                <Route path="/scan/:scanId" element={<Scan />} />
                <Route path="/reports" element={<Reports />} />
            </Routes>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
