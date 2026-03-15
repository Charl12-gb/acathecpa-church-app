import apiClient from './index';

export interface PaymentCreate {
  course_id: number;
  amount: number;
  currency?: string;
  payment_method?: string;
}

export interface PaymentResponse {
  id: number;
  user_id: number;
  course_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  payment_method?: string | null;
  transaction_ref?: string | null;
  created_at: string;
  completed_at?: string | null;
  course_title?: string | null;
}

export const initiatePayment = async (data: PaymentCreate): Promise<PaymentResponse> => {
  const response = await apiClient.post<PaymentResponse>('/payments/', data);
  return response.data;
};

export const confirmPayment = async (paymentId: number): Promise<PaymentResponse> => {
  const response = await apiClient.post<PaymentResponse>(`/payments/${paymentId}/confirm`);
  return response.data;
};

export const getMyPayments = async (): Promise<PaymentResponse[]> => {
  const response = await apiClient.get<PaymentResponse[]>('/payments/me');
  return response.data;
};

export const getPaymentDetail = async (paymentId: number): Promise<PaymentResponse> => {
  const response = await apiClient.get<PaymentResponse>(`/payments/${paymentId}`);
  return response.data;
};
