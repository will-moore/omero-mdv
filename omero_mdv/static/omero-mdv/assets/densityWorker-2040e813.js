(function(){"use strict";const Kn=Qn(_n);function Qn(n){return function(r,t,e=t){if(!((t=+t)>=0))throw new RangeError("invalid rx");if(!((e=+e)>=0))throw new RangeError("invalid ry");let{data:i,width:f,height:a}=r;if(!((f=Math.floor(f))>=0))throw new RangeError("invalid width");if(!((a=Math.floor(a!==void 0?a:i.length/f))>=0))throw new RangeError("invalid height");if(!f||!a||!t&&!e)return r;const o=t&&n(t),c=e&&n(e),u=i.slice();return o&&c?(C(o,u,i,f,a),C(o,i,u,f,a),C(o,u,i,f,a),B(c,i,u,f,a),B(c,u,i,f,a),B(c,i,u,f,a)):o?(C(o,i,u,f,a),C(o,u,i,f,a),C(o,i,u,f,a)):c&&(B(c,i,u,f,a),B(c,u,i,f,a),B(c,i,u,f,a)),r}}function C(n,r,t,e,i){for(let f=0,a=e*i;f<a;)n(r,t,f,f+=e,1)}function B(n,r,t,e,i){for(let f=0,a=e*i;f<e;++f)n(r,t,f,f+a,e)}function _n(n){const r=Math.floor(n);if(r===n)return nr(n);const t=n-r,e=2*n+1;return(i,f,a,o,c)=>{if(!((o-=c)>=a))return;let u=r*f[a];const l=c*r,d=l+c;for(let h=a,m=a+l;h<m;h+=c)u+=f[Math.min(o,h)];for(let h=a,m=o;h<=m;h+=c)u+=f[Math.min(o,h+l)],i[h]=(u+t*(f[Math.max(a,h-d)]+f[Math.min(o,h+d)]))/e,u-=f[Math.max(a,h-l)]}}function nr(n){const r=2*n+1;return(t,e,i,f,a)=>{if(!((f-=a)>=i))return;let o=n*e[i];const c=a*n;for(let u=i,l=i+c;u<l;u+=a)o+=e[Math.min(f,u)];for(let u=i,l=f;u<=l;u+=a)o+=e[Math.min(f,u+c)],t[u]=o/r,o-=e[Math.max(i,u-c)]}}function rr(n,r){let t=0;if(r===void 0)for(let e of n)e!=null&&(e=+e)>=e&&++t;else{let e=-1;for(let i of n)(i=r(i,++e,n))!=null&&(i=+i)>=i&&++t}return t}function tr(n,r){let t,e;if(r===void 0)for(const i of n)i!=null&&(t===void 0?i>=i&&(t=e=i):(t>i&&(t=i),e<i&&(e=i)));else{let i=-1;for(let f of n)(f=r(f,++i,n))!=null&&(t===void 0?f>=f&&(t=e=f):(t>f&&(t=f),e<f&&(e=f)))}return[t,e]}var an=Math.sqrt(50),on=Math.sqrt(10),un=Math.sqrt(2);function vn(n,r,t){var e,i=-1,f,a,o;if(r=+r,n=+n,t=+t,n===r&&t>0)return[n];if((e=r<n)&&(f=n,n=r,r=f),(o=er(n,r,t))===0||!isFinite(o))return[];if(o>0){let c=Math.round(n/o),u=Math.round(r/o);for(c*o<n&&++c,u*o>r&&--u,a=new Array(f=u-c+1);++i<f;)a[i]=(c+i)*o}else{o=-o;let c=Math.round(n*o),u=Math.round(r*o);for(c/o<n&&++c,u/o>r&&--u,a=new Array(f=u-c+1);++i<f;)a[i]=(c+i)/o}return e&&a.reverse(),a}function er(n,r,t){var e=(r-n)/Math.max(0,t),i=Math.floor(Math.log(e)/Math.LN10),f=e/Math.pow(10,i);return i>=0?(f>=an?10:f>=on?5:f>=un?2:1)*Math.pow(10,i):-Math.pow(10,-i)/(f>=an?10:f>=on?5:f>=un?2:1)}function ir(n,r,t){var e=Math.abs(r-n)/Math.max(0,t),i=Math.pow(10,Math.floor(Math.log(e)/Math.LN10)),f=e/i;return f>=an?i*=10:f>=on?i*=5:f>=un&&(i*=2),r<n?-i:i}function fr(n){return Math.ceil(Math.log(rr(n))/Math.LN2)+1}function $n(n,r){let t;if(r===void 0)for(const e of n)e!=null&&(t<e||t===void 0&&e>=e)&&(t=e);else{let e=-1;for(let i of n)(i=r(i,++e,n))!=null&&(t<i||t===void 0&&i>=i)&&(t=i)}return t}var ar=Array.prototype,Nn=ar.slice;function or(n,r){return n-r}function ur(n){for(var r=0,t=n.length,e=n[t-1][1]*n[0][0]-n[t-1][0]*n[0][1];++r<t;)e+=n[r-1][1]*n[r][0]-n[r-1][0]*n[r][1];return e}var S=n=>()=>n;function cr(n,r){for(var t=-1,e=r.length,i;++t<e;)if(i=hr(n,r[t]))return i;return 0}function hr(n,r){for(var t=r[0],e=r[1],i=-1,f=0,a=n.length,o=a-1;f<a;o=f++){var c=n[f],u=c[0],l=c[1],d=n[o],h=d[0],m=d[1];if(lr(c,d,r))return 0;l>e!=m>e&&t<(h-u)*(e-l)/(m-l)+u&&(i=-i)}return i}function lr(n,r,t){var e;return sr(n,r,t)&&dr(n[e=+(n[0]===r[0])],t[e],r[e])}function sr(n,r,t){return(r[0]-n[0])*(t[1]-n[1])===(t[0]-n[0])*(r[1]-n[1])}function dr(n,r,t){return n<=r&&r<=t||t<=r&&r<=n}function gr(){}var j=[[],[[[1,1.5],[.5,1]]],[[[1.5,1],[1,1.5]]],[[[1.5,1],[.5,1]]],[[[1,.5],[1.5,1]]],[[[1,1.5],[.5,1]],[[1,.5],[1.5,1]]],[[[1,.5],[1,1.5]]],[[[1,.5],[.5,1]]],[[[.5,1],[1,.5]]],[[[1,1.5],[1,.5]]],[[[.5,1],[1,.5]],[[1.5,1],[1,1.5]]],[[[1.5,1],[1,.5]]],[[[.5,1],[1.5,1]]],[[[1,1.5],[1.5,1]]],[[[.5,1],[1,1.5]]],[]];function kn(){var n=1,r=1,t=fr,e=c;function i(u){var l=t(u);if(Array.isArray(l))l=l.slice().sort(or);else{const d=tr(u),h=ir(d[0],d[1],l);l=vn(Math.floor(d[0]/h)*h,Math.floor(d[1]/h-1)*h,l)}return l.map(d=>f(u,d))}function f(u,l){var d=[],h=[];return a(u,l,function(m){e(m,u,l),ur(m)>0?d.push([m]):h.push(m)}),h.forEach(function(m){for(var x=0,v=d.length,$;x<v;++x)if(cr(($=d[x])[0],m)!==-1){$.push(m);return}}),{type:"MultiPolygon",value:l,coordinates:d}}function a(u,l,d){var h=new Array,m=new Array,x,v,$,y,s,b;for(x=v=-1,y=u[0]>=l,j[y<<1].forEach(p);++x<n-1;)$=y,y=u[x+1]>=l,j[$|y<<1].forEach(p);for(j[y<<0].forEach(p);++v<r-1;){for(x=-1,y=u[v*n+n]>=l,s=u[v*n]>=l,j[y<<1|s<<2].forEach(p);++x<n-1;)$=y,y=u[v*n+n+x+1]>=l,b=s,s=u[v*n+x+1]>=l,j[$|y<<1|s<<2|b<<3].forEach(p);j[y|s<<3].forEach(p)}for(x=-1,s=u[v*n]>=l,j[s<<2].forEach(p);++x<n-1;)b=s,s=u[v*n+x+1]>=l,j[s<<2|b<<3].forEach(p);j[s<<3].forEach(p);function p(M){var k=[M[0][0]+x,M[0][1]+v],N=[M[1][0]+x,M[1][1]+v],A=o(k),z=o(N),w,g;(w=m[A])?(g=h[z])?(delete m[w.end],delete h[g.start],w===g?(w.ring.push(N),d(w.ring)):h[w.start]=m[g.end]={start:w.start,end:g.end,ring:w.ring.concat(g.ring)}):(delete m[w.end],w.ring.push(N),m[w.end=z]=w):(w=h[z])?(g=m[A])?(delete h[w.start],delete m[g.end],w===g?(w.ring.push(N),d(w.ring)):h[g.start]=m[w.end]={start:g.start,end:w.end,ring:g.ring.concat(w.ring)}):(delete h[w.start],w.ring.unshift(k),h[w.start=A]=w):h[A]=m[z]={start:A,end:z,ring:[k,N]}}}function o(u){return u[0]*2+u[1]*(n+1)*4}function c(u,l,d){u.forEach(function(h){var m=h[0],x=h[1],v=m|0,$=x|0,y,s=l[$*n+v];m>0&&m<n&&v===m&&(y=l[$*n+v-1],h[0]=m+(d-y)/(s-y)-.5),x>0&&x<r&&$===x&&(y=l[($-1)*n+v],h[1]=x+(d-y)/(s-y)-.5)})}return i.contour=f,i.size=function(u){if(!arguments.length)return[n,r];var l=Math.floor(u[0]),d=Math.floor(u[1]);if(!(l>=0&&d>=0))throw new Error("invalid size");return n=l,r=d,i},i.thresholds=function(u){return arguments.length?(t=typeof u=="function"?u:Array.isArray(u)?S(Nn.call(u)):S(u),i):t},i.smooth=function(u){return arguments.length?(e=u?c:gr,i):e===c},i}function xr(n){return n[0]}function mr(n){return n[1]}function wr(){return 1}function yr(){var n=xr,r=mr,t=wr,e=960,i=500,f=20,a=2,o=f*3,c=e+o*2>>a,u=i+o*2>>a,l=S(20);function d(s){var b=new Float32Array(c*u),p=Math.pow(2,-a),M=-1;for(const E of s){var k=(n(E,++M,s)+o)*p,N=(r(E,M,s)+o)*p,A=+t(E,M,s);if(k>=0&&k<c&&N>=0&&N<u){var z=Math.floor(k),w=Math.floor(N),g=k-z-.5,P=N-w-.5;b[z+w*c]+=(1-g)*(1-P)*A,b[z+1+w*c]+=g*(1-P)*A,b[z+1+(w+1)*c]+=g*P*A,b[z+(w+1)*c]+=(1-g)*P*A}}return Kn({data:b,width:c,height:u},f*p),b}function h(s){var b=d(s),p=l(b),M=Math.pow(2,2*a);return Array.isArray(p)||(p=vn(Number.MIN_VALUE,$n(b)/M,p)),kn().size([c,u]).thresholds(p.map(k=>k*M))(b).map((k,N)=>(k.value=+p[N],m(k)))}h.contours=function(s){var b=d(s),p=kn().size([c,u]),M=Math.pow(2,2*a),k=N=>{N=+N;var A=m(p.contour(b,N*M));return A.value=N,A};return Object.defineProperty(k,"max",{get:()=>$n(b)/M}),k};function m(s){return s.coordinates.forEach(x),s}function x(s){s.forEach(v)}function v(s){s.forEach($)}function $(s){s[0]=s[0]*Math.pow(2,a)-o,s[1]=s[1]*Math.pow(2,a)-o}function y(){return o=f*3,c=e+o*2>>a,u=i+o*2>>a,h}return h.x=function(s){return arguments.length?(n=typeof s=="function"?s:S(+s),h):n},h.y=function(s){return arguments.length?(r=typeof s=="function"?s:S(+s),h):r},h.weight=function(s){return arguments.length?(t=typeof s=="function"?s:S(+s),h):t},h.size=function(s){if(!arguments.length)return[e,i];var b=+s[0],p=+s[1];if(!(b>=0&&p>=0))throw new Error("invalid size");return e=b,i=p,y()},h.cellSize=function(s){if(!arguments.length)return 1<<a;if(!((s=+s)>=1))throw new Error("invalid cell size");return a=Math.floor(Math.log(s)/Math.LN2),y()},h.thresholds=function(s){return arguments.length?(l=typeof s=="function"?s:Array.isArray(s)?S(Nn.call(s)):S(s),h):l},h.bandwidth=function(s){if(!arguments.length)return Math.sqrt(f*(f+1));if(!((s=+s)>=0))throw new Error("invalid bandwidth");return f=(Math.sqrt(4*s*s+1)-1)/2,y()},h}function An(n,r){return n<r?-1:n>r?1:n>=r?0:NaN}function En(n){let r=n,t=n;n.length===1&&(r=(a,o)=>n(a)-o,t=br(n));function e(a,o,c,u){for(c==null&&(c=0),u==null&&(u=a.length);c<u;){const l=c+u>>>1;t(a[l],o)<0?c=l+1:u=l}return c}function i(a,o,c,u){for(c==null&&(c=0),u==null&&(u=a.length);c<u;){const l=c+u>>>1;t(a[l],o)>0?u=l:c=l+1}return c}function f(a,o,c,u){c==null&&(c=0),u==null&&(u=a.length);const l=e(a,o,c,u-1);return l>c&&r(a[l-1],o)>-r(a[l],o)?l-1:l}return{left:e,center:f,right:i}}function br(n){return(r,t)=>An(n(r),t)}function pr(n){return n===null?NaN:+n}const Mr=En(An).right;En(pr).center;var vr=Mr,cn=Math.sqrt(50),hn=Math.sqrt(10),ln=Math.sqrt(2);function $r(n,r,t){var e,i=-1,f,a,o;if(r=+r,n=+n,t=+t,n===r&&t>0)return[n];if((e=r<n)&&(f=n,n=r,r=f),(o=Rn(n,r,t))===0||!isFinite(o))return[];if(o>0){let c=Math.round(n/o),u=Math.round(r/o);for(c*o<n&&++c,u*o>r&&--u,a=new Array(f=u-c+1);++i<f;)a[i]=(c+i)*o}else{o=-o;let c=Math.round(n*o),u=Math.round(r*o);for(c/o<n&&++c,u/o>r&&--u,a=new Array(f=u-c+1);++i<f;)a[i]=(c+i)/o}return e&&a.reverse(),a}function Rn(n,r,t){var e=(r-n)/Math.max(0,t),i=Math.floor(Math.log(e)/Math.LN10),f=e/Math.pow(10,i);return i>=0?(f>=cn?10:f>=hn?5:f>=ln?2:1)*Math.pow(10,i):-Math.pow(10,-i)/(f>=cn?10:f>=hn?5:f>=ln?2:1)}function Nr(n,r,t){var e=Math.abs(r-n)/Math.max(0,t),i=Math.pow(10,Math.floor(Math.log(e)/Math.LN10)),f=e/i;return f>=cn?i*=10:f>=hn?i*=5:f>=ln&&(i*=2),r<n?-i:i}function kr(n,r){switch(arguments.length){case 0:break;case 1:this.range(n);break;default:this.range(r).domain(n);break}return this}function sn(n,r,t){n.prototype=r.prototype=t,t.constructor=n}function zn(n,r){var t=Object.create(n.prototype);for(var e in r)t[e]=r[e];return t}function G(){}var V=.7,W=1/V,D="\\s*([+-]?\\d+)\\s*",X="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*",I="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*",Ar=/^#([0-9a-f]{3,8})$/,Er=new RegExp(`^rgb\\(${D},${D},${D}\\)$`),Rr=new RegExp(`^rgb\\(${I},${I},${I}\\)$`),zr=new RegExp(`^rgba\\(${D},${D},${D},${X}\\)$`),Pr=new RegExp(`^rgba\\(${I},${I},${I},${X}\\)$`),Hr=new RegExp(`^hsl\\(${X},${I},${I}\\)$`),Ir=new RegExp(`^hsla\\(${X},${I},${I},${X}\\)$`),Pn={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074};sn(G,Y,{copy(n){return Object.assign(new this.constructor,this,n)},displayable(){return this.rgb().displayable()},hex:Hn,formatHex:Hn,formatHex8:jr,formatHsl:qr,formatRgb:In,toString:In});function Hn(){return this.rgb().formatHex()}function jr(){return this.rgb().formatHex8()}function qr(){return Ln(this).formatHsl()}function In(){return this.rgb().formatRgb()}function Y(n){var r,t;return n=(n+"").trim().toLowerCase(),(r=Ar.exec(n))?(t=r[1].length,r=parseInt(r[1],16),t===6?jn(r):t===3?new R(r>>8&15|r>>4&240,r>>4&15|r&240,(r&15)<<4|r&15,1):t===8?Z(r>>24&255,r>>16&255,r>>8&255,(r&255)/255):t===4?Z(r>>12&15|r>>8&240,r>>8&15|r>>4&240,r>>4&15|r&240,((r&15)<<4|r&15)/255):null):(r=Er.exec(n))?new R(r[1],r[2],r[3],1):(r=Rr.exec(n))?new R(r[1]*255/100,r[2]*255/100,r[3]*255/100,1):(r=zr.exec(n))?Z(r[1],r[2],r[3],r[4]):(r=Pr.exec(n))?Z(r[1]*255/100,r[2]*255/100,r[3]*255/100,r[4]):(r=Hr.exec(n))?Fn(r[1],r[2]/100,r[3]/100,1):(r=Ir.exec(n))?Fn(r[1],r[2]/100,r[3]/100,r[4]):Pn.hasOwnProperty(n)?jn(Pn[n]):n==="transparent"?new R(NaN,NaN,NaN,0):null}function jn(n){return new R(n>>16&255,n>>8&255,n&255,1)}function Z(n,r,t,e){return e<=0&&(n=r=t=NaN),new R(n,r,t,e)}function Sr(n){return n instanceof G||(n=Y(n)),n?(n=n.rgb(),new R(n.r,n.g,n.b,n.opacity)):new R}function dn(n,r,t,e){return arguments.length===1?Sr(n):new R(n,r,t,e??1)}function R(n,r,t,e){this.r=+n,this.g=+r,this.b=+t,this.opacity=+e}sn(R,dn,zn(G,{brighter(n){return n=n==null?W:Math.pow(W,n),new R(this.r*n,this.g*n,this.b*n,this.opacity)},darker(n){return n=n==null?V:Math.pow(V,n),new R(this.r*n,this.g*n,this.b*n,this.opacity)},rgb(){return this},clamp(){return new R(F(this.r),F(this.g),F(this.b),J(this.opacity))},displayable(){return-.5<=this.r&&this.r<255.5&&-.5<=this.g&&this.g<255.5&&-.5<=this.b&&this.b<255.5&&0<=this.opacity&&this.opacity<=1},hex:qn,formatHex:qn,formatHex8:Fr,formatRgb:Sn,toString:Sn}));function qn(){return`#${L(this.r)}${L(this.g)}${L(this.b)}`}function Fr(){return`#${L(this.r)}${L(this.g)}${L(this.b)}${L((isNaN(this.opacity)?1:this.opacity)*255)}`}function Sn(){const n=J(this.opacity);return`${n===1?"rgb(":"rgba("}${F(this.r)}, ${F(this.g)}, ${F(this.b)}${n===1?")":`, ${n})`}`}function J(n){return isNaN(n)?1:Math.max(0,Math.min(1,n))}function F(n){return Math.max(0,Math.min(255,Math.round(n)||0))}function L(n){return n=F(n),(n<16?"0":"")+n.toString(16)}function Fn(n,r,t,e){return e<=0?n=r=t=NaN:t<=0||t>=1?n=r=NaN:r<=0&&(n=NaN),new H(n,r,t,e)}function Ln(n){if(n instanceof H)return new H(n.h,n.s,n.l,n.opacity);if(n instanceof G||(n=Y(n)),!n)return new H;if(n instanceof H)return n;n=n.rgb();var r=n.r/255,t=n.g/255,e=n.b/255,i=Math.min(r,t,e),f=Math.max(r,t,e),a=NaN,o=f-i,c=(f+i)/2;return o?(r===f?a=(t-e)/o+(t<e)*6:t===f?a=(e-r)/o+2:a=(r-t)/o+4,o/=c<.5?f+i:2-f-i,a*=60):o=c>0&&c<1?0:a,new H(a,o,c,n.opacity)}function Lr(n,r,t,e){return arguments.length===1?Ln(n):new H(n,r,t,e??1)}function H(n,r,t,e){this.h=+n,this.s=+r,this.l=+t,this.opacity=+e}sn(H,Lr,zn(G,{brighter(n){return n=n==null?W:Math.pow(W,n),new H(this.h,this.s,this.l*n,this.opacity)},darker(n){return n=n==null?V:Math.pow(V,n),new H(this.h,this.s,this.l*n,this.opacity)},rgb(){var n=this.h%360+(this.h<0)*360,r=isNaN(n)||isNaN(this.s)?0:this.s,t=this.l,e=t+(t<.5?t:1-t)*r,i=2*t-e;return new R(gn(n>=240?n-240:n+120,i,e),gn(n,i,e),gn(n<120?n+240:n-120,i,e),this.opacity)},clamp(){return new H(Cn(this.h),K(this.s),K(this.l),J(this.opacity))},displayable(){return(0<=this.s&&this.s<=1||isNaN(this.s))&&0<=this.l&&this.l<=1&&0<=this.opacity&&this.opacity<=1},formatHsl(){const n=J(this.opacity);return`${n===1?"hsl(":"hsla("}${Cn(this.h)}, ${K(this.s)*100}%, ${K(this.l)*100}%${n===1?")":`, ${n})`}`}}));function Cn(n){return n=(n||0)%360,n<0?n+360:n}function K(n){return Math.max(0,Math.min(1,n||0))}function gn(n,r,t){return(n<60?r+(t-r)*n/60:n<180?t:n<240?r+(t-r)*(240-n)/60:r)*255}var xn=n=>()=>n;function Cr(n,r){return function(t){return n+t*r}}function Br(n,r,t){return n=Math.pow(n,t),r=Math.pow(r,t)-n,t=1/t,function(e){return Math.pow(n+e*r,t)}}function Dr(n){return(n=+n)==1?Bn:function(r,t){return t-r?Br(r,t,n):xn(isNaN(r)?t:r)}}function Bn(n,r){var t=r-n;return t?Cr(n,t):xn(isNaN(n)?r:n)}var Dn=function n(r){var t=Dr(r);function e(i,f){var a=t((i=dn(i)).r,(f=dn(f)).r),o=t(i.g,f.g),c=t(i.b,f.b),u=Bn(i.opacity,f.opacity);return function(l){return i.r=a(l),i.g=o(l),i.b=c(l),i.opacity=u(l),i+""}}return e.gamma=n,e}(1);function Or(n,r){r||(r=[]);var t=n?Math.min(r.length,n.length):0,e=r.slice(),i;return function(f){for(i=0;i<t;++i)e[i]=n[i]*(1-f)+r[i]*f;return e}}function Tr(n){return ArrayBuffer.isView(n)&&!(n instanceof DataView)}function Ur(n,r){var t=r?r.length:0,e=n?Math.min(t,n.length):0,i=new Array(e),f=new Array(t),a;for(a=0;a<e;++a)i[a]=yn(n[a],r[a]);for(;a<t;++a)f[a]=r[a];return function(o){for(a=0;a<e;++a)f[a]=i[a](o);return f}}function Gr(n,r){var t=new Date;return n=+n,r=+r,function(e){return t.setTime(n*(1-e)+r*e),t}}function Q(n,r){return n=+n,r=+r,function(t){return n*(1-t)+r*t}}function Vr(n,r){var t={},e={},i;(n===null||typeof n!="object")&&(n={}),(r===null||typeof r!="object")&&(r={});for(i in r)i in n?t[i]=yn(n[i],r[i]):e[i]=r[i];return function(f){for(i in t)e[i]=t[i](f);return e}}var mn=/[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g,wn=new RegExp(mn.source,"g");function Xr(n){return function(){return n}}function Yr(n){return function(r){return n(r)+""}}function Wr(n,r){var t=mn.lastIndex=wn.lastIndex=0,e,i,f,a=-1,o=[],c=[];for(n=n+"",r=r+"";(e=mn.exec(n))&&(i=wn.exec(r));)(f=i.index)>t&&(f=r.slice(t,f),o[a]?o[a]+=f:o[++a]=f),(e=e[0])===(i=i[0])?o[a]?o[a]+=i:o[++a]=i:(o[++a]=null,c.push({i:a,x:Q(e,i)})),t=wn.lastIndex;return t<r.length&&(f=r.slice(t),o[a]?o[a]+=f:o[++a]=f),o.length<2?c[0]?Yr(c[0].x):Xr(r):(r=c.length,function(u){for(var l=0,d;l<r;++l)o[(d=c[l]).i]=d.x(u);return o.join("")})}function yn(n,r){var t=typeof r,e;return r==null||t==="boolean"?xn(r):(t==="number"?Q:t==="string"?(e=Y(r))?(r=e,Dn):Wr:r instanceof Y?Dn:r instanceof Date?Gr:Tr(r)?Or:Array.isArray(r)?Ur:typeof r.valueOf!="function"&&typeof r.toString!="function"||isNaN(r)?Vr:Q)(n,r)}function Zr(n,r){return n=+n,r=+r,function(t){return Math.round(n*(1-t)+r*t)}}function Jr(n){return function(){return n}}function Kr(n){return+n}var On=[0,1];function O(n){return n}function bn(n,r){return(r-=n=+n)?function(t){return(t-n)/r}:Jr(isNaN(r)?NaN:.5)}function Qr(n,r){var t;return n>r&&(t=n,n=r,r=t),function(e){return Math.max(n,Math.min(r,e))}}function _r(n,r,t){var e=n[0],i=n[1],f=r[0],a=r[1];return i<e?(e=bn(i,e),f=t(a,f)):(e=bn(e,i),f=t(f,a)),function(o){return f(e(o))}}function nt(n,r,t){var e=Math.min(n.length,r.length)-1,i=new Array(e),f=new Array(e),a=-1;for(n[e]<n[0]&&(n=n.slice().reverse(),r=r.slice().reverse());++a<e;)i[a]=bn(n[a],n[a+1]),f[a]=t(r[a],r[a+1]);return function(o){var c=vr(n,o,1,e)-1;return f[c](i[c](o))}}function rt(n,r){return r.domain(n.domain()).range(n.range()).interpolate(n.interpolate()).clamp(n.clamp()).unknown(n.unknown())}function tt(){var n=On,r=On,t=yn,e,i,f,a=O,o,c,u;function l(){var h=Math.min(n.length,r.length);return a!==O&&(a=Qr(n[0],n[h-1])),o=h>2?nt:_r,c=u=null,d}function d(h){return h==null||isNaN(h=+h)?f:(c||(c=o(n.map(e),r,t)))(e(a(h)))}return d.invert=function(h){return a(i((u||(u=o(r,n.map(e),Q)))(h)))},d.domain=function(h){return arguments.length?(n=Array.from(h,Kr),l()):n.slice()},d.range=function(h){return arguments.length?(r=Array.from(h),l()):r.slice()},d.rangeRound=function(h){return r=Array.from(h),t=Zr,l()},d.clamp=function(h){return arguments.length?(a=h?!0:O,l()):a!==O},d.interpolate=function(h){return arguments.length?(t=h,l()):t},d.unknown=function(h){return arguments.length?(f=h,d):f},function(h,m){return e=h,i=m,l()}}function et(){return tt()(O,O)}function it(n){return Math.abs(n=Math.round(n))>=1e21?n.toLocaleString("en").replace(/,/g,""):n.toString(10)}function _(n,r){if((t=(n=r?n.toExponential(r-1):n.toExponential()).indexOf("e"))<0)return null;var t,e=n.slice(0,t);return[e.length>1?e[0]+e.slice(2):e,+n.slice(t+1)]}function T(n){return n=_(Math.abs(n)),n?n[1]:NaN}function ft(n,r){return function(t,e){for(var i=t.length,f=[],a=0,o=n[0],c=0;i>0&&o>0&&(c+o+1>e&&(o=Math.max(1,e-c)),f.push(t.substring(i-=o,i+o)),!((c+=o+1)>e));)o=n[a=(a+1)%n.length];return f.reverse().join(r)}}function at(n){return function(r){return r.replace(/[0-9]/g,function(t){return n[+t]})}}var ot=/^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;function nn(n){if(!(r=ot.exec(n)))throw new Error("invalid format: "+n);var r;return new pn({fill:r[1],align:r[2],sign:r[3],symbol:r[4],zero:r[5],width:r[6],comma:r[7],precision:r[8]&&r[8].slice(1),trim:r[9],type:r[10]})}nn.prototype=pn.prototype;function pn(n){this.fill=n.fill===void 0?" ":n.fill+"",this.align=n.align===void 0?">":n.align+"",this.sign=n.sign===void 0?"-":n.sign+"",this.symbol=n.symbol===void 0?"":n.symbol+"",this.zero=!!n.zero,this.width=n.width===void 0?void 0:+n.width,this.comma=!!n.comma,this.precision=n.precision===void 0?void 0:+n.precision,this.trim=!!n.trim,this.type=n.type===void 0?"":n.type+""}pn.prototype.toString=function(){return this.fill+this.align+this.sign+this.symbol+(this.zero?"0":"")+(this.width===void 0?"":Math.max(1,this.width|0))+(this.comma?",":"")+(this.precision===void 0?"":"."+Math.max(0,this.precision|0))+(this.trim?"~":"")+this.type};function ut(n){n:for(var r=n.length,t=1,e=-1,i;t<r;++t)switch(n[t]){case".":e=i=t;break;case"0":e===0&&(e=t),i=t;break;default:if(!+n[t])break n;e>0&&(e=0);break}return e>0?n.slice(0,e)+n.slice(i+1):n}var Tn;function ct(n,r){var t=_(n,r);if(!t)return n+"";var e=t[0],i=t[1],f=i-(Tn=Math.max(-8,Math.min(8,Math.floor(i/3)))*3)+1,a=e.length;return f===a?e:f>a?e+new Array(f-a+1).join("0"):f>0?e.slice(0,f)+"."+e.slice(f):"0."+new Array(1-f).join("0")+_(n,Math.max(0,r+f-1))[0]}function Un(n,r){var t=_(n,r);if(!t)return n+"";var e=t[0],i=t[1];return i<0?"0."+new Array(-i).join("0")+e:e.length>i+1?e.slice(0,i+1)+"."+e.slice(i+1):e+new Array(i-e.length+2).join("0")}var Gn={"%":(n,r)=>(n*100).toFixed(r),b:n=>Math.round(n).toString(2),c:n=>n+"",d:it,e:(n,r)=>n.toExponential(r),f:(n,r)=>n.toFixed(r),g:(n,r)=>n.toPrecision(r),o:n=>Math.round(n).toString(8),p:(n,r)=>Un(n*100,r),r:Un,s:ct,X:n=>Math.round(n).toString(16).toUpperCase(),x:n=>Math.round(n).toString(16)};function Vn(n){return n}var Xn=Array.prototype.map,Yn=["y","z","a","f","p","n","µ","m","","k","M","G","T","P","E","Z","Y"];function ht(n){var r=n.grouping===void 0||n.thousands===void 0?Vn:ft(Xn.call(n.grouping,Number),n.thousands+""),t=n.currency===void 0?"":n.currency[0]+"",e=n.currency===void 0?"":n.currency[1]+"",i=n.decimal===void 0?".":n.decimal+"",f=n.numerals===void 0?Vn:at(Xn.call(n.numerals,String)),a=n.percent===void 0?"%":n.percent+"",o=n.minus===void 0?"−":n.minus+"",c=n.nan===void 0?"NaN":n.nan+"";function u(d){d=nn(d);var h=d.fill,m=d.align,x=d.sign,v=d.symbol,$=d.zero,y=d.width,s=d.comma,b=d.precision,p=d.trim,M=d.type;M==="n"?(s=!0,M="g"):Gn[M]||(b===void 0&&(b=12),p=!0,M="g"),($||h==="0"&&m==="=")&&($=!0,h="0",m="=");var k=v==="$"?t:v==="#"&&/[boxX]/.test(M)?"0"+M.toLowerCase():"",N=v==="$"?e:/[%p]/.test(M)?a:"",A=Gn[M],z=/[defgprs%]/.test(M);b=b===void 0?6:/[gprs]/.test(M)?Math.max(1,Math.min(21,b)):Math.max(0,Math.min(20,b));function w(g){var P=k,E=N,U,Jn,tn;if(M==="c")E=A(g)+E,g="";else{g=+g;var en=g<0||1/g<0;if(g=isNaN(g)?c:A(Math.abs(g),b),p&&(g=ut(g)),en&&+g==0&&x!=="+"&&(en=!1),P=(en?x==="("?x:o:x==="-"||x==="("?"":x)+P,E=(M==="s"?Yn[8+Tn/3]:"")+E+(en&&x==="("?")":""),z){for(U=-1,Jn=g.length;++U<Jn;)if(tn=g.charCodeAt(U),48>tn||tn>57){E=(tn===46?i+g.slice(U+1):g.slice(U))+E,g=g.slice(0,U);break}}}s&&!$&&(g=r(g,1/0));var fn=P.length+g.length+E.length,q=fn<y?new Array(y-fn+1).join(h):"";switch(s&&$&&(g=r(q+g,q.length?y-E.length:1/0),q=""),m){case"<":g=P+g+E+q;break;case"=":g=P+q+g+E;break;case"^":g=q.slice(0,fn=q.length>>1)+P+g+E+q.slice(fn);break;default:g=q+P+g+E;break}return f(g)}return w.toString=function(){return d+""},w}function l(d,h){var m=u((d=nn(d),d.type="f",d)),x=Math.max(-8,Math.min(8,Math.floor(T(h)/3)))*3,v=Math.pow(10,-x),$=Yn[8+x/3];return function(y){return m(v*y)+$}}return{format:u,formatPrefix:l}}var rn,Wn,Zn;lt({thousands:",",grouping:[3],currency:["$",""]});function lt(n){return rn=ht(n),Wn=rn.format,Zn=rn.formatPrefix,rn}function st(n){return Math.max(0,-T(Math.abs(n)))}function dt(n,r){return Math.max(0,Math.max(-8,Math.min(8,Math.floor(T(r)/3)))*3-T(Math.abs(n)))}function gt(n,r){return n=Math.abs(n),r=Math.abs(r)-n,Math.max(0,T(r)-T(n))+1}function xt(n,r,t,e){var i=Nr(n,r,t),f;switch(e=nn(e??",f"),e.type){case"s":{var a=Math.max(Math.abs(n),Math.abs(r));return e.precision==null&&!isNaN(f=dt(i,a))&&(e.precision=f),Zn(e,a)}case"":case"e":case"g":case"p":case"r":{e.precision==null&&!isNaN(f=gt(i,Math.max(Math.abs(n),Math.abs(r))))&&(e.precision=f-(e.type==="e"));break}case"f":case"%":{e.precision==null&&!isNaN(f=st(i))&&(e.precision=f-(e.type==="%")*2);break}}return Wn(e)}function mt(n){var r=n.domain;return n.ticks=function(t){var e=r();return $r(e[0],e[e.length-1],t??10)},n.tickFormat=function(t,e){var i=r();return xt(i[0],i[i.length-1],t??10,e)},n.nice=function(t){t==null&&(t=10);var e=r(),i=0,f=e.length-1,a=e[i],o=e[f],c,u,l=10;for(o<a&&(u=a,a=o,o=u,u=i,i=f,f=u);l-- >0;){if(u=Rn(a,o,t),u===c)return e[i]=a,e[f]=o,r(e);if(u>0)a=Math.floor(a/u)*u,o=Math.ceil(o/u)*u;else if(u<0)a=Math.ceil(a*u)/u,o=Math.floor(o*u)/u;else break;c=u}return n},n}function Mn(){var n=et();return n.copy=function(){return rt(n,Mn())},kr.apply(n,arguments),mt(n)}onmessage=function(n){const r=n.data[5],t=new Uint8Array(n.data[4]),e=n.data[3][1]=="int32"?new Int32Array(n.data[3][0]):new Float32Array(n.data[3][0]),i=n.data[2][1]=="int32"?new Int32Array(n.data[2][0]):new Float32Array(n.data[2][0]),f=new Uint8Array(n.data[0]),a=new Uint8Array(n.data[1]),o=r.yscale[1][1],c=Mn().domain(r.yscale[0]).range(r.yscale[1]),u=Mn().domain(r.xscale[0]).range(r.xscale[1]);function l(h){return yr().x(function(m,x){return u(i[x])}).y(function(m,x){return c(e[x])}).weight((m,x)=>f[x]==2||a[x]!==0&&a[x]!==f[x]||t[x]!==h?0:1).size([r.xscale[1][1],o]).bandwidth(r.bandwidth)(a)}const d=[];for(let h of r.categories)h===-1?d.push(null):d.push(l(h));postMessage(d)}})();
