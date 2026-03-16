export interface Session {
	session_id: string;
	customer_name: string;
	customer_phone: string;
	customer_email: string;
	customer_address: string;
	customer_zip: string;
	referral_source: string;
	job_description: string;
	job_type: string;
	job_total: string;
	job_date: string;
	plumber_name: string;
	is_repeat_customer: boolean;
	follow_up_notes: string;
	device_type: string;
	status: string;
	created_at: string;
	message_count: number;
}

export interface ChatMessage {
	role: string;
	content: string;
	ts: number;
}

export interface Analytics {
	reviews_today: number;
	reviews_this_week: Record<string, number>;
	total_sessions: number;
	completion_rate: number;
}

export interface DetailedAnalytics extends Analytics {
	funnel: Record<string, number>;
	daily_reviews: Record<string, number>;
	daily_started: Record<string, number>;
	avg_messages: number;
}

export interface RedisStatCard {
	name: string;
	type: string;
	key_pattern: string;
	count: number;
	purpose: string;
}

export interface PipelineEvent {
	id: string;
	session_id: string;
	event: string;
	timestamp: string;
	data: Record<string, string>;
}

export interface JobCreatePayload {
	customer_name: string;
	customer_phone: string;
	customer_email: string;
	customer_address: string;
	customer_zip: string;
	referral_source: string;
	job_description: string;
	job_type: string;
	job_total: string;
	job_date: string;
	plumber_name: string;
	is_repeat_customer: boolean;
	follow_up_notes: string;
}

export interface JobResponse {
	session_id: string;
	review_link: string;
	sms_sent: boolean;
	sms_error: string | null;
}
