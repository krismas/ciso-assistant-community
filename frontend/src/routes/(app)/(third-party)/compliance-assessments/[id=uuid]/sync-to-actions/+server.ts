import { BASE_API_URL } from '$lib/utils/constants';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async (event) => {
	const requestInitOptions: RequestInit = {
		method: 'POST'
	};

	const endpoint = `${BASE_API_URL}/compliance-assessments/${event.params.id}/syncToActions/`;
	const res = await event.fetch(endpoint, requestInitOptions);

	if (!res.ok) {
		const response = await res.json();
		console.error(response);
		return new Response(JSON.stringify(response), {
			status: res.status,
			headers: {
				'Content-Type': 'application/json'
			}
		});
	}

	return new Response(JSON.stringify(await res.json()), {
		headers: {
			'Content-Type': 'application/json'
		}
	});
};
