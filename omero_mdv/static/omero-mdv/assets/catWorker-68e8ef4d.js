(function(){"use strict";onmessage=function(u){const o=u.data[3],a=o.datatype=="multitext"?Uint16Array:Uint8Array,l=new a(u.data[2]),e=new Uint8Array(u.data[0]),i=new Uint8Array(u.data[1]);let n=null;if(o.method==="sankey"){const c=new Uint8Array(u.data[4]);n=L(e,i,l,c,o)}else if(o.method==="venn")n=S(e,i,l,o);else if(o.method==="proportion"){const c=new Uint8Array(u.data[4]);n=k(e,i,l,c,o)}else n=b(e,i,l,o);postMessage(n)};function k(u,o,a,l,e){const i=e.values.length,n=e.values2.length,c=e.cats?new Uint8Array(e.cats):null,f=a.length,s=new Array(i),h=e.diviser?e.diviser:new Array(i);for(let r=0;r<i;r++)s[r]=new Array(n).fill(0),h[r]=new Array(n).fill(0);const y=e.category;for(let r=0;r<f;r++)if(h[a[r]][l[r]]++,o[r]===0){if(c&&c[r]!==y)continue;s[a[r]][l[r]]++}let d=0,A=1e7;for(let r=0;r<h.length;r++){const g=h[r],x=s[r],p=[],U=[];let t=0,m=0,v=1e7;for(let w=0;w<g.length;w++){if(g[w]===0)continue;const M=e.denominators?x[w]/e.denominators[w]:x[w]/g[w]*100;p.push([M,r,w,Math.floor(Math.random()*6)]),U.push(M),t+=M,m=Math.max(m,M),v=Math.min(v,M)}p.av=t/p.length,p.std=z(U,p.av),p.max=m,p.min=v,s[r]=p,d=Math.max(d,m),A=Math.min(A,v)}return s.max=d,s.min=A,s}function S(u,o,a,l){const e=performance.now(),i=a.length/l.stringLength,n=new Map,c=l.stringLength;for(let s=0;s<i;s++){if(o[s]!==0&&o[s]!==u[s])continue;const h=s*c;let y=a.slice(h,h+c).toString();const d=n.get(y);d?n.set(y,d+1):n.set(y,1)}const f=[];for(const[s,h]of n.entries(n)){const y=s.split(",").map(d=>l.values[d]).filter(d=>d!==void 0);f.push({sets:y,size:h})}return console.log(`calc ven : ${performance.now()-e}`),f}function b(u,o,a,l){const e=l.datatype==="multitext"?a.length/l.stringLength:a.length,i=new Array(l.values.length).fill(0);if(l.datatype==="multitext"){const n=l.stringLength;for(let c=0;c<e;c++){if(o[c]!==0&&o[c]!==u[c])continue;const f=c*n;for(let s=f;s<f+n&&a[s]!==65535;s++)i[a[s]]++}}else for(let n=0;n<e;n++)o[n]!==0&&o[n]!==u[n]||i[a[n]]++;return i}function L(u,o,a,l,e){const i=e.values.length,n=e.values2.length,c=a.length,f=new Array(i),s=e.values.map((t,m)=>"A"+m),h=e.values2.map((t,m)=>"B"+m);for(let t=0;t<i;t++)f[t]=new Array(n).fill(0);const y=[];let d=0;for(let t=0;t<c;t++)o[t]!==0&&o[t]!==u[t]||(f[a[t]][l[t]]++,d++);const A=new Set,r=new Set,g=Math.round(d/300);for(let t=0;t<i;t++)for(let m=0;m<n;m++){const v=f[t][m];v!==0&&(A.add(s[t]),r.add(h[m]),y.push({source:s[t],target:h[m],value:v<g?g:v,trueValue:v}))}const x=Math.min(A.size,r.size),p=Array.from(A).map(t=>({id:t,ind:t.substring(1),param:0})),U=Array.from(r).map(t=>({id:t,ind:t.substring(1),param:1}));return{links:y,nodes:p.concat(U),minNodes:x}}function z(u,o){let a=u.length-1;a=a===0?1:a;let l=u.reduce((e,i)=>e+Math.pow(i-o,2),0);return Math.sqrt(l/a)}})();
