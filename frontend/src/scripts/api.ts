export const API_URL: string = import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000/api';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

type DrfError = Record<string, unknown> & { detail?: string; non_field_errors?: string[] };

/** Flattens a Django REST Framework error body into a single readable message. */
export function parseApiError(body: unknown, fallback = 'Ocurrió un error inesperado.'): string {
  if (typeof body === 'string' && body.trim()) return body;
  if (!body || typeof body !== 'object') return fallback;

  const data = body as DrfError;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
    return data.non_field_errors.join(' ');
  }

  const parts = Object.entries(data).map(([key, value]) => {
    const text = Array.isArray(value) ? value.join(' ') : String(value);
    return key === 'non_field_errors' ? text : `${key}: ${text}`;
  });
  return parts.length ? parts.join(' · ') : fallback;
}

interface AuthInit extends RequestInit {
  auth?: boolean;
}

/** Thin fetch wrapper that injects JSON headers, optional token auth, and DRF-aware errors. */
export async function apiFetch<T = unknown>(path: string, init: AuthInit = {}): Promise<T> {
  const { auth, headers, ...rest } = init;
  const finalHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string> | undefined),
  };

  if (auth) {
    const token = localStorage.getItem('gustos_token');
    if (token) finalHeaders.Authorization = `Token ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { headers: finalHeaders, ...rest });
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Revisa tu conexión o que el backend esté activo.', 0);
  }

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(parseApiError(body), response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
