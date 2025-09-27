export default function SignIn() {
	return <div>
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh'}}>
            <h1 style={{fontSize: '2rem', marginBottom: '1rem'}}>Sign In</h1>
            <form style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                <input type="text" placeholder="Username" style={{padding: '0.5rem', marginBottom: '1rem', width: '200px'}} />
                <input type="password" placeholder="Password" style={{padding: '0.5rem', marginBottom: '1rem', width: '200px'}} />
                <button type="submit" style={{padding: '0.5rem 1rem'}}>Sign In</button>
            </form>
        </div>
    </div>;
}