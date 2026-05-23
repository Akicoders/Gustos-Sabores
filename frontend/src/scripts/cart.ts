export const CART_KEY = 'gustos_cart';
export const CART_EVENT = 'cart:change';

export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
}

export interface DishLike {
  id: number | string;
  name: string;
  price: number | string;
  image_url?: string;
}

function isCartItem(value: unknown): value is CartItem {
  if (!value || typeof value !== 'object') return false;
  const item = value as Record<string, unknown>;
  return typeof item.id === 'number' && typeof item.quantity === 'number' && item.quantity > 0;
}

export function getCart(): CartItem[] {
  try {
    const raw: unknown = JSON.parse(localStorage.getItem(CART_KEY) ?? '[]');
    return Array.isArray(raw) ? raw.filter(isCartItem) : [];
  } catch {
    return [];
  }
}

export function saveCart(cart: CartItem[]): void {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  document.dispatchEvent(new CustomEvent<CartItem[]>(CART_EVENT, { detail: cart }));
}

export function addToCart(dish: DishLike): void {
  const id = Number(dish.id);
  const cart = getCart();
  const existing = cart.find((item) => item.id === id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id, name: dish.name, price: Number(dish.price), quantity: 1, image_url: dish.image_url });
  }
  saveCart(cart);
}

export function changeQuantity(id: number, delta: number): void {
  const cart = getCart()
    .map((item) => (item.id === id ? { ...item, quantity: item.quantity + delta } : item))
    .filter((item) => item.quantity > 0);
  saveCart(cart);
}

export function clearCart(): void {
  saveCart([]);
}

export function cartTotal(cart: CartItem[] = getCart()): number {
  return cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function cartCount(cart: CartItem[] = getCart()): number {
  return cart.reduce((sum, item) => sum + item.quantity, 0);
}
