# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered navigation assistant that uses MCP (Model Context Protocol) for computer automation. The application accepts voice or text input to automatically open Baidu Maps or Gaode Maps and initiate navigation from point A to point B.

## Architecture

```
Frontend (Voice/Text Input) → Server (Intent Parsing) → MCP Client → Automation Control
```

### Key Components

- **Frontend**: Web interface with voice recording and text input
- **Intent Parser**: Natural language processing for navigation commands
- **Speech Service**: Voice recognition using Google Speech-to-Text
- **Navigation Service**: Map integration (Baidu Maps, Gaode Maps)
- **MCP Client**: Automation control through Model Context Protocol
- **Socket.IO**: Real-time communication between frontend and backend

## Development Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Start production server
npm start

# Run tests
npm test
```

## File Structure

```
src/
├── server.js              # Main server entry point
├── config/
│   └── mcp.js            # MCP client configuration
├── services/
│   ├── intentParser.js   # Natural language intent parsing
│   ├── speechService.js  # Voice recognition service
│   └── navigationService.js # Map navigation logic
├── mcp/
│   └── automationClient.js # MCP automation integration
└── public/
    ├── index.html        # Frontend interface
    ├── style.css         # Styling
    └── app.js            # Frontend JavaScript
```

## Key Features

### Voice Input
- Real-time voice recording and transcription
- Support for WAV audio format
- Fallback to mock recognition when Google Speech API unavailable

### Text Input
- Natural language processing for navigation commands
- Support for various command patterns:
  - "导航从北京到上海" (Route navigation)
  - "去天安门广场" (Destination navigation)
  - "从公司导航回家" (Start location navigation)

### Map Integration
- Baidu Maps support
- Gaode Maps support
- Automatic URL generation for navigation
- Browser automation through MCP

### MCP Automation
- Browser control (open, navigate, click)
- Element interaction
- Screenshot capabilities
- Fallback to mock automation when MCP unavailable

## Configuration

### Environment Setup
- Node.js 18+ required
- Google Cloud credentials for Speech-to-Text (optional)
- MCP server configuration for full automation

### Default Settings
- Default map: Baidu Maps
- Port: 3000
- Speech recognition: Chinese (zh-CN)

## Development Notes

- The application gracefully degrades when external services (Google Speech, MCP) are unavailable
- Mock implementations provided for development and testing
- Real-time status updates through Socket.IO
- Comprehensive error handling and user feedback

## API Endpoints

- `GET /` - Main application interface
- `GET /health` - Health check
- `POST /api/voice-command` - Voice command processing
- `GET /api/status` - System status information

## Socket Events

- `navigation_command` - Send navigation commands
- `command_response` - Receive command execution results
- `status_update` - Real-time status updates
- `error` - Error notifications