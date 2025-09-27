"use client";

import { CedarCopilot } from 'cedar-os';
import PatientInterface from './pages/PatientInterface';

export default function Home() {
	return (
		<CedarCopilot
			llmProvider={{
				provider: 'openai',
				apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY ?? '',
			}}>
			<PatientInterface />
		</CedarCopilot>
	);
}