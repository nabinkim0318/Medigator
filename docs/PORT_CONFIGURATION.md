# Port configuration

The canonical local/demo Compose workflow has one API and one unified
development frontend:

| Service | Container port | Host port | URL |
| --- | ---: | ---: | --- |
| FastAPI | 8082 | 8082 | `http://localhost:8082` |
| Next.js demo UI | 3000 | 3000 | `http://localhost:3000` |

Start it from the repository root:

```bash
make docker-up
```

The frontend is built with `NEXT_PUBLIC_API_URL=http://localhost:8082`.
That URL is evaluated by the user's browser, so the Compose service name
`http://api:8082` is not appropriate for this client-side setting.

The optional, secondary `docker/docker-compose-separate.yml` maps patient UI
to host/container port 3000 and doctor UI to host/container port 3001. It is
not part of the Docker CI gate.

Host development uses the same API port. `npm run dev` defaults to port 3000;
`npm run dev:patient` and `npm run dev:doctor` use ports 3000 and 3001.

If a port is occupied, stop the conflicting process or override the Compose
host mapping locally. The documented and CI-verified mappings remain those
listed above.
