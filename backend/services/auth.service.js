import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { createClient } from '@supabase/supabase-js';
import { config } from '../config/env.js';

const supabase = createClient(config.supabase.url, config.supabase.key);

export const authService = {
  async signup(email, password) {
    // Validate password length
    if (!password || password.length < 8) {
      throw new Error('Password must be at least 8 characters');
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    const { data: newUser, error } = await supabase
      .from('users')
      .insert([
        {
          email,
          password_hash: passwordHash,
          plan: 'free',
        },
      ])
      .select()
      .single();

    if (error) throw error;

    // Generate token
    const token = jwt.sign(
      { userId: newUser.id, email: newUser.email },
      config.jwt.secret,
      { expiresIn: config.jwt.expiresIn }
    );

    return { token, user: { id: newUser.id, email: newUser.email, plan: 'free' } };
  },

  async login(email, password) {
    const { data: user, error } = await supabase
      .from('users')
      .select('*')
      .eq('email', email)
      .single();

    if (error || !user) {
      throw new Error('Invalid email or password');
    }

    const passwordMatch = await bcrypt.compare(password, user.password_hash);
    if (!passwordMatch) {
      throw new Error('Invalid email or password');
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email },
      config.jwt.secret,
      { expiresIn: config.jwt.expiresIn }
    );

    return { token, user: { id: user.id, email: user.email, plan: user.plan } };
  },

  verifyToken(token) {
    try {
      const decoded = jwt.verify(token, config.jwt.secret);
      return decoded;
    } catch (error) {
      throw new Error('Invalid or expired token');
    }
  },
};
