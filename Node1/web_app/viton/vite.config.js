import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Go back to the main project's directory and save its filepath.
const mainDir = path.resolve(__dirname, '..', '..')

// Access env_config.json.
const envPath = path.join(mainDir, 'env_config.json')
if (!fs.existsSync(envPath)) {
  throw new Error(`env_config.json non trovato in ${envPath}`)
}
const envConfig = JSON.parse(fs.readFileSync(envPath, 'utf-8'))

// Paths to SSL certificates and key vite.config.js
const certPath = path.join(__dirname, 'cert.pem')
const keyPath = path.join(__dirname, 'key.pem')

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',              // or envConfig.IP_MAIN if you need to bind the IP
    port: parseInt(envConfig.webPort, 10) || 3000,
    https: {
      key: fs.readFileSync(keyPath),
      cert: fs.readFileSync(certPath)
    },
  }
})
