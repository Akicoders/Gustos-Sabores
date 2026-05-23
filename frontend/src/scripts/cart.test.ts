import { describe, it, expect, beforeEach } from 'vitest';
import {
  getCart, addToCart, changeQuantity, clearCart, cartTotal, cartCount, CART_KEY,
} from './cart';

describe('cart', () => {
  beforeEach(() => localStorage.clear());

  it('adds a dish and increments quantity when added again', () => {
    addToCart({ id: 1, name: 'Lomo saltado', price: 28 });
    addToCart({ id: 1, name: 'Lomo saltado', price: 28 });
    const cart = getCart();
    expect(cart).toHaveLength(1);
    expect(cart[0].quantity).toBe(2);
  });

  it('computes total and item count across lines', () => {
    addToCart({ id: 1, name: 'Lomo', price: 28 });
    addToCart({ id: 2, name: 'Inca Kola', price: 5 });
    addToCart({ id: 2, name: 'Inca Kola', price: 5 });
    expect(cartTotal()).toBe(38);
    expect(cartCount()).toBe(3);
  });

  it('removes a line when its quantity reaches zero', () => {
    addToCart({ id: 1, name: 'Lomo', price: 28 });
    changeQuantity(1, -1);
    expect(getCart()).toHaveLength(0);
  });

  it('clears the whole cart', () => {
    addToCart({ id: 1, name: 'Lomo', price: 28 });
    clearCart();
    expect(getCart()).toHaveLength(0);
  });

  it('returns an empty array when storage is corrupt', () => {
    localStorage.setItem(CART_KEY, 'not-json{');
    expect(getCart()).toEqual([]);
  });

  it('coerces string id and price coming from the API', () => {
    addToCart({ id: '3', name: 'Ceviche', price: '32.50' });
    const [item] = getCart();
    expect(item.id).toBe(3);
    expect(item.price).toBe(32.5);
  });
});
