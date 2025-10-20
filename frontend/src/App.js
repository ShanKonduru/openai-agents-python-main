import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Fade,
  Slide
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Psychology as PsychologyIcon,
  Search as SearchIcon,
  Article as ArticleIcon,
  Image as ImageIcon,
  Publish as PublishIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './App.css';

const steps = [
  {
    label: 'User Input Processing',
    description: 'Analyzing and enhancing your topic',
    icon: <PsychologyIcon />,
    agent: 'User Input Agent'
  },
  {
    label: 'Research Phase',
    description: 'Conducting comprehensive research',
    icon: <SearchIcon />,
    agent: 'Research Agent'
  },
  {
    label: 'Content Structuring',
    description: 'Creating structured content',
    icon: <ArticleIcon />,
    agent: 'Content Structuring Agent'
  },
  {
    label: 'Visual Design',
    description: 'Designing visual content strategy',
    icon: <ImageIcon />,
    agent: 'Visual Content Designer'
  },
  {
    label: 'Publishing',
    description: 'Creating final publication',
    icon: <PublishIcon />,
    agent: 'Digital Publishing Specialist'
  }
];

function App() {
  const [activeStep, setActiveStep] = useState(-1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [topic, setTopic] = useState('');
  const [config, setConfig] = useState({
    target_audience: 'general',
    content_type: 'article',
    content_length: 'medium',
    tone: 'professional',
    include_technical_details: false,
    generate_real_images: false,
    max_word_count: 2000
  });
  
  const [stepResults, setStepResults] = useState({});
  const [finalResult, setFinalResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentOperation, setCurrentOperation] = useState('');
  
  const wsRef = useRef(null);
  const progressInterval = useRef(null);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, []);

  const handleStartProcess = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic for content creation');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setActiveStep(0);
    setStepResults({});
    setFinalResult(null);
    setProgress(0);
    setCurrentOperation('Initializing...');

    try {
      // Start the content creation process
      const response = await axios.post('/api/create-content', {
        topic: topic.trim(),
        config: config
      });

      if (response.data.success) {
        // Start polling for progress
        startProgressPolling(response.data.task_id);
      } else {
        throw new Error(response.data.error || 'Failed to start content creation');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to start content creation');
      setIsProcessing(false);
      setActiveStep(-1);
    }
  };

  const startProgressPolling = (taskId) => {
    progressInterval.current = setInterval(async () => {
      try {
        const response = await axios.get(`/api/progress/${taskId}`);
        const data = response.data;
        
        setProgress(data.progress);
        setCurrentOperation(data.current_operation || '');
        setActiveStep(data.current_step);
        
        // Update step results
        if (data.step_results) {
          setStepResults(prev => ({
            ...prev,
            ...data.step_results
          }));
        }
        
        // Check if completed
        if (data.status === 'completed') {
          setFinalResult(data.final_result);
          setIsProcessing(false);
          setProgress(100);
          clearInterval(progressInterval.current);
        } else if (data.status === 'failed') {
          setError(data.error || 'Content creation failed');
          setIsProcessing(false);
          clearInterval(progressInterval.current);
        }
      } catch (err) {
        console.error('Progress polling error:', err);
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleStopProcess = () => {
    setIsProcessing(false);
    setActiveStep(-1);
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
    }
    // TODO: Send stop signal to backend
  };

  const downloadResult = (type) => {
    if (!finalResult) return;
    
    let content, filename, mimeType;
    
    if (type === 'html') {
      content = finalResult.html_content;
      filename = `${finalResult.article_url_slug}.html`;
      mimeType = 'text/html';
    } else if (type === 'markdown') {
      content = finalResult.markdown_content;
      filename = `${finalResult.article_url_slug}.md`;
      mimeType = 'text/markdown';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const previewResult = () => {
    if (!finalResult?.html_content) return;
    
    const newWindow = window.open('', '_blank');
    newWindow.document.write(finalResult.html_content);
    newWindow.document.close();
  };

  const renderStepResult = (stepIndex, result) => {
    if (!result) return null;

    switch (stepIndex) {
      case 0: // User Input
        return (
          <Card sx={{ mt: 2, bgcolor: '#f8f9fa' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                📝 Processed Input
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Topic:</Typography>
                  <Typography variant="body1">{result.topic}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Audience:</Typography>
                  <Typography variant="body1">{result.target_audience}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Content Type:</Typography>
                  <Typography variant="body1">{result.content_type}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Tone:</Typography>
                  <Typography variant="body1">{result.tone}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        );

      case 1: // Research
        return (
          <Card sx={{ mt: 2, bgcolor: '#f8f9fa' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                🔍 Research Results
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={`Quality Score: ${result.research_quality_score}/10`} 
                  color={result.research_quality_score >= 8 ? 'success' : 'warning'}
                  sx={{ mr: 1 }}
                />
                <Chip label={`${result.key_points?.length || 0} Key Points`} variant="outlined" sx={{ mr: 1 }} />
                <Chip label={`${result.sources?.length || 0} Sources`} variant="outlined" />
              </Box>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Executive Summary</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">{result.executive_summary}</Typography>
                </AccordionDetails>
              </Accordion>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Key Points ({result.key_points?.length || 0})</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {result.key_points?.map((point, index) => (
                    <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                      • {point}
                    </Typography>
                  ))}
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        );

      case 2: // Content Structuring
        return (
          <Card sx={{ mt: 2, bgcolor: '#f8f9fa' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                📄 Structured Content
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Title:</Typography>
                  <Typography variant="h6">{result.title}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Reading Time:</Typography>
                  <Typography variant="body1">{result.estimated_read_time}</Typography>
                </Grid>
              </Grid>

              <Typography variant="body2" color="textSecondary">Subtitle:</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>{result.subtitle}</Typography>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Table of Contents</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {result.table_of_contents?.map((item, index) => (
                    <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                      {index + 1}. {item}
                    </Typography>
                  ))}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Content Preview</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ maxHeight: 300, overflow: 'auto', border: '1px solid #e0e0e0', p: 2, borderRadius: 1 }}>
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                    >
                      {result.markdown_content?.substring(0, 1000) + '...'}
                    </ReactMarkdown>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        );

      case 3: // Visual Design
        return (
          <Card sx={{ mt: 2, bgcolor: '#f8f9fa' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                🎨 Visual Design Strategy
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Style:</Typography>
                  <Typography variant="body1">{result.image_style}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Color Scheme:</Typography>
                  <Typography variant="body1">{result.color_scheme}</Typography>
                </Grid>
              </Grid>

              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Hero Image</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="textSecondary">Prompt:</Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>{result.hero_image?.prompt}</Typography>
                  <Typography variant="body2" color="textSecondary">Alt Text:</Typography>
                  <Typography variant="body2">{result.hero_image?.alt_text}</Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Section Images ({result.section_images?.length || 0})</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {result.section_images?.map((img, index) => (
                    <Box key={index} sx={{ mb: 2, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                      <Typography variant="body2" color="textSecondary">Image {index + 1}:</Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>{img.prompt}</Typography>
                      <Typography variant="body2" color="textSecondary">Alt: {img.alt_text}</Typography>
                    </Box>
                  ))}
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        );

      case 4: // Publishing
        return (
          <Card sx={{ mt: 2, bgcolor: '#e8f5e8' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="success.main">
                🌐 Published Article
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Word Count:</Typography>
                  <Typography variant="body1">{result.word_count}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">SEO Score:</Typography>
                  <Chip 
                    label={`${result.seo_score}/10`} 
                    color={result.seo_score >= 8 ? 'success' : 'warning'}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Sections:</Typography>
                  <Typography variant="body1">{result.sections_count}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">Reading Time:</Typography>
                  <Typography variant="body1">{result.estimated_read_time}</Typography>
                </Grid>
              </Grid>

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<VisibilityIcon />}
                  onClick={previewResult}
                  sx={{ mr: 1, mb: 1 }}
                >
                  Preview Article
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => downloadResult('html')}
                  sx={{ mr: 1, mb: 1 }}
                >
                  Download HTML
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => downloadResult('markdown')}
                  sx={{ mb: 1 }}
                >
                  Download Markdown
                </Button>
              </Box>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 1 }}>
          🤖 AI Content Creation System
        </Typography>
        <Typography variant="h6" color="textSecondary" align="center" sx={{ mb: 4 }}>
          Multi-Agent Powered Content Generation
        </Typography>

        {/* Configuration Section */}
        <Card sx={{ mb: 4, bgcolor: '#f8f9fa' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📋 Content Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Content Topic"
                  placeholder="Enter the topic you want to create content about..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={isProcessing}
                  multiline
                  rows={2}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Target Audience</InputLabel>
                  <Select
                    value={config.target_audience}
                    label="Target Audience"
                    onChange={(e) => setConfig({...config, target_audience: e.target.value})}
                    disabled={isProcessing}
                  >
                    <MenuItem value="general">General Public</MenuItem>
                    <MenuItem value="technical">Technical Professionals</MenuItem>
                    <MenuItem value="business">Business Leaders</MenuItem>
                    <MenuItem value="academic">Academic Researchers</MenuItem>
                    <MenuItem value="students">Students</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Content Type</InputLabel>
                  <Select
                    value={config.content_type}
                    label="Content Type"
                    onChange={(e) => setConfig({...config, content_type: e.target.value})}
                    disabled={isProcessing}
                  >
                    <MenuItem value="article">Article</MenuItem>
                    <MenuItem value="tutorial">Tutorial</MenuItem>
                    <MenuItem value="guide">Guide</MenuItem>
                    <MenuItem value="analysis">Analysis</MenuItem>
                    <MenuItem value="review">Review</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Content Length</InputLabel>
                  <Select
                    value={config.content_length}
                    label="Content Length"
                    onChange={(e) => setConfig({...config, content_length: e.target.value})}
                    disabled={isProcessing}
                  >
                    <MenuItem value="short">Short (500-800 words)</MenuItem>
                    <MenuItem value="medium">Medium (800-1500 words)</MenuItem>
                    <MenuItem value="long">Long (1500-2500 words)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Tone</InputLabel>
                  <Select
                    value={config.tone}
                    label="Tone"
                    onChange={(e) => setConfig({...config, tone: e.target.value})}
                    disabled={isProcessing}
                  >
                    <MenuItem value="professional">Professional</MenuItem>
                    <MenuItem value="casual">Casual</MenuItem>
                    <MenuItem value="academic">Academic</MenuItem>
                    <MenuItem value="friendly">Friendly</MenuItem>
                    <MenuItem value="authoritative">Authoritative</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.include_technical_details}
                      onChange={(e) => setConfig({...config, include_technical_details: e.target.checked})}
                      disabled={isProcessing}
                    />
                  }
                  label="Include Technical Details"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.generate_real_images}
                      onChange={(e) => setConfig({...config, generate_real_images: e.target.checked})}
                      disabled={isProcessing}
                    />
                  }
                  label="Generate Real Images (requires image API)"
                  sx={{ ml: 2 }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Control Buttons */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          {!isProcessing ? (
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrowIcon />}
              onClick={handleStartProcess}
              disabled={!topic.trim()}
              sx={{ px: 4, py: 1.5 }}
            >
              Start Content Creation
            </Button>
          ) : (
            <Button
              variant="contained"
              color="error"
              size="large"
              startIcon={<StopIcon />}
              onClick={handleStopProcess}
              sx={{ px: 4, py: 1.5 }}
            >
              Stop Process
            </Button>
          )}
        </Box>

        {/* Error Display */}
        {error && (
          <Fade in={!!error}>
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
              <Typography variant="body1">{error}</Typography>
            </Alert>
          </Fade>
        )}

        {/* Progress Indicator */}
        {isProcessing && (
          <Card sx={{ mb: 4, bgcolor: '#e3f2fd' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CircularProgress size={24} sx={{ mr: 2 }} />
                <Typography variant="h6" color="primary">
                  Processing... {Math.round(progress)}%
                </Typography>
              </Box>
              <LinearProgress variant="determinate" value={progress} sx={{ mb: 1 }} />
              <Typography variant="body2" color="textSecondary">
                {currentOperation}
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Steps Display */}
        {(isProcessing || activeStep >= 0) && (
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel
                  StepIconComponent={({ active, completed }) => (
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: completed ? 'success.main' : active ? 'primary.main' : 'grey.300',
                        color: 'white'
                      }}
                    >
                      {completed ? <CheckCircleIcon /> : active ? step.icon : step.icon}
                    </Box>
                  )}
                >
                  <Typography variant="h6">{step.label}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {step.agent}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {step.description}
                  </Typography>
                  
                  {stepResults[index] && (
                    <Slide direction="up" in={!!stepResults[index]} mountOnEnter unmountOnExit>
                      <Box>
                        {renderStepResult(index, stepResults[index])}
                      </Box>
                    </Slide>
                  )}
                </StepContent>
              </Step>
            ))}
          </Stepper>
        )}

        {/* Final Result */}
        {finalResult && (
          <Fade in={!!finalResult}>
            <Card sx={{ mt: 4, bgcolor: '#e8f5e8', border: '2px solid #4caf50' }}>
              <CardContent>
                <Typography variant="h4" gutterBottom color="success.main" align="center">
                  🎉 Content Creation Completed!
                </Typography>
                
                <Grid container spacing={3} sx={{ mt: 2 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" color="primary">{finalResult.word_count}</Typography>
                      <Typography variant="body2" color="textSecondary">Words</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" color="primary">{finalResult.sections_count}</Typography>
                      <Typography variant="body2" color="textSecondary">Sections</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" color="primary">{finalResult.estimated_read_time}</Typography>
                      <Typography variant="body2" color="textSecondary">Read Time</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" color="primary">{finalResult.seo_score}/10</Typography>
                      <Typography variant="body2" color="textSecondary">SEO Score</Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 3 }} />

                <Box textAlign="center">
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<VisibilityIcon />}
                    onClick={previewResult}
                    sx={{ mr: 2, mb: 2 }}
                  >
                    Preview Article
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<DownloadIcon />}
                    onClick={() => downloadResult('html')}
                    sx={{ mr: 2, mb: 2 }}
                  >
                    Download HTML
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<DownloadIcon />}
                    onClick={() => downloadResult('markdown')}
                    sx={{ mb: 2 }}
                  >
                    Download Markdown
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Fade>
        )}
      </Paper>
    </Container>
  );
}

export default App;