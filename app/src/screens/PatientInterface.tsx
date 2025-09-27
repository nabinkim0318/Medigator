import { FloatingCedarChat } from '@/chatComponents/FloatingCedarChat';

export default function PatientInterface() {
	return (
		<div>
			{/* Your main content */}
			<FloatingCedarChat
				side='right'
				title='Assistant'
				collapsedLabel='How can I help you today?'
				dimensions={{
					width: 400,
					height: 600,
					minWidth: 350,
					minHeight: 400,
				}}
				resizable={true}
			/>
		</div>
	);
}

// Props interface
interface FloatingCedarChatProps {
	side?: 'left' | 'right';
	title?: string;
	collapsedLabel?: string;
	companyLogo?: React.ReactNode;
	dimensions?: {
		width?: number;
		height?: number;
		minWidth?: number;
		minHeight?: number;
		maxWidth?: number;
		maxHeight?: number;
	};
	resizable?: boolean;
}