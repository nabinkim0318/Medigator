"use client";

import { CedarCopilot } from 'cedar-os';
import PatientInterface from './screens/PatientInterface';

function App() {
	return (
		<CedarCopilot
			llmProvider={{
				provider: 'openai',
				apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
			}}>
			<PatientInterface />
		</CedarCopilot>
	);
}