import React, { useState } from "react";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <header className="App-header">
        <h1>BBB Medical Report System</h1>
        <p>Medical report generation and analysis system</p>

        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.tsx</code> and save to test HMR
          </p>
        </div>

        <div className="api-info">
          <h2>API endpoints</h2>
          <ul>
            <li>
              <a
                href="http://localhost:8082/docs"
                target="_blank"
                rel="noopener noreferrer"
              >
                API Documentation
              </a>
            </li>
            <li>
              <a
                href="http://localhost:8082/api/v1/reports/demo/pdf"
                target="_blank"
                rel="noopener noreferrer"
              >
                Generate Demo PDF
              </a>
            </li>
            <li>
              <a
                href="http://localhost:8082/"
                target="_blank"
                rel="noopener noreferrer"
              >
                API Root
              </a>
            </li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
