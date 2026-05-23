import { describe, it, expect } from 'vitest';
import { parseApiError } from './api';

describe('parseApiError', () => {
  it('returns a plain string body as-is', () => {
    expect(parseApiError('Algo falló')).toBe('Algo falló');
  });

  it('prefers the DRF detail field', () => {
    expect(parseApiError({ detail: 'No encontrado' })).toBe('No encontrado');
  });

  it('joins non_field_errors', () => {
    expect(parseApiError({ non_field_errors: ['Inválido.', 'Reintenta.'] })).toBe('Inválido. Reintenta.');
  });

  it('prefixes field-level errors with the field name', () => {
    expect(parseApiError({ delivery_address: ['La dirección es obligatoria.'] })).toBe(
      'delivery_address: La dirección es obligatoria.',
    );
  });

  it('joins multiple field errors', () => {
    const message = parseApiError({ party_size: ['Debe ser > 0.'], reserved_at: ['Futuro.'] });
    expect(message).toContain('party_size: Debe ser > 0.');
    expect(message).toContain('reserved_at: Futuro.');
  });

  it('uses the fallback for empty or non-object bodies', () => {
    expect(parseApiError(null)).toBe('Ocurrió un error inesperado.');
    expect(parseApiError(undefined, 'Mensaje propio')).toBe('Mensaje propio');
  });
});
