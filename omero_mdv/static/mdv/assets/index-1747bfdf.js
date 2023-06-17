var B=Object.defineProperty;var L=(o,e,t)=>e in o?B(o,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):o[e]=t;var u=(o,e,t)=>(L(o,typeof e!="symbol"?e+"":e,t),t);import{m as $,B as x,c as f,a as F,D as k,S as P,L as V,O as U,b as O,d as N,j as R,r as b,e as X,_ as j,f as H,C as W,T as Y,A as K,g as G}from"./AnnotationDialogReact-6e70f00e.js";class q{constructor(e,t,s={}){this.container=e,this.img=new Image,this.img.style.position="absolute",this.img.onload=i=>{this.orig_dim=[this.img.naturalWidth,this.img.naturalHeight,this.img.naturalWidth/this.img.naturalHeight],this.container.append(this.img),this.fit()},$(this.img),this.container.style.overflow="hidden",this.container.addEventListener("wheel",i=>{i.preventDefault(),this.zoom(Math.sign(i.deltaY)>0?-1:1,i)}),this.setImage(t)}setImage(e){this.img.src=e}fit(){const e=this.container.getBoundingClientRect();this.img.height=e.height,this.img.width=this.img.height*this.orig_dim[2],this.img.width>e.width?(this.img.width=e.width,this.img.height=this.img.width/this.orig_dim[2],this.img.style.top=`${(e.height-this.img.height)/2}px`,this.img.style.left="0px"):(this.img.style.top="0px",this.img.style.left=`${(e.width-this.img.width)/2}px`)}zoom(e,t){e=e>0?1.1:.9;const s=this.container.getBoundingClientRect();let i=this.img.getBoundingClientRect();const a=(t.clientX-s.left-this.img.offsetLeft)*(e-1),r=(t.clientY-s.top-this.img.offsetTop)*(e-1);this.img.width=i.width*e,this.img.height=i.height*e,this.img.style.left=`${this.img.offsetLeft-a}px`,this.img.style.top=`${this.img.offsetTop-r}px`}}class J extends x{constructor(e,t,s){if(super(e,t,s),s.image){const a=f("div",{classes:["mdv-image-holder"],style:{height:parseInt(this.width*.7)+"px"}},this.contentDiv);this.imViewer=new q(a,this._getImage(0))}this.paramHolders={};const i=f("div",{},this.contentDiv);for(let a of this.config.param){if(a===this.img_param)continue;const r=this.dataStore.columnIndex[a],n=f("div",{classes:["mdv-section"]},i);n.__mcol__=r.field,f("div",{text:r.name,classes:["mdv-section-header"]},n);let l=f("div",{classes:["mdv-section-value"]},n);r.is_url&&(l=f("a",{target:"_blank"},l)),this.paramHolders[r.field]=l}F(i,{handle:"mdv-section-header",sortEnded:a=>{const r=this.config;let n=[];r.image&&(n=[r.param[r.image.param]],r.image.param=0),r.param=n.concat(a.map(l=>l.__mcol__))}}),this.setParam(0),this.contentDiv.style.overflowY="auto"}setParam(e){for(let t in this.paramHolders){const s=this.dataStore.getRowText(e,t);this.paramHolders[t].textContent=s,this.paramHolders[t].nodeName==="A"&&(this.paramHolders[t].href=s)}}_getImage(e){const t=this.config,s=t.param[t.image.param];this.img_param=s;const i=this.dataStore.getRowText(e,s);return`${t.image.base_url}${i}.${t.image.type}`}setSize(e,t){super.setSize(e,t),this.imViewer&&(this.imViewer.container.style.height=Math.round(this.width*.7)+"px",this.imViewer.fit())}onDataHighlighted(e){const t=e.indexes[0];this.imViewer&&this.imViewer.setImage(this._getImage(t)),this.setParam(t)}onDataFiltered(){const e=this.dataStore.getFirstFilteredIndex();this.onDataHighlighted({indexes:[e]})}changeBaseDocument(e){super.changeBaseDocument(e),this.imViewer.img.__doc__=e}getSettings(){return super.getSettings()}}x.types.row_summary_box={class:J,name:"Row Summary Box",init:(o,e,t)=>{const s=t.image_set;if(s&&s!=="__none__"){const i=e.large_images[s];o.param=o.param||[],o.param.push(i.key_column),o.image={base_url:i.base_url,type:i.type,param:o.param.length-1}}},extra_controls:o=>{const e=o.large_images;if(e){let t=[];for(let s in e)t.push({name:s,value:s});return t=[{name:"none",value:"__none__"}].concat(t),[{type:"dropdown",name:"image_set",label:"Image Set",values:t}]}return[]},params:[{type:"_multi_column:all",name:"Values To Display"}]};class Z{constructor(e,t,s){typeof e=="string"&&(e=document.getElementById("#"+e)),s||(s={}),this.domId=this._getRandomString(),this.row_first=0,this.row_last=139,this.tile_height=205,this.tile_width=205;let i=this;this.__doc__=document,this.display_columns=[],this.selection_mode=!0,this.imageFunc=s.imageFunc,this.base_url=s.base_url,this.parent=e,this.selected_tiles={},this.cache_size=5;const a=this.parent.getBoundingClientRect();this.config=s,s.background_color,this.view_port=f("div",{styles:{height:a.height+"px",width:a.width+"px",overflow:"auto"}},this.parent),this.canvas=f("div",{styles:{position:"relative"}},this.view_port),this.canvas.addEventListener("click",h=>{this.imageClicked(h,h.srcElement)}),this.canvas.addEventListener("mouseover",h=>{this.mouseOver(h,h.srcElement)}),this.canvas.addEventListener("keydown",h=>{this.keyPressed(h)}),this.data_view=t,this._setCanvasHeight(),this.view_port.addEventListener("scroll",h=>this._hasScrolled(h)),this.parent.append(this.view_port),this.resize_timeout=null,this.resize_timeout_length=50,this.listeners={image_clicked:new Map,image_over:new Map,image_out:new Map,data_changed:new Map,image_selected:new Map},this.highlightcolors=null,this.tag_color_palletes={},this.image_suffix=s.image_suffix?s.image_suffix:".png",s.columns&&this.setColumns(s.columns);let r=new Image;r.onload=function(h){i.originalDimensions=[r.width,r.height],i.preferred_width=i.img_width=r.width,i.preferred_height=i.img_height=r.height,s.initial_image_width&&(i.preferred_width=s.initial_image_width,i.preferred_height=Math.round(i.preferred_width/i.img_width*i.img_height)),i._resize()};const n=this.config.base_url,l=this.config.image_type,g=this.data_view.getItemField(1,this.config.image_key);r.src=`${n}${g}.${l}`}mouseOver(e,t){if(t.id){let s=t.id.split("-"),i=parseInt(s[1]),a=this.data_view.getItem(i);if(!a)return;if(this.image_over){if(a.id===this.image_over.id)return;this.listeners.image_out.forEach(r=>{r(e,this.image_over[0],self.image_over[1])})}this.listeners.image_over.forEach(r=>{r(e,a,t)}),this.image_over=t}else this.image_over&&this.listeners.image_out.forEach(s=>{s(e,self.image_over[0],self.image_over[1])}),this.image_over=null}imageClicked(e,t){let s=t.id;if(s||(s=t.parentElement.id),!s)return;let i=s.split("-");if(i[0]==="mlvtile"){let a=null,r=parseInt(i[2]);if(e.shiftKey&&self.last_img_clicked!=null){const l=this.last_img_clicked.index;range=[],a=[];let g=r-l<0?-1:1,h=l+1,c=r+1;g===-1&&(h=r,c=l);for(let d=h;d<c;d++){let m=this.data_view.getId(d);a.push(m)}a.push(this.data_view.getId(l))}const n=this.data_view.getId(r);this.listeners.image_clicked.forEach(l=>{l(e,n,t)}),this.last_index_clicked=r,this.selection_mode&&this.setSelectedTiles([r],e.ctrlKey,!0)}}keyPressed(e){if(e.which===39||e.which===40){if(this.last_index_clicked===this.data_view.getFilteredItems().length-1)return;(this.last_index_clicked||this.last_index_clicked===0)&&(this.last_index_clicked++,this.setSelectedTiles([this.data_view.getItem(this.last_index_clicked).id],!1,!0),this.last_index_clicked>this.getLastTileInView()&&this.show(this.last_index_clicked))}else if(e.which===37||e.which===38){if(this.last_index_clicked===0)return;this.last_index_clicked&&(this.last_index_clicked--,this.setSelectedTiles([this.data_view.getItem(this.last_index_clicked).id],!1,!0),this.last_index_clicked<this.getFirstTileInView()&&this.show(this.last_index_clicked))}}addListener(e,t,s){let i=this.listeners[e];return i?(s||(s=this._getRandomString()),i.set(s,t),s):null}removeListener(e,t){let s=this.listeners[e];return s?s.delete(t):!1}setImageWidth(e,t){this.setImageDimensions([e,Math.round(e/this.img_width*this.img_height)],t)}setImageLabel(e){this.config.image_label=e;const t=this.getFirstTileInView();this.setImageDimensions(),this.show(t)}setImageTitle(e){this.config.image_title=e;const t=this.getFirstTileInView();this.show(t)}setImageDimensions(e,t){this.lrm=this.config.margins.left_right,this.tbm=this.config.margins.top_bottom;let s=this.getFirstTileInView();e?(this.preferred_width=e[0],this.preferred_height=e[1]):e=[this.preferred_width,this.preferred_height],this.width<this.preferred_width+this.lrm*2&&this.width!==0?(e[0]=this.width-this.lrm*3,this.num_per_row=1):(this.num_per_row=Math.ceil((this.width-this.lrm)/(this.preferred_width+this.lrm)),e[0]=Math.floor((this.width-2*this.lrm)/this.num_per_row)-this.lrm),e[1]=Math.round(e[0]/this.preferred_width*this.preferred_height),this.config.image_label&&(this.label_size=Math.round(e[1]/12),this.label_size=Math.max(this.label_size,12),this.tbm=this.tbm<this.label_size+4?this.label_size+4:this.tbm),this.tile_width=parseInt(e[0])+this.lrm,this.tile_height=parseInt(e[1])+this.tbm,this.t_width=parseInt(e[0]),this.t_height=parseInt(e[1]);let i=Math.floor((this.height+this.cache_size*this.tile_height)/this.tile_height);this.max_difference=i+this.cache_size,t&&this.show(s)}resize(){let e=this;clearTimeout(this.resize_timeout),e.resize_timeout=setTimeout(()=>{e._resize()},e.resize_timeout_length)}getFirstTileInView(){let e=this.view_port.scrollTop;return Math.floor(e/this.tile_height)*this.num_per_row}getLastTileInView(){let e=this.view_port.scrollTop+this.view_port.height();return Math.floor(e/this.tile_height)*this.num_per_row}setColumns(e){this.columns=e}setColorBy(e,t){this.color_by=e,this.color_overlay=t}_setCanvasHeight(){let e=Math.ceil(this.data_view.getLength()/this.num_per_row)*this.tile_height+this.tbm;this.canvas.style.height=e+"px"}_hasScrolled(){clearTimeout(this.scroll_timeout);let e=this.view_port.scrollTop,t=Math.floor((e-this.cache_size*this.tile_height)/this.tile_height),s=Math.floor((e+this.height+this.cache_size*this.tile_height)/this.tile_height);t<0&&(t=0);let i=10;Math.abs(t-this.row_displayed_first)>this.max_difference&&(i=50),this.scroll_timeout=setTimeout(()=>{Math.abs(t-this.row_displayed_first)>this.max_difference?this.render(t,s,!0):this.render(t,s)},i)}_removeByClass(e){document.querySelectorAll(e).forEach(t=>t.remove())}render(e,t,s){if(s){this.canvas.innerHTML="";for(let i=e;i<t;i++)this._addRow(i)}else{if(e===this.row_displayed_first&&e!==0)return;if(e<this.row_displayed_first){for(let i=e;i<this.row_displayed_first;i++)this._addRow(i);for(let i=t;i<this.row_displayed_last;i++)this._removeByClass(`.mlv-tile-${this.domId}-${i}`)}else{for(let i=this.row_displayed_last;i<t;i++)this._addRow(i);for(let i=this.row_displayed_first;i<e;i++)this._removeByClass(`.mlv-tile-${this.domId}-${i}`)}}this.row_displayed_first=e,this.row_displayed_last=t}_resize(e){e||(e=this.getFirstTileInView());const t=this.parent.getBoundingClientRect();this.width=Math.round(t.width),this.height=Math.round(t.height),this.view_port.style.height=this.height+"px",this.view_port.style.width=this.width+"px",this.setImageDimensions(),this.show(e)}_calculateTopBottomRow(e){e||(e=0);let t=0;e||e===0?t=Math.floor(e/this.num_per_row)*this.tile_height:t=this.view_port.scrollTop;let i=this.view_port.getBoundingClientRect().height,a=Math.floor((t-this.cache_size*this.tile_height)/this.tile_height),r=Math.floor((t+i+this.cache_size*this.tile_height)/this.tile_height);return a<0&&(a=0),{top:a,bottom:r,scroll_top:t}}setSelectedTiles(e,t,s){if(!t){for(let i in this.selected_tiles){let a=this.__doc__.getElementById(`mlvtile-${this.domId}-${i}`);a&&(a.style.border=this.selected_tiles[i])}this.selected_tiles={}}for(let i of e){let a=this.__doc__.getElementById(`mlvtile-${this.domId}-${i}`);a&&(this.selected_tiles[i]=a.style.border,a.style.border="4px solid goldenrod",console.log(a.style.border))}s&&this.listeners.image_selected.forEach(i=>{i(e)})}scrollToTile(e,t){const s=this.data_view.data.indexOf(e);let i=this._calculateTopBottomRow(s);Math.abs(i.top-this.row_displayed_first)>this.max_difference?this.render(i.top,i.bottom,!0):this.render(i.top,i.bottom),this.view_port.scrollTop=i.scroll_top,t&&this.setSelectedTiles([s])}_getRandomString(e,t){e||(e=6),t=t&&t.toLowerCase();let s="",i=0,a=t=="a"?10:0,r=t=="n"?10:62;for(;i++<e;){let n=Math.random()*(r-a)+a<<0;s+=String.fromCharCode(n+=n>9?n<36?55:61:48)}return s}show(e){e||(e=this.getFirstTileInView()),this._setCanvasHeight();let t=this._calculateTopBottomRow(e);this.render(t.top,t.bottom,!0),this.view_port.scrollTop=t.scroll_top}_addRow(e){const t=this.config.image_label;let s=e*this.num_per_row,i=s+this.num_per_row,a=e*this.tile_height+this.tbm,r=0;const n=this.t_width+"px",l=this.t_height+"px",g=this.config.base_url,h=this.config.image_type,c=this.config.image_title||"Gene",d=this.data_view.dataStore.columnIndex[c]!==void 0;for(let m=s;m<i;m++){const _=this.data_view.getId(m);if(_==null)return;const p=this.data_view.getItemField(m,this.config.image_key),w=d?`${c} '${this.data_view.getItemField(m,c)}'`:p,E=p==="missing";let v=r*this.tile_width+this.lrm;r++;let y="";if(this.color_by){let A=this.color_by(_);y="4px solid "+A,this.color_overlay&&f("div",{styles:{height:l,width:n,left:v+"px",top:a+"px",zIndex:1,pointerEvents:"none",backgroundColor:A,opacity:this.color_overlay},classes:["mlv-tile",`mlv-tile-overlay-${this.domId}`,`mlv-tile-overlay-${this.domId}-${e}`]},this.canvas)}let I=[];this.selected_tiles[_]&&(y="4px solid goldenrod"),E&&I.push("mlv-tile-missing"),f("img",{src:`${g}${p}.${h}`,id:`mlvtile-${this.domId}-${m}`,styles:{border:y,height:l,width:n,left:v+"px",top:a+"px"},alt:w,title:w,classes:["mlv-tile",`mlv-tile-${this.domId}`,`mlv-tile-${this.domId}-${e}`].concat(I)},this.canvas),t&&f("div",{text:this.data_view.getItemField(m,t),classes:["mdv-image-label"],styles:{width:n,fontSize:`${this.label_size}px`,top:a-this.label_size+"px",left:v+"px"}},this.canvas)}}}class Q extends x{constructor(e,t,s){super(e,t,s),this.dataModel=new k(e,{autoupdate:!1}),this.dataModel.setColumns(this.config.param),this.dataModel.updateModel();const i=this.config;i.margins=i.margins||{top_bottom:10,left_right:10},this.grid=new Z(this.contentDiv,this.dataModel,{base_url:i.images.base_url,image_type:i.images.type,image_key:i.param[0],initial_image_width:i.image_width,image_label:i.image_label,margins:i.margins}),this.grid.addListener("image_clicked",(a,r)=>{this.dataStore.dataHighlighted([r],this)},i.id),i.sortBy&&this.sortBy(i.sortBy,i.sortOrder)}setSize(e,t){super.setSize(e,t),this.grid.resize()}onDataFiltered(){this.dataModel.updateModel(),this.grid.show()}getColorOptions(){return{colorby:"all",color_overlay:0}}onDataHighlighted(e){if(e.source===this)return;const t=e.indexes[0];this.grid.scrollToTile(t,!0)}setImageLabel(e){this.config.image_label=e,this.grid.setImageLabel(e)}colorByColumn(e){this.grid.setColorBy(this.getColorFunction(e,!1),this.config.color_overlay);const t=this.grid.getFirstTileInView();this.grid.show(t)}colorByDefault(){this.grid.setColorBy(null);const e=this.grid.getFirstTileInView();this.grid.show(e)}sortBy(e,t=!0){this.config.sortBy=e,this.config.sortOrder=t,this.dataModel.sort(e,t?"asc":"desc");const s=this.grid.getFirstTileInView();this.grid.show(s)}setImageTitle(e){this.config.image_title=e,this.grid.setImageTitle(e)}getSettings(){const e=this.grid.originalDimensions,t=this.config,s=super.getSettings(),i=this.dataStore.getColumnList("all",!0);return s.concat([{type:"slider",max:e[1]*4,min:10,doc:this.__doc__,label:"Image Size",current_value:t.image_width||e[0],func:a=>{t.image_width=a,this.grid.setImageWidth(a,!0)}},{label:"Label",type:"dropdown",values:[i,"name","field"],current_value:t.image_label||"__none__",func:a=>{this.setImageLabel(a==="__none__"?null:a)}},{label:"Tooltip",type:"dropdown",values:[i,"name","field"],current_value:t.image_title||"__none__",func:a=>{this.setImageTitle(a==="__none__"?void 0:a)}},{label:"Sort By",type:"dropdown",values:[i,"name","field"],current_value:t.sortBy||"__none__",func:a=>{this.sortBy(a==="__none__"?null:a)}},{label:"Sort Ascending?",type:"check",current_value:t.sortOrder||!0,func:a=>{this.sortBy(t.sortBy,a)}}])}changeBaseDocument(e){super.changeBaseDocument(e),this.grid.__doc__=e}}x.types.image_table_chart={class:Q,name:"Image Table",required:["images"],methodsUsingColumns:["setImageLabel","sortBy","setTitleColumn"],configEntriesUsingColumns:["image_label","sort_by","image_title"],init:(o,e,t)=>{const s=e.images[t.image_set];o.param=[s.key_column],o.images={base_url:s.base_url,type:s.type},o.sortBy=t.sort_by,o.sortOrder=t.sort_order},extra_controls:o=>{const e=[];for(let s in o.images)e.push({name:s,value:s});const t=o.getLoadedColumns().map(s=>({name:s,value:s}));return[{type:"dropdown",name:"image_set",label:"Image Set",values:e},{type:"dropdown",name:"image_title",label:"Tooltip",values:t},{type:"dropdown",name:"sort_by",label:"Sort By",values:t}]}};class ee{constructor(e,t,s,i){u(this,"textures");u(this,"texturesByIndex");u(this,"texture");u(this,"gl");u(this,"logEl");u(this,"dataView");u(this,"onProgress");this.textures=new Map,this.texturesByIndex=new Map,this.dataView=s;const a=t.getContext("webgl2");this.gl=a,this.texture=a.createTexture(),this.logEl=f("div",{},t.parentElement),this.logEl.style.color="white",this.loadImageColumn(e,a,i)}getImageAspect(e){return this.texturesByIndex.get(e).aspectRatio}getImageIndex(e){return this.texturesByIndex.get(e).zIndex}drawProgress(e=0){this.logEl.textContent=`Loading images: ${Math.round(e*100)}%`,this.onProgress&&this.onProgress(e)}loadImageColumn(e,t,s){const{base_url:i,image_type:a,image_key:r,width:n,height:l}=s,g=e.columnIndex[r],h=this.texture;t.activeTexture(t.TEXTURE0),t.bindTexture(t.TEXTURE_2D_ARRAY,h);const c=Math.floor(Math.log2(n));t.texParameteri(t.TEXTURE_2D_ARRAY,t.TEXTURE_MIN_FILTER,t.LINEAR_MIPMAP_LINEAR),t.texParameteri(t.TEXTURE_2D_ARRAY,t.TEXTURE_MAG_FILTER,t.LINEAR),t.texParameteri(t.TEXTURE_2D_ARRAY,t.TEXTURE_WRAP_S,t.CLAMP_TO_EDGE),t.texParameteri(t.TEXTURE_2D_ARRAY,t.TEXTURE_WRAP_T,t.CLAMP_TO_EDGE),t.texStorage3D(t.TEXTURE_2D_ARRAY,c,t.RGBA8,n,l,g.data.length);const d=n*l*4*g.data.length/1024/1024;console.log(`Allocated ${d.toFixed(2)}MB for image array (not accounting for mipmaps)`);let m=0;g.data.map((_,p)=>{const w=_;if(this.textures.has(w)){this.texturesByIndex.set(p,this.textures.get(w)),m++;return}const E=`${i}/${w}.${a}`,v=p,y=new Image,I={zIndex:v,aspectRatio:1};this.textures.set(w,I),this.texturesByIndex.set(p,I),y.src=E,y.crossOrigin="anonymous",y.onload=()=>{if(s.cancel)return;t.activeTexture(t.TEXTURE0),t.bindTexture(t.TEXTURE_2D_ARRAY,h),I.aspectRatio=y.width/y.height;const A=te(y,n,l);t.texSubImage3D(t.TEXTURE_2D_ARRAY,0,0,0,v,n,l,1,t.RGBA,t.UNSIGNED_BYTE,A);const z=t.getError();z!==t.NO_ERROR&&console.error(`glError ${z} loading image #${v} '${E}'`),t.generateMipmap(t.TEXTURE_2D_ARRAY),this.drawProgress(m++/g.data.length)},y.onerror=()=>{console.error(`Error loading image #${v} '${E}'`)}})}}function te(o,e,t,s){const i=document.createElement("canvas");return i.width=e,i.height=t,i.getContext("2d").drawImage(o,0,0,e,t),s&&(i.style.opacity="0.2",s.parentElement.appendChild(i),setTimeout(()=>{s.parentElement.removeChild(i)},1e3)),i}class ie extends P{constructor(e){super(e)}getShaders(){const e=super.getShaders();return e.vs=`#version 300 es
`+e.vs,e.fs=`#version 300 es
`+e.fs,e}}class se extends V{static get componentName(){return"ImageArrayExtension"}getShaders(){return{inject:{"vs:#decl":`
        //---- ImageArrayExtension
        in float imageIndex;
        in float imageAspect;
        out float vImageIndex;
        out float vImageAspect;
        ////
        `,"vs:#main-start":`
        //---- ImageArrayExtension
        vImageIndex = imageIndex;
        vImageAspect = imageAspect;
        ////
        
        `,"vs:#main-end":`
        //---- ImageArrayExtension
        outerRadiusPixels = 1e-3;//HACKACK to make everything 'inCircle' for now
        // - but it breaks opacity, and generally we can do better...
        // it would be good to have border lines back, too
        ////
        
        `,"fs:#decl":`
        //---- ImageArrayExtension
        uniform mediump sampler2DArray imageArray;
        in float vImageIndex;
        in float vImageAspect;
        uniform float opacity;
        
        `,"fs:DECKGL_FILTER_COLOR":`
        //---- ImageArrayExtension
        vec2 uv = 0.5 * (geometry.uv + 1.0);
        uv.y = 1. - uv.y; // flip y
        // todo fix aspect ratio in vertex shader
        uv.x /= min(1., vImageAspect);
        uv.y *= max(1., vImageAspect);
        if (uv.y > 1. || uv.x > 1.) discard;
        vec3 uvw = vec3(uv, vImageIndex);
        vec4 t = texture(imageArray, uvw);
        color *= t;
        ///--- opacity may well not be correct gamma etc
        color.a = t.a * opacity; //HACK so broken inCircle doesn't break opacity
        // color.r = vImageAspect - 0.5;
        // vec3 s = vec3(textureSize(imageArray, 0));
        // uvw.z /= s.z;
        // color.rgb = uvw;
        // color.r = vImageIndex / s.z;
        ////

        `}}}initializeState(e,t){var s;(s=this.getAttributeManager())==null||s.addInstanced({imageIndex:{size:1,accessor:"getImageIndex",defaultValue:0},imageAspect:{size:1,accessor:"getImageAspect",defaultValue:1}})}updateState(e){const{texture:t}=e.props.imageArray;for(const s of this.getModels()){const i=s.gl;i.activeTexture(i.TEXTURE10),i.bindTexture(i.TEXTURE_2D_ARRAY,t),s.setUniforms({imageArray:10})}}}let ae=0;class oe extends x{constructor(t,s,i){super(t,s,i);u(this,"canvas");u(this,"imageArray");u(this,"deck");u(this,"dataModel");u(this,"progress",0);u(this,"billboard",!0);u(this,"size",20);u(this,"opacity",255);u(this,"colorBy");u(this,"id");this.id=ae++;const a=this.canvas=f("canvas",{},this.contentDiv),{base_url:r,image_key:n,texture_size:l}=i.images;this.dataModel=new k(t,{autoUpdate:!1}),this.dataModel.setColumns([...i.param,n,i.image_title]),this.dataModel.updateModel(),this.imageArray=new ee(t,a,this.dataModel,{base_url:r,image_type:"png",image_key:n,width:l,height:l}),this.imageArray.onProgress=c=>{this.progress=c,this.updateDeck()};const g=this.updateDeck(),h=new U;this.deck=new O({canvas:a,layers:g,views:[h],controller:!0,initialViewState:{target:[0,0,0],zoom:0},getTooltip:c=>{const{index:d,picked:m}=c,_=this.config.image_title,p=this.dataModel.getItemField(d,_);return m&&{html:`<div>${_}: '${p}'</div>`}}})}updateDeck(){const{param:t}=this.config,{columnIndex:s}=this.dataStore,i=s[t[0]],a=s[t[1]],r=s[t[2]];function n(d,m){const{minMax:_}=d;return 200*(d.data[m]-_[0])/(_[1]-_[0])-100}const{data:l}=this.dataModel,{imageArray:g,billboard:h}=this,c=new ie({id:`scatter-${this.id}`,data:l,billboard:h,pickable:!0,getImageIndex:d=>g.getImageIndex(d),getImageAspect:d=>g.getImageAspect(d),getPosition:(d,{target:m})=>(m[0]=n(i,d),m[1]=n(a,d),m[2]=n(r,d),m),getRadius:1,radiusScale:this.size,opacity:this.opacity/255,getFillColor:this.colorBy?d=>this.colorBy(d):[255,255,255],imageArray:g,updateTriggers:{getImageAspect:this.progress,getFillColor:[this.colorBy,this.opacity]},extensions:[new se]});return this.deck&&this.deck.setProps({layers:[c]}),[c]}onDataFiltered(t){this.dataModel.updateModel(),this.updateDeck()}colorByColumn(t){this.colorBy=this.getColorFunction(t,!0),this.updateDeck()}getColorOptions(){return{colorby:"all"}}getSettings(){return[...super.getSettings(),{name:"billboard",label:"Billboard",type:"check",current_value:this.billboard,func:t=>{this.billboard=t,this.updateDeck()}},{type:"slider",name:"size",label:"Size",current_value:this.size,min:5,max:100,step:1,continuous:!0,func:t=>{this.size=t,this.updateDeck()}},{type:"slider",name:"opacity",label:"Opacity",current_value:this.opacity,min:0,max:255,step:1,continuous:!0,func:t=>{this.opacity=t,this.updateDeck()}}]}}x.types.ImageScatterChart={class:oe,name:"Image Scatter Plot",required:["images"],methodsUsingColumns:["updateDeck"],configEntriesUsingColumns:["image_key","image_title"],init:(o,e,t)=>{const s=e.images[t.image_set];console.log("ImageScatterChart param",o.param),o.images={base_url:s.base_url,type:"png",image_key:s.key_column,texture_size:t.texture_size},o.image_key=s.key_column},extra_controls:o=>{const e=[];for(let i in o.images)e.push({name:i,value:i});console.log("imageSets",e);const t=o.getLoadedColumns().map(i=>({name:i,value:i})),s=[32,64,128,256,512,1024].map(i=>({name:i,value:i}));return[{type:"dropdown",name:"image_set",label:"Image Set",values:e},{type:"dropdown",name:"image_title",label:"Tooltip",values:t},{type:"dropdown",name:"texture_size",label:"Texture Size",values:s,defaultVal:256}]},params:[{type:"number",name:"X axis"},{type:"number",name:"Y axis"},{type:"number",name:"Z axis"}]};let re=0;function ne({parent:o}){const{dataStore:e}=o,[t]=b.useState(re++),[s,i]=b.useState(e.filterSize),[a]=b.useState(e.getDimension("catcol_dimension")),[r,n]=b.useState(["hello","world"]),[l,g]=b.useState(o.config.text);return b.useEffect(()=>{e.addListener(t,()=>i(e.filterSize)),o.addListener("text",(_,p)=>g(p+" "+o.config.wordSize));const h=o.config.param[0],c=o.config.param[1],d=e.getColumnValues(h),m=e.getColumnValues(c);return e.columnIndex[h],e.columnIndex[c],e.getRowAsObject(),n(d),console.log(m),a&&a.getAverages?a.getAverages(_=>{console.log(_)},[c],{}):console.log("no averages"),()=>{e.removeListener(t),o.removeListener("text")}},[e,a,l]),X("div",{style:{padding:"0.3em",overflow:"auto"},children:[R("h2",{children:"Words:"}),R("pre",{children:JSON.stringify(r,null,2)})]})}class le extends x{constructor(e,t,s){super(e,t,s),N(this.contentDiv).render(R(ne,{parent:this}))}drawChart(){this._callListeners("text","Hello World")}getSettings(){const e=this.config;return super.getSettings().concat([{type:"slider",label:"Word Size",current_value:e.wordSize||100,min:10,max:100,func:s=>{e.wordSize=s,this.drawChart()}}])}remove(){super.remove()}}x.types.WordCloud2={class:le,name:"WordCloud Chart",params:[{type:["text","multitext"],name:"text"},{type:["text","multitext"],name:"word size"}],init:(o,e,t)=>{o.wordSize=20}};function he(o,e){const t={};for(let s of o)t[s.name]=new de(`${e}/${s.name}.b`,s.size);return async(s,i,a)=>await t[i].getColumnData(s,a)}class de{constructor(e,t){this.url=e,this.index=null,this.size=t}async getColumnData(e,t){const{default:s}=await j(()=>import("./pako.esm-0a50cf5c.js"),[],import.meta.url);if(!this.index){const i=this.url.replace(".b",".json"),a=await fetch(i);this.index=await a.json()}return await Promise.all(e.map(async i=>{let a=i.field;if(i.subgroup){const h=i.field.split("|");a=h[0]+h[2]}const r=this.index[a],l=await(await fetch(this.url,{headers:{responseType:"arraybuffer",range:`bytes=${r[0]}-${r[1]}`}})).arrayBuffer(),g=r[1]-r[0]+1;l.byteLength!==g&&console.warn(`Expected ${g} bytes but got ${l.byteLength} for ${i.field}... is the server correctly configured to Accept-Ranges?`);try{const h=s.inflate(l);if(i.sgtype==="sparse"){const c=new Uint32Array(h,0,1)[0],d=new Uint32Array(h,4,c),m=new Float32Array(h,c*4+1,c),_=new SharedArrayBuffer(t*4),p=new Float32Array(_);p.fill(NaN);for(let w=0;w<d.length;w++)p[d[w]]=m[w];return{data:_,field:i.field}}else{const c=new SharedArrayBuffer(h.length);return new Uint8Array(c).set(h,0),{data:c,field:i.field}}}catch(h){console.warn(`Error inflating ${i.field}: ${h}`)}}))}}console.log(H);document.addEventListener("DOMContentLoaded",()=>ge());const D=new URLSearchParams(window.location.search),S=D.get("dir");if(!S){const o=prompt("Enter data URL","https://mdvstatic.netlify.app/ytrap2");D.set("dir",o);const e=document.location.href+"?"+D.toString();document.location=e}const T=S.endsWith("/")?S.substring(0,S.length-1):S;document.title=`MDV - ${T}`;function M(o){if(Array.isArray(o)){for(const e of o)M(e);return}for(const e in o)e==="base_url"?o[e]=o[e].replace("./",`${T}/`):typeof o[e]=="object"&&M(o[e])}async function C(o){const t=await(await fetch(o)).json();return M(t),t}async function ce(o,e){e||(e={});let t={method:o,args:e};console.log("window.CSRF_TOKEN",window.CSRF_TOKEN);const s=new Request("meths/execute_project_action/",{method:"POST",headers:{"X-CSRFToken":window.CSRFTOKEN,Accept:"application/json,text/plain,*/*","Content-Type":"application/json"},mode:"same-origin",body:JSON.stringify(t)}),i=await fetch(s);let a={success:!1};try{a=await i.json()}catch(r){console.error(r)}return a}function me(o,e,t){switch(o){case"state_saved":console.log("listener state_saved",e,t),ce("save_state",{state:t}).then(s=>{s.success?(e.createInfoAlert("Data Saved",{duration:2e3}),e.setAllColumnsClean()):e.createInfoAlert("UnableToSaveData",{duration:3e3,type:"danger"})});break}}async function ge(){const o=await C(`${T}/datasources.json`),e=await C(`${T}/state.json`),t=await C(`${T}/views.json`),s={function:he(o,T),viewLoader:async l=>t[l]},i=new W("app1",o,s,e,me),a=o[0].name,r=i.dsIndex[a],n=new Y(r.dataStore);setTimeout(()=>{i.addMenuIcon(a,"fas fa-tags","Tag Annotation",()=>{new K(r.dataStore,n)}),i.addMenuIcon(a,"fas fa-tags","Tag Annotation (react)",()=>{new G.experiment.AnnotationDialogReact(r.dataStore,n)}),i.addMenuIcon(a,"fas fa-spinner","Pre-Load Data",async()=>{const l=o[0].columns.map(g=>g.name);i.loadColumnSet(l,a,()=>{console.log("done loadColumnSet")})})},0)}