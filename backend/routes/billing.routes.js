import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import { stripeService } from '../services/stripe.service.js';

const router = express.Router();

router.post('/checkout', authMiddleware, async (req, res) => {
  try {
    const { plan } = req.body;
    const userId = req.user.userId;

    if (!['starter', 'pro'].includes(plan)) {
      return res.status(400).json({ error: 'Invalid plan' });
    }

    const { sessionUrl } = await stripeService.createCheckoutSession(userId, plan);
    res.json({ sessionUrl });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const event = JSON.parse(req.body);
    await stripeService.handleWebhookEvent(event);
    res.json({ received: true });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default router;
