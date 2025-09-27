import { CedarCaptionChat } from "@/cedar/components/chatComponents/CedarCaptionChat";

export default function PatientInterface() {
    return <div>
        <button style={{ position: 'fixed', top: 10, right: 10, zIndex: 1000, color: "black", backgroundColor: 'white', padding: '5px 10px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
            onClick={() => {
                window.location.href = '/signin';
            }}>
            Sign in
        </button>
        <CedarCaptionChat />
    </div>;
}