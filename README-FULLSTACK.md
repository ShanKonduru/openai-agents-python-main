# 🚀 Full-Stack AI Content Creation System

A modern web application that combines a **React.js frontend** with a **Python FastAPI backend** to create professional content using multiple AI agents.

## 🌟 Features

### Frontend (React.js)
- **Modern Material-UI Interface** - Beautiful, responsive design
- **Real-time Progress Tracking** - Watch agents work step-by-step  
- **Interactive Configuration** - Customize content type, audience, tone
- **Live Results Display** - See interim outputs from each agent
- **Content Preview** - View generated articles before download
- **Multi-format Export** - Download HTML and Markdown files

### Backend (FastAPI)
- **REST API** - Clean API endpoints for all operations
- **Background Processing** - Non-blocking content generation
- **Progress Monitoring** - Real-time status updates
- **File Management** - Automatic file generation and serving
- **Error Handling** - Comprehensive error reporting

### AI Content Creation
- **5 Specialized Agents** working in sequence:
  1. 📝 **User Input Agent** - Process and enhance topics
  2. 🔍 **Research Agent** - Conduct comprehensive research  
  3. 📄 **Content Structuring Agent** - Create well-formatted content
  4. 🎨 **Visual Content Designer** - Design image strategies
  5. 🌐 **Digital Publishing Specialist** - Generate final publications

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   FastAPI       │    │   OpenAI        │
│   Frontend      │◄──►│   Backend       │◄──►│   Agents SDK    │
│   (Port 3000)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Git** (for cloning)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/ShanKonduru/openai-agents-python-main.git
cd openai-agents-python-main
```

### 2. Setup API Key (Choose one method)

**Method A: Using our setup script**
```bash
# Windows Command Prompt
006_setup_api_key.bat

# PowerShell  
.\006_setup_api_key.ps1
```

**Method B: Manual setup**
```bash
# Create a file named 'openai_key.txt' in the project root
echo "your-actual-api-key-here" > openai_key.txt
```

### 3. Install Dependencies

**Automated Setup:**
```bash
# Windows
setup_fullstack.bat
```

**Manual Setup:**
```bash
# Backend dependencies
pip install -r requirements-api.txt

# Frontend dependencies  
cd frontend
npm install
npm run build
cd ..
```

### 4. Start the Application

**Automated Start:**
```bash
# Windows Command Prompt
start_fullstack.bat

# PowerShell
.\start_fullstack.ps1
```

**Manual Start:**
```bash
# Terminal 1: Start Backend
python api_server.py

# Terminal 2: Start Frontend  
cd frontend
npm start
```

### 5. Access the Application
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### Creating Content

1. **Open the Web Interface** at http://localhost:3000

2. **Configure Your Content**:
   - Enter your topic (e.g., "Artificial Intelligence in Healthcare")
   - Select target audience (General, Technical, Business, etc.)
   - Choose content type (Article, Tutorial, Guide, etc.)
   - Set content length and tone
   - Toggle technical details and image generation

3. **Start Creation Process**:
   - Click "Start Content Creation"
   - Watch real-time progress through 5 agent steps
   - View interim results from each agent

4. **Review & Download**:
   - Preview the generated article
   - Download HTML and Markdown versions
   - View SEO score and reading statistics

### Agent Workflow

The system processes your request through 5 specialized agents:

```
📝 User Input Agent
   ↓ (Validates and enhances topic)
🔍 Research Agent  
   ↓ (Conducts comprehensive research)
📄 Content Structuring Agent
   ↓ (Creates structured, formatted content)
🎨 Visual Content Designer
   ↓ (Designs visual content strategy)
🌐 Digital Publishing Specialist
   ↓ (Generates final HTML/Markdown)
```

## 🔧 Configuration

### Backend Configuration
Edit `api_server.py` to customize:
- Server port (default: 8000)
- CORS settings
- File storage paths
- Task timeout settings

### Frontend Configuration  
Edit `frontend/src/App.js` to customize:
- API endpoint URLs
- UI themes and styling
- Default configuration values
- Progress polling intervals

### Content Creation Config
Modify default settings in `ContentCreationConfig`:
```python
config = ContentCreationConfig(
    output_directory="output",
    generate_real_images=False,  # Requires image generation API
    max_word_count=2000,
    include_toc=True,
    include_references=True
)
```

## 📁 Project Structure

```
openai-agents-python-main/
├── frontend/                 # React.js frontend
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── App.css          # Styling
│   │   └── index.js         # React entry point
│   ├── public/              # Static assets
│   └── package.json         # Node.js dependencies
├── api_server.py            # FastAPI backend server
├── enhanced_content_system.py # Core content creation logic
├── requirements-api.txt     # Python backend dependencies
├── setup_fullstack.bat     # Automated setup script
├── start_fullstack.bat     # Automated startup script
├── 006_setup_api_key.bat   # API key setup (secure)
└── README.md               # This file
```

## 🔒 Security Features

- **API Key Protection**: Keys stored in gitignored files
- **CORS Configuration**: Restricted to localhost during development
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: Comprehensive error catching and reporting
- **Background Processing**: Non-blocking operations

## 📊 API Endpoints

### Content Creation
- `POST /api/create-content` - Start content creation
- `GET /api/progress/{task_id}` - Get creation progress
- `DELETE /api/tasks/{task_id}` - Cancel task

### File Management  
- `GET /api/download/{task_id}/{file_type}` - Download results
- `GET /api/tasks` - List all tasks
- `GET /api/health` - Health check

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API docs

## 🎨 Customization

### Styling the Frontend
Edit `frontend/src/App.css` and Material-UI theme in `index.js`:
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
  },
});
```

### Adding New Agents
1. Define agent in `enhanced_content_system.py`
2. Add step to `steps` array in `App.js`  
3. Handle step result in `renderStepResult()` function

### Custom Output Formats
Extend the `PublishedArticle` model and add handlers in the publisher agent.

## 🐛 Troubleshooting

### Common Issues

**Frontend won't start**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Backend API errors**
- Verify OpenAI API key is set correctly
- Check Python dependencies: `pip install -r requirements-api.txt`
- Ensure Python 3.11+ is installed

**CORS errors**
- Make sure backend is running on port 8000
- Check CORS settings in `api_server.py`

**Content generation fails**
- Verify API key has sufficient credits
- Check internet connection
- Review error logs in backend terminal

### Debug Mode
Start backend with debug logging:
```bash
python api_server.py --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`) 
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Agents SDK** - Core AI functionality
- **FastAPI** - High-performance backend framework
- **React.js** - Frontend user interface
- **Material-UI** - Component library
- **OpenAI API** - Language model capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ShanKonduru/openai-agents-python-main/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ShanKonduru/openai-agents-python-main/discussions)
- **Documentation**: Check `/docs` API endpoint

---

**Made with ❤️ by the OpenAI Agents Community**