# México Trans y Querido - Admin Dashboard

Full-stack admin dashboard for managing presentations and members with Discord OAuth authentication.

**Backend**: FastAPI (Python)
**Frontend**: React + Refine + TypeScript
**Database**: SQLite (development) / PostgreSQL (production)

## Features

### Backend (FastAPI)
- **Discord OAuth Authentication**: Staff members login using their Discord accounts
- **Staff Role Verification**: Only users with staff role in the Discord server can access
- **JWT Token Management**: Stateless authentication with JWT tokens
- **REST API**: Complete API for presentations and members management
- **Database Integration**: Connected to bot's SQLite database

### Frontend (React + Refine)
- **Dashboard**: Overview with statistics
- **Presentations Management**: List, view, approve, reject presentations
- **Members Management**: View members and their presentation status
- **Discord OAuth Login**: Seamless Discord authentication
- **Real-time Updates**: React Query integration
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
admin/
├── package.json              # Frontend dependencies
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Main app component
│   ├── pages/                # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Presentations.tsx
│   │   ├── Members.tsx
│   │   └── Login.tsx
│   ├── components/           # Reusable components
│   ├── api/                  # API client
│   ├── hooks/                # Custom React hooks
│   ├── types/                # TypeScript types
│   └── styles/               # Global styles
├── main.py                   # FastAPI application entry point
├── settings.py               # Configuration and settings
├── auth.py                   # Discord OAuth and JWT logic
├── db.py                     # Database connection
├── routes/
│   ├── auth.py               # Authentication endpoints
│   └── api.py                # API endpoints
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Quick Start - Backend Only

### Prerequisites

- Python 3.10+
- Discord bot token and OAuth credentials

### Installation

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (shared from root):
   The `.env` file should already be in the parent directory with Discord configuration

4. **Run the backend**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Start - Full Stack (Backend + Frontend)

### Prerequisites

- Node.js 16+ and npm/yarn
- Python 3.10+
- Discord bot token and OAuth credentials

### Backend Setup

1. **Navigate to admin directory**:
   ```bash
   cd admin
   ```

2. **Create Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify .env configuration** in root directory has:
   ```
   DISCORD_CLIENT_ID=your_id
   DISCORD_CLIENT_SECRET=your_secret
   DISCORD_BOT_TOKEN=your_bot_token
   SECRET_KEY=your_secret_key
   ```

5. **Start FastAPI backend** (in one terminal):
   ```bash
   python main.py
   ```
   Backend running at: http://localhost:8000

### Frontend Setup

1. **Install Node dependencies** (in another terminal):
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   Frontend running at: http://localhost:5173

3. **Open browser**:
   Navigate to http://localhost:5173 and login with Discord

## Build for Production

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run with production ASGI server
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
# Build optimized bundle
npm run build

# Preview production build locally
npm run preview

# Output will be in 'dist/' directory
```

### Docker (Optional)

```bash
# Build image
docker build -t transmexico-admin .

# Run container
docker run -p 8000:8000 -p 5173:5173 transmexico-admin
```

## API Endpoints

### Authentication

- `GET /auth/login` - Start Discord OAuth flow
- `GET /auth/discord/callback` - OAuth callback (automatic)
- `GET /auth/me?token=<jwt>` - Get current user
- `POST /auth/logout` - Logout user

### Presentations

- `GET /api/presentations` - List presentations
- `GET /api/presentations/{id}` - Get single presentation
- `POST /api/presentations/{id}/approve?token=<jwt>` - Approve
- `POST /api/presentations/{id}/reject?token=<jwt>` - Reject

### Members

- `GET /api/members` - List members
- `GET /api/members/{id}` - Get member details

### Dashboard

- `GET /api/stats` - Get statistics

## Development

### Backend Development

- **Auto-reload**: Uvicorn watches for Python file changes
- **API Documentation**: Visit http://localhost:8000/docs for Swagger UI
- **Debugging**: Use print statements or Python debugger (pdb)

### Frontend Development

- **Hot reload**: Vite provides instant HMR
- **Type checking**: TypeScript catches errors before runtime
- **Testing**: `npm run test`
- **Linting**: `npm run lint`

### Database

- **SQLite** (development): Located at `../bot/transmexico.db`
- **PostgreSQL** (production): Update DATABASE_URL in `.env`

## Troubleshooting

### Backend Issues

**Import Error: cannot import name 'DATABASE_URL' from 'config'**
- Ensure you've renamed `config.py` to `settings.py`
- The admin and bot have separate config modules to avoid conflicts

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Frontend Issues

**Module not found errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Discord OAuth fails**
- Verify DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET in .env
- Check DISCORD_REDIRECT_URI matches backend (http://localhost:8000/auth/discord/callback)
- Ensure your Discord server ID matches DISCORD_SERVER_ID

## Deployment

### Heroku

```bash
# Create app
heroku create transmexico-admin

# Set environment variables
heroku config:set DISCORD_CLIENT_ID=...
heroku config:set DISCORD_CLIENT_SECRET=...
# ... etc

# Deploy
git push heroku main
```

### Docker + Docker Compose

See `docker-compose.yml` for local multi-container setup

### AWS / GCP / Azure

Refer to platform-specific deployment guides. The app consists of:
- FastAPI backend (Python 3.11+)
- React frontend (Node 16+)
- SQLite/PostgreSQL database

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Install dev dependencies: `npm install` and `pip install -r requirements.txt`
3. Make changes and test locally
4. Submit pull request

## Support

For issues or questions:
- Backend issues: Check `/docs` endpoint on running API
- Frontend issues: Check browser console for errors
- Database issues: Verify bot is running and database exists at `../bot/transmexico.db`
- Tailwind CSS
- Zustand

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL

## 📁 Structure

```
admin/
├── frontend/              # React app
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI server
│   ├── main.py
│   ├── routes/
│   └── requirements.txt
└── README.md
```

## 🚀 Getting Started

See main project README at `/proj/transmexico.org/README.md`

## 📝 Contributing

Build step by step following the main project roadmap.
