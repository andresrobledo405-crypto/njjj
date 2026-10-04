import dotenv from 'dotenv';
dotenv.config();

const requiredEnvVars = [
  'SUPABASE_URL',
  'SUPABASE_KEY',
  'JWT_SECRET',
  'CLAUDE_API_KEY',
  'STRIPE_SECRET_KEY',
];

requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    throw new Error(`Missing required environment variable: ${varName}`);
  }
});

export const config = {
  env: process.env.NODE_ENV || 'development',
  port: process.env.PORT || 3000,
  supabase: {
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_KEY,
    serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },
  claude: {
    apiKey: process.env.CLAUDE_API_KEY,
  },
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY,
    priceStarter: process.env.STRIPE_PRICE_STARTER,
    pricePro: process.env.STRIPE_PRICE_PRO,
  },
  make: {
    webhookUrl: process.env.MAKE_WEBHOOK_URL,
  },
  app: {
    url: process.env.APP_URL,
    frontendUrl: process.env.FRONTEND_URL,
  },
};
