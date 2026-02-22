/**
 * Invoice Manager API client.
 * Uses Vite proxy: /api -> http://localhost:5000
 */
const API_BASE = '/api';

const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    const json = await response.json();
    if (json.error) {
      throw new Error(json.error);
    }
    return json.data;
  }
  return response;
};

export const getHealth = async () => {
  const response = await fetch('/health');
  return response.json();
};

export const getInvoices = async (status = 'all') => {
  const response = await fetch(`${API_BASE}/invoices?status=${status}`);
  return handleResponse(response);
};

export const getInvoice = async (id) => {
  const response = await fetch(`${API_BASE}/invoices/${id}`);
  return handleResponse(response);
};

export const createInvoice = async (data) => {
  const response = await fetch(`${API_BASE}/invoices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const markPaid = async (invoiceId) => {
  const response = await fetch(`${API_BASE}/invoices/${invoiceId}/pay`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const deleteInvoice = async (invoiceId) => {
  const response = await fetch(`${API_BASE}/invoices/${invoiceId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

export const getQrUrl = (invoiceId) => `${API_BASE}/invoices/${invoiceId}/qr`;

export const getRecurring = async () => {
  const response = await fetch(`${API_BASE}/recurring`);
  return handleResponse(response);
};

export const createRecurring = async (data) => {
  const response = await fetch(`${API_BASE}/recurring`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};
