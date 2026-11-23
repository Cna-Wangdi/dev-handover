let csrfToken = '';
export async function csrf() { const r = await fetch('/api/csrf/', {credentials:'same-origin'}); const body = await r.json(); csrfToken = body.csrfToken; }
export async function api(path, options={}) {
 if (!csrfToken) await csrf();
 const r = await fetch('/api/'+path, {method: options.method||'GET',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:options.body===undefined?undefined:JSON.stringify(options.body)});
 let payload;try{payload=await r.json()}catch{payload={detail:'Unexpected response from server.'}}
 if (!r.ok) {let message=payload.detail||Object.entries(payload).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):String(v)}`).join('; ');throw new Error(message||`Request failed (${r.status})`)}
 return payload;
}
