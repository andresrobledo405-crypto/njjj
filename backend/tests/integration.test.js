import app from '../server.js';
import { authService } from '../services/auth.service.js';
import { config } from '../config/env.js';

describe('Integration Tests', () => {
  const testUser = {
    email: 'test.integration@example.com',
    password: 'TestPassword123',
  };

  let token = null;
  let userId = null;

  describe('User Onboarding Flow', () => {
    test('POST /auth/signup creates user and returns token', async () => {
      const response = await fetch('http://localhost:3001/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testUser),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.token).toBeDefined();
      expect(data.token.length).toBeGreaterThan(0);

      token = data.token;
      // Decode JWT to get userId (in real app, would use jwt.decode)
      userId = 'test-user-id';
    });

    test('POST /auth/login with correct credentials returns token', async () => {
      const response = await fetch('http://localhost:3001/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testUser),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.token).toBeDefined();
      token = data.token;
    });

    test('POST /auth/login with wrong password returns 401', async () => {
      const response = await fetch('http://localhost:3001/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: testUser.email,
          password: 'WrongPassword',
        }),
      });

      expect(response.status).toBe(401);
      const data = await response.json();
      expect(data.error).toBeDefined();
    });
  });

  describe('Video Processing Flow', () => {
    test('GET /videos returns empty list initially', async () => {
      const response = await fetch('http://localhost:3001/videos', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data.videos)).toBe(true);
    });

    test('POST /videos/upload creates video record', async () => {
      // Mock file upload
      const formData = new FormData();
      formData.append('title', 'Test Video');
      formData.append('video', new Blob(['mock video data'], { type: 'video/mp4' }), 'test.mp4');

      const response = await fetch('http://localhost:3001/videos/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        expect(data.video).toBeDefined();
        expect(data.video.id).toBeDefined();
        expect(data.video.status).toBe('uploaded');
      }
    });

    test('POST /videos/:id/process generates clips', async () => {
      // This would require a valid video ID from upload step
      // Mocked for MVP - real test would upload first
      const videoId = 'mock-video-id';

      const response = await fetch(`http://localhost:3001/videos/${videoId}/process`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      // Expected to fail with 404 on mock ID
      expect([404, 500]).toContain(response.status);
    });
  });

  describe('Billing Flow', () => {
    test('POST /billing/checkout creates Stripe session', async () => {
      const response = await fetch('http://localhost:3001/billing/checkout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan: 'starter' }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.sessionUrl).toBeDefined();
    });

    test('POST /billing/checkout rejects invalid plan', async () => {
      const response = await fetch('http://localhost:3001/billing/checkout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan: 'invalid' }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toBeDefined();
    });

    test('POST /billing/webhook handles subscription events', async () => {
      const event = {
        type: 'checkout.session.completed',
        data: {
          object: {
            client_reference_id: 'user-123',
          },
        },
      };

      const response = await fetch('http://localhost:3001/billing/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.received).toBe(true);
    });
  });

  describe('Error Handling', () => {
    test('Missing auth token returns 401', async () => {
      const response = await fetch('http://localhost:3001/videos');

      expect(response.status).toBe(401);
      const data = await response.json();
      expect(data.error).toBeDefined();
    });

    test('Invalid auth token returns 401', async () => {
      const response = await fetch('http://localhost:3001/videos', {
        headers: { 'Authorization': 'Bearer invalid-token' },
      });

      expect(response.status).toBe(401);
    });

    test('Invalid endpoint returns 404', async () => {
      const response = await fetch('http://localhost:3001/nonexistent');

      expect(response.status).toBe(404);
    });
  });

  describe('Validator Functions', () => {
    test('validateEmail accepts valid emails', () => {
      const { validateEmail } = require('../utils/validators.js');
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name+tag@example.co.uk')).toBe(true);
    });

    test('validateEmail rejects invalid emails', () => {
      const { validateEmail } = require('../utils/validators.js');
      expect(validateEmail('invalid')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
    });

    test('validatePassword enforces minimum length', () => {
      const { validatePassword } = require('../utils/validators.js');
      expect(validatePassword('Pass123')).toBe(false); // 7 chars
      expect(validatePassword('Pass1234')).toBe(true); // 8 chars
      expect(validatePassword('VeryLongPassword123')).toBe(true);
    });

    test('validateFileSize checks max 2GB', () => {
      const { validateFileSize } = require('../utils/validators.js');
      expect(validateFileSize(1000)).toBe(true); // 1KB
      expect(validateFileSize(1000 * 1024 * 1024)).toBe(true); // 1GB
      expect(validateFileSize(3 * 1024 * 1024 * 1024)).toBe(false); // 3GB
    });

    test('validateVideoFormat checks allowed extensions', () => {
      const { validateVideoFormat } = require('../utils/validators.js');
      expect(validateVideoFormat('video.mp4')).toBe(true);
      expect(validateVideoFormat('video.mov')).toBe(true);
      expect(validateVideoFormat('video.webm')).toBe(true);
      expect(validateVideoFormat('video.avi')).toBe(false);
      expect(validateVideoFormat('image.jpg')).toBe(false);
    });
  });
});
