#!/usr/bin/env node
// Cliente MCP mínimo para o servidor OFICIAL do Rigby2D (src/mcp/server.js).
// Fala JSON-RPC 2.0 por stdio, exatamente como o Claude Desktop faz.
//
// Uso:
//   node tools/rigby_mcp.mjs --server <rigby2d>/src/mcp/server.js --root <pasta> list
//   node tools/rigby_mcp.mjs --server ... --root ... call <ferramenta> '<json-args>'
//   node tools/rigby_mcp.mjs --server ... --root ... calls <arquivo.json>   (lista [{tool, args}])
//
// Variável RIGBY2D_MCP pode substituir --server.
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';

const argv = process.argv.slice(2);
let server = process.env.RIGBY2D_MCP;
const roots = [];
const rest = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--server') server = argv[++i];
  else if (argv[i] === '--root') roots.push(argv[++i]);
  else rest.push(argv[i]);
}
if (!server) { console.error('Informe --server ou RIGBY2D_MCP'); process.exit(2); }

const child = spawn(process.execPath, [server, ...roots.flatMap((r) => ['--root', r])], {
  stdio: ['pipe', 'pipe', 'inherit'],
});
let buf = '';
let nextId = 1;
const pending = new Map();
child.stdout.on('data', (d) => {
  buf += d;
  let nl;
  while ((nl = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, nl).trim();
    buf = buf.slice(nl + 1);
    if (!line) continue;
    const msg = JSON.parse(line);
    const p = pending.get(msg.id);
    if (p) { pending.delete(msg.id); p(msg); }
  }
});
const rpc = (method, params) => new Promise((resolve) => {
  const id = nextId++;
  pending.set(id, resolve);
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
});

const init = await rpc('initialize', {
  protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'estudio-biblico', version: '0.1' },
});
child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

let failed = false;
const callTool = async (name, args) => {
  const r = await rpc('tools/call', { name, arguments: args });
  if (r.error) { failed = true; return { tool: name, rpcError: r.error }; }
  if (r.result.isError) failed = true;
  return { tool: name, isError: !!r.result.isError, result: r.result.structuredContent ?? r.result.content?.map((c) => c.text).join('\n') };
};

const [cmd, a1, a2] = rest;
let out;
if (cmd === 'list') {
  const r = await rpc('tools/list', {});
  out = { server: init.result.serverInfo, protocol: init.result.protocolVersion,
    tools: r.result.tools.map((t) => ({ name: t.name, readOnly: !!t.annotations?.readOnlyHint, params: Object.keys(t.inputSchema?.properties ?? {}) })) };
} else if (cmd === 'call') {
  out = await callTool(a1, a2 ? JSON.parse(a2) : {});
} else if (cmd === 'calls') {
  out = [];
  for (const c of JSON.parse(readFileSync(a1, 'utf8'))) out.push(await callTool(c.tool, c.args));
} else {
  console.error('Comando: list | call <tool> <json> | calls <arquivo.json>'); process.exit(2);
}
child.stdin.end();
child.kill();
// sai só depois de o stdout esvaziar (saídas grandes são cortadas em 64 KB com exit direto)
process.stdout.write(JSON.stringify(out, null, 2) + '\n', () => process.exit(failed ? 1 : 0));
