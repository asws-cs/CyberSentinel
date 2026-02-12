import React from 'react';
import { Paper, Typography, Box, Button, Grid } from '@mui/material';
import { PlayArrow, Pause, Stop } from '@mui/icons-material';

const ToolController = ({ runningTools }) => {
    // This is a placeholder component.
    // In a real implementation, these buttons would interact with the backend
    // to pause, resume, or stop specific tools in a running scan.

    return (
        <Paper elevation={3} sx={{ p: 2, mt: 4 }}>
            <Typography variant="h6" gutterBottom>Tool Control</Typography>
            <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Live tool management is not yet implemented. This is a conceptual UI.
                </Typography>
                <Grid container spacing={2}>
                    <Grid item>
                        <Button variant="contained" startIcon={<PlayArrow />} disabled>
                            Resume All
                        </Button>
                    </Grid>
                     <Grid item>
                        <Button variant="contained" color="warning" startIcon={<Pause />} disabled>
                            Pause All
                        </Button>
                    </Grid>
                     <Grid item>
                        <Button variant="contained" color="error" startIcon={<Stop />} disabled>
                            Stop All
                        </Button>
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    );
};

export default ToolController;
