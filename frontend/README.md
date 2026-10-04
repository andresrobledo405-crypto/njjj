# Repurpose AI - Frontend

Simple HTML/JavaScript frontend for Repurpose AI SaaS application.

## Pages

1. **index.html** - Landing page with pricing and CTA
2. **auth.html** - Login/Signup page
3. **dashboard.html** - Main dashboard with video upload and list
4. **video-detail.html** - Video analysis results and generated clips
5. **settings.html** - Account settings and plan management
6. **billing.html** - Upgrade plan page
7. **styles.css** - Shared stylesheet

## Running Locally

1. Start the backend server:
```bash
cd backend
npm run dev
```

Backend runs on `http://localhost:3001`

2. Open frontend pages in browser:
```bash
# Open in your browser
open frontend/index.html
```

Or use a simple HTTP server:
```bash
cd frontend
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Features

### Authentication
- Email/password signup and login
- JWT token stored in localStorage
- Auto-redirect to dashboard if logged in

### Dashboard
- Drag & drop video upload
- File validation (format, size)
- Video processing orchestration
- List of user's videos

### Video Details
- Viral scores per platform (TikTok, Reels, Shorts, LinkedIn)
- Best moment detection
- Generated clips preview
- Clip status tracking

### Settings
- Account information
- Current plan display
- Plan upgrade (Starter/Pro)
- Subscription management

### Billing
- Plan selection (Starter/Pro/Agency)
- Stripe checkout integration
- Pricing display

## API Endpoints Used

- POST `/auth/signup` - User registration
- POST `/auth/login` - User login
- GET `/videos` - List user videos
- GET `/videos/:id` - Get video details + clips
- POST `/videos/upload` - Upload video
- POST `/videos/:id/process` - Analyze & generate clips
- POST `/billing/checkout` - Create Stripe checkout session

## Error Handling

All API calls include try-catch blocks with user-friendly error messages.
Network errors and API failures are caught and displayed to the user.

## CORS

Frontend assumes backend is running on `http://localhost:3001`.
For production, update `API_URL` constant in each HTML file.

## Security Notes

- JWT token stored in localStorage (not production-safe)
- No HTTPS validation on localhost
- For production: use httpOnly cookies, HTTPS, CSRF tokens
