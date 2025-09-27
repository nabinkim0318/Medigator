"use client";

import { FloatingCedarChat } from '@/cedar/components/chatComponents/FloatingCedarChat';
import { CedarCopilot } from 'cedar-os';

export default function Home() {
	return (
		<CedarCopilot
			llmProvider={{
				provider: 'openai',
				apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY ?? '',
			}}>
			<FloatingCedarChat />
		</CedarCopilot>
	);
}