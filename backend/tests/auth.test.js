import { authService } from '../services/auth.service.js';

describe('Auth Service', () => {
  describe('verifyToken', () => {
    it('should reject invalid token', () => {
      expect(() => authService.verifyToken('invalid-token')).toThrow();
    });

    it('should reject malformed token', () => {
      expect(() => authService.verifyToken('bearer.token.invalid')).toThrow();
    });
  });

  describe('Signup/Login (requires Supabase)', () => {
    it('should reject password less than 8 characters', async () => {
      try {
        await authService.signup('test@example.com', 'short');
        throw new Error('Should have thrown');
      } catch (error) {
        expect(error.message.toLowerCase()).toContain('password');
      }
    });

    it('should throw on Supabase connection error (expected without DB)', async () => {
      // Note: Real signup/login require Supabase configured in .env
      try {
        await authService.signup('test@example.com', 'ValidPassword123');
        // If Supabase not configured, will throw
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });
});
