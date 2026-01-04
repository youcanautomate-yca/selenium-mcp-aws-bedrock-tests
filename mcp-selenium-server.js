#!/usr/bin/env node

const http = require('http');
const { spawn } = require('child_process');
const readline = require('readline');
const path = require('path');

// Start the MCP Selenium process by spawning the server directly
const mcp = spawn('node', [path.join(__dirname, 'node_modules', '@angiejones', 'mcp-selenium', 'src', 'lib', 'server.js')], {
  stdio: ['pipe', 'pipe', 'inherit']
});

const rl = readline.createInterface({
  input: mcp.stdout,
  output: mcp.stdin,
  terminal: false
});

const PORT = process.env.PORT || 8000;
let messageId = 1;
const pendingRequests = new Map();

// Parse JSON-RPC responses from MCP server
rl.on('line', (line) => {
  try {
    const response = JSON.parse(line);
    
    if (response.id && pendingRequests.has(response.id)) {
      const { res } = pendingRequests.get(response.id);
      pendingRequests.delete(response.id);
      
      // Send response to client
      res.writeHead(200, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      });
      res.end(JSON.stringify(response));
    }
  } catch (e) {
    console.error('Error parsing MCP response:', e);
  }
});

// Create HTTP server
const server = http.createServer((req, res) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  if (req.method === 'POST' && req.url === '/call') {
    let body = '';
    
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const request = JSON.parse(body);
        const id = messageId++;
        
        // Store the response writer for later
        pendingRequests.set(id, { res });
        
        // Convert HTTP call format to MCP format
        let rpcCall;
        if (request.tool_name) {
          // New format: {tool_name, parameters}
          rpcCall = {
            jsonrpc: '2.0',
            method: 'tools/call',
            params: {
              name: request.tool_name,
              arguments: request.parameters || {}
            },
            id: id
          };
        } else if (request.method) {
          // Already in JSON-RPC format
          rpcCall = {
            jsonrpc: '2.0',
            method: request.method,
            params: request.params || {},
            id: id
          };
        }
        
        // Send JSON-RPC call to MCP server
        mcp.stdin.write(JSON.stringify(rpcCall) + '\n');
        
        // Timeout after 30 seconds
        setTimeout(() => {
          if (pendingRequests.has(id)) {
            pendingRequests.delete(id);
            res.writeHead(408, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Request timeout' }));
          }
        }, 30000);
        
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON: ' + e.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`🚀 MCP Selenium SSE Server listening on http://localhost:${PORT}`);
  console.log(`📞 POST /call endpoint available for JSON-RPC calls`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down...');
  mcp.kill();
  server.close();
});

process.on('SIGINT', () => {
  console.log('Shutting down...');
  mcp.kill();
  server.close();
});
