import Stripe from 'stripe';
import { config } from '../config/env.js';

const stripe = new Stripe(config.stripe.secretKey);

export const stripeService = {
  async createCheckoutSession(userId, plan) {
    const priceId = plan === 'starter' ? config.stripe.priceStarter : config.stripe.pricePro;

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      mode: 'subscription',
      success_url: `${config.app.frontendUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${config.app.frontendUrl}/pricing`,
      client_reference_id: userId,
    });

    return { sessionUrl: session.url };
  },

  async handleWebhookEvent(event) {
    switch (event.type) {
      case 'checkout.session.completed':
        console.log('Subscription started:', event.data.object.client_reference_id);
        break;
      case 'customer.subscription.deleted':
        console.log('Subscription cancelled');
        break;
      default:
        console.log('Event:', event.type);
    }
  },
};
