const money = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });

export function formatMoney(value: number): string {
  return money.format(Number.isFinite(value) ? value : 0);
}
