
window.RGraph=window.RGraph||{isRGraph:true};(function(win,doc,undefined)
{var ua=navigator.userAgent;RGraph.Highlight={};RGraph.Registry={};RGraph.Registry.store=[];RGraph.Registry.store['event.handlers']=[];RGraph.Registry.store['__rgraph_event_listeners__']=[];RGraph.Background={};RGraph.background={};RGraph.objects=[];RGraph.Resizing={};RGraph.events=[];RGraph.cursor=[];RGraph.Effects=RGraph.Effects||{};RGraph.cache=[];RGraph.ObjectRegistry={};RGraph.ObjectRegistry.objects={};RGraph.ObjectRegistry.objects.byUID=[];RGraph.ObjectRegistry.objects.byCanvasID=[];RGraph.OR=RGraph.ObjectRegistry;RGraph.PI=Math.PI;RGraph.HALFPI=RGraph.PI/2;RGraph.TWOPI=RGraph.PI*2;RGraph.ISFF=ua.indexOf('Firefox')!=-1;RGraph.ISOPERA=ua.indexOf('Opera')!=-1;RGraph.ISCHROME=ua.indexOf('Chrome')!=-1;RGraph.ISSAFARI=ua.indexOf('Safari')!=-1&&!RGraph.ISCHROME;RGraph.ISWEBKIT=ua.indexOf('WebKit')!=-1;RGraph.ISIE=ua.indexOf('Trident')>0||navigator.userAgent.indexOf('MSIE')>0;RGraph.ISIE6=ua.indexOf('MSIE 6')>0;RGraph.ISIE7=ua.indexOf('MSIE 7')>0;RGraph.ISIE8=ua.indexOf('MSIE 8')>0;RGraph.ISIE9=ua.indexOf('MSIE 9')>0;RGraph.ISIE10=ua.indexOf('MSIE 10')>0;RGraph.ISOLD=RGraph.ISIE6||RGraph.ISIE7||RGraph.ISIE8;RGraph.ISIE11UP=ua.indexOf('MSIE')==-1&&ua.indexOf('Trident')>0;RGraph.ISIE10UP=RGraph.ISIE10||RGraph.ISIE11UP;RGraph.ISIE9UP=RGraph.ISIE9||RGraph.ISIE10UP;RGraph.getScale2=RGraph.getScale=function(args)
{var prop=args.object.properties,numlabels=typeof args.options['scale.labels.count']=='number'?args.options['scale.labels.count']:5,units_pre=typeof args.options['scale.units.pre']=='string'?args.options['scale.units.pre']:'',units_post=typeof args.options['scale.units.post']=='string'?args.options['scale.units.post']:'',max=Number(args.options['scale.max']),min=typeof args.options['scale.min']=='number'?args.options['scale.min']:0,strict=args.options['scale.strict'],decimals=Number(args.options['scale.decimals']),point=args.options['scale.point'],thousand=args.options['scale.thousand'],original_max=max,round=args.options['scale.round'],scale={max:1,labels:[],values:[]},formatter=args.options['scale.formatter'];prefix=args.object.type==='hbar'?'xaxis':'yaxis';prefix=args.object.type==='odo'?'':prefix;if(!max){var max=1;for(var i=0;i<numlabels;++i){var label=((((max-min)/numlabels)+min)*(i+1)).toFixed(decimals);scale.labels.push(units_pre+label+units_post);scale.values.push(parseFloat(label))}}else if(max<=1&&!strict){var arr=[1,0.5,0.10,0.05,0.010,0.005,0.0010,0.0005,0.00010,0.00005,0.000010,0.000005,0.0000010,0.0000005,0.00000010,0.00000005,0.000000010,0.000000005,0.0000000010,0.0000000005,0.00000000010,0.00000000005,0.000000000010,0.000000000005,0.0000000000010,0.0000000000005],vals=[];for(var i=0;i<arr.length;++i){if(max>arr[i]){i--;break;}}
scale.max=arr[i]
scale.labels=[];scale.values=[];for(var j=0;j<numlabels;++j){var value=((((arr[i]-min)/numlabels)*(j+1))+min).toFixed(decimals);scale.values.push(value);scale.labels.push(RGraph.numberFormat({object:args.object,number:value,unitspre:units_pre,unitspost:units_post,thousand:thousand,point:point,formatter:formatter,decimals:decimals}));}}else if(!strict){max=Math.ceil(max);var interval=Math.pow(10,Math.max(1,Number(String(Number(max)-Number(min)).length-1)));var topValue=interval;while(topValue<max){topValue+=(interval/2);}
if(Number(original_max)>Number(topValue)){topValue+=(interval/2);}
if(max<=10){topValue=(Number(original_max)<=5?5:10);}
if(args.object&&typeof round=='boolean'&&round){topValue=10*interval;}
scale.max=topValue;var tmp_point=prop[prefix+'ScalePoint'];var tmp_thousand=prop[prefix+'ScaleThousand'];args.object.set(prefix+'scaleThousand',thousand);args.object.set(prefix+'scalePoint',point);for(var i=0;i<numlabels;++i){scale.labels.push(RGraph.numberFormat({object:args.object,number:((((i+1)/numlabels)*(topValue-min))+min).toFixed(decimals),unitspre:units_pre,unitspost:units_post,point:point,thousand:thousand,formatter:formatter}));scale.values.push(((((i+1)/numlabels)*(topValue-min))+min).toFixed(decimals));}
args.object.set(prefix+'scaleThousand',tmp_thousand);args.object.set(prefix+'scalePoint',tmp_point);}else if(typeof max=='number'&&strict){for(var i=0;i<numlabels;++i){scale.labels.push(RGraph.numberFormat({object:args.object,number:((((i+1)/numlabels)*(max-min))+min).toFixed(decimals),unitspre:units_pre,unitspost:units_post,thousand:thousand,point:point,formatter:formatter}));scale.values.push(((((i+1)/numlabels)*(max-min))+min).toFixed(decimals));}
scale.max=max;}
scale.units_pre=units_pre;scale.units_post=units_post;scale.point=point;scale.decimals=decimals;scale.thousand=thousand;scale.numlabels=numlabels;scale.round=Boolean(round);scale.min=min;scale.formatter=formatter;for(var i=0;i<scale.values.length;++i){scale.values[i]=parseFloat(scale.values[i]);}
return scale;};RGraph.parseJSONGradient=function(args)
{var obj=args.object,def=args.def,context=args.object.context;def=eval("("+def+")");if(typeof def.r1==='number'&&typeof def.r2==='number'){var grad=context.createRadialGradient(def.x1,def.y1,def.r1,def.x2,def.y2,def.r2);}else{var grad=context.createLinearGradient(def.x1,def.y1,def.x2,def.y2);}
var diff=1/(def.colors.length-1);grad.addColorStop(0,RGraph.trim(def.colors[0]));for(var j=1,len=def.colors.length;j<len;++j){grad.addColorStop(j*diff,RGraph.trim(def.colors[j]));}
return grad;};RGraph.arrayInvert=function(arr)
{for(var i=0,len=arr.length;i<len;++i){arr[i]=!arr[i];}
return arr;};RGraph.arrayTrim=function(arr)
{var out=[],content=false;for(var i=0;i<arr.length;i++){if(arr[i]){content=true;}
if(content){out.push(arr[i]);}}
out=RGraph.arrayReverse(out);var out2=[],content=false;for(var i=0;i<out.length;i++){if(out[i]){content=true;}
if(content){out2.push(out[i]);}}
out2=RGraph.arrayReverse(out2);return out2;};RGraph.arrayClone=RGraph.array_clone=function(obj)
{if(obj===null||typeof obj!=='object'){return obj;}
var temp=RGraph.isArray(obj)?[]:{};for(var i in obj){if(typeof i==='string'||typeof i==='number'){if(typeof obj[i]==='number'){temp[i]=(function(arg){return Number(arg);})(obj[i]);}else if(typeof obj[i]==='string'){temp[i]=(function(arg){return String(arg);})(obj[i]);}else if(typeof obj[i]==='function'){temp[i]=obj[i];}else{temp[i]=RGraph.arrayClone(obj[i]);}}}
return temp;};RGraph.arrayMax=RGraph.array_max=function(arr)
{var max=null,ma=Math
if(typeof arr==='number'){return arr;}
if(RGraph.isNull(arr)){return 0;}
for(var i=0,len=arr.length;i<len;++i){if(typeof arr[i]==='number'&&!isNaN(arr[i])){var val=arguments[1]?Math.abs(arr[i]):arr[i];if(typeof max==='number'){max=Math.max(max,val);}else{max=val;}}}
return max;};RGraph.arrayMin=function(arr)
{var max=null,min=null,ma=Math;if(typeof arr==='number'){return arr;}
if(RGraph.isNull(arr)){return 0;}
for(var i=0,len=arr.length;i<len;++i){if(typeof arr[i]==='number'){var val=arguments[1]?Math.abs(arr[i]):arr[i];if(typeof min==='number'){min=Math.min(min,val);}else{min=val;}}}
return min;};RGraph.arrayPad=RGraph.array_pad=function(arr,len)
{if(arr.length<len){var val=arguments[2]?arguments[2]:null;for(var i=arr.length;i<len;i+=1){arr[i]=val;}}
return arr;};RGraph.arraySum=RGraph.array_sum=function(arr)
{if(typeof arr==='number'){return arr;}
if(RGraph.isNull(arr)){return 0;}
var i,sum,len=arr.length;for(i=0,sum=0;i<len;sum+=(arr[i++]||0));return sum;};RGraph.arrayLinearize=RGraph.array_linearize=function()
{var arr=[],args=arguments
for(var i=0,len=args.length;i<len;++i){if(typeof args[i]==='object'&&args[i]){for(var j=0,len2=args[i].length;j<len2;++j){var sub=RGraph.arrayLinearize(args[i][j]);for(var k=0,len3=sub.length;k<len3;++k){arr.push(sub[k]);}}}else{arr.push(args[i]);}}
return arr;};RGraph.arrayShift=RGraph.array_shift=function(arr)
{var ret=[];for(var i=1,len=arr.length;i<len;++i){ret.push(arr[i]);}
return ret;};RGraph.arrayReverse=RGraph.array_reverse=function(arr)
{if(!arr){return;}
var newarr=[];for(var i=arr.length-1;i>=0;i-=1){newarr.push(arr[i]);}
return newarr;};RGraph.abs=function(value)
{if(typeof value==='string'){value=parseFloat(value)||0;}
if(typeof value==='number'){return Math.abs(value);}
if(typeof value==='object'){for(i in value){if(typeof i==='string'||typeof i==='number'||typeof i==='object'){value[i]=RGraph.abs(value[i]);}}
return value;}
return 0;};RGraph.clear=RGraph.Clear=function(canvas)
{var obj=canvas.__object__;var context=canvas.getContext('2d');var color=arguments[1]||(obj&&obj.get('clearto'));if(!canvas){return;}
RGraph.fireCustomEvent(obj,'onbeforeclear');if(RGraph.text.domNodeCache&&RGraph.text.domNodeCache[canvas.id]){for(var i in RGraph.text.domNodeCache[canvas.id]){var el=RGraph.text.domNodeCache[canvas.id][i];if(el&&el.style){el.style.display='none';}}}
if(!color||(color&&color==='rgba(0,0,0,0)'||color==='transparent')){context.clearRect(-100,-100,canvas.width+200,canvas.height+200);context.globalCompositeOperation='source-over';}else if(color){RGraph.path(context,'fs % fr -100 -100 % %',color,canvas.width+200,canvas.height+200);}else{RGraph.path(context,'fs % fr -100 -100 % %',obj.get('clearto'),canvas.width+200,canvas.height+200);}
if(RGraph.Registry.get('background.image.'+canvas.id)){var img=RGraph.Registry.get('background.image.'+canvas.id);img.style.position='absolute';img.style.left='-10000px';img.style.top='-10000px';}
if(RGraph.Registry.get('tooltip')&&obj&&!obj.get('tooltipsNohideonclear')){RGraph.hideTooltip(canvas);}
canvas.style.cursor='default';RGraph.fireCustomEvent(obj,'onclear');};RGraph.drawTitle=RGraph.DrawTitle=function(obj,text,marginTop)
{var canvas=obj.canvas,context=obj.context,prop=obj.properties,marginLeft=prop.marginLeft,marginRight=prop.marginRight,marginTop=marginTop,marginBottom=prop.marginBottom,centerx=(arguments[3]?arguments[3]:((canvas.width-marginLeft-marginRight)/2)+marginLeft),keypos=prop.keyPosition,vpos=prop.titleVpos,hpos=prop.titleHpos,bgcolor=prop.titleBackground,x=prop.titleX,y=prop.titleY,halign='center',valign='center',textConf=RGraph.getTextConf({object:obj,prefix:'title'});var size=textConf.size,bold=textConf.bold,italic=textConf.italic;if(RGraph.isNull(bold)){textConf.bold=true;bold=true;}
if(obj.type=='bar'&&prop.variant=='3d'){keypos='margin';}
context.beginPath();context.fillStyle=textConf.color?textConf.color:'black';if(keypos&&keypos!='margin'){var valign='center';}else if(!keypos){var valign='center';}else{var valign='bottom';}
if(typeof prop.titleVpos==='number'){vpos=prop.titleVpos*marginTop;if(prop.xaxisPosition==='top'){vpos=prop.titleVpos*marginBottom+marginTop+(canvas.height-marginTop-marginBottom);}}else{vpos=marginTop-size-5;if(prop.xaxisPosition==='top'){vpos=canvas.height-marginBottom+size+5;}}
if(typeof hpos==='number'){centerx=hpos*canvas.width;}
if(typeof x==='number')centerx=x;if(typeof y==='number')vpos=y;if(typeof x==='string')centerx+=parseFloat(x);if(typeof y==='string')vpos+=parseFloat(y);if(typeof prop.titleHalign==='string'){halign=prop.titleHalign;}
if(typeof prop.titleValign==='string'){valign=prop.titleValign;}
if(typeof textConf.color!==null){var oldColor=context.fillStyle,newColor=textConf.color;context.fillStyle=newColor?newColor:'black';}
var ret=RGraph.text({object:obj,font:textConf.font,size:textConf.size,color:textConf.color,bold:textConf.bold,italic:textConf.italic,x:centerx,y:vpos,text:text,valign:valign,halign:halign,bounding:bgcolor!=null,'bounding.fill':bgcolor,tag:'title',marker:false});context.fillStyle=oldColor;};RGraph.getMouseXY=function(e)
{if(!e.target){return;}
var el=e.target,canvas=el,caStyle=canvas.style,offsetX=0,offsetY=0,x,y,borderLeft=parseInt(caStyle.borderLeftWidth)||0,borderTop=parseInt(caStyle.borderTopWidth)||0,paddingLeft=parseInt(caStyle.paddingLeft)||0,paddingTop=parseInt(caStyle.paddingTop)||0,additionalX=borderLeft+paddingLeft,additionalY=borderTop+paddingTop;if(typeof e.offsetX==='number'&&typeof e.offsetY==='number'){if(!RGraph.ISIE&&!RGraph.ISOPERA){x=e.offsetX-borderLeft-paddingLeft;y=e.offsetY-borderTop-paddingTop;}else if(RGraph.ISIE){x=e.offsetX-paddingLeft;y=e.offsetY-paddingTop;}else{x=e.offsetX;y=e.offsetY;}}else{if(typeof el.offsetParent!=='undefined'){do{offsetX+=el.offsetLeft;offsetY+=el.offsetTop;}while((el=el.offsetParent));}
x=e.pageX-offsetX-additionalX;y=e.pageY-offsetY-additionalY;x-=(2*(parseInt(document.body.style.borderLeftWidth)||0));y-=(2*(parseInt(document.body.style.borderTopWidth)||0));}
return[x,y];};RGraph.getCanvasXY=function(canvas)
{var x=0;var y=0;var el=canvas;do{x+=el.offsetLeft;y+=el.offsetTop;if(el.tagName.toLowerCase()=='table'&&(RGraph.ISCHROME||RGraph.ISSAFARI)){x+=parseInt(el.border)||0;y+=parseInt(el.border)||0;}
el=el.offsetParent;}while(el&&el.tagName.toLowerCase()!='body');var paddingLeft=canvas.style.paddingLeft?parseInt(canvas.style.paddingLeft):0;var paddingTop=canvas.style.paddingTop?parseInt(canvas.style.paddingTop):0;var borderLeft=canvas.style.borderLeftWidth?parseInt(canvas.style.borderLeftWidth):0;var borderTop=canvas.style.borderTopWidth?parseInt(canvas.style.borderTopWidth):0;if(navigator.userAgent.indexOf('Firefox')>0){x+=parseInt(document.body.style.borderLeftWidth)||0;y+=parseInt(document.body.style.borderTopWidth)||0;}
return[x+paddingLeft+borderLeft,y+paddingTop+borderTop];};RGraph.isFixed=function(canvas)
{var obj=canvas;var i=0;while(obj&&obj.tagName.toLowerCase()!='body'&&i<99){if(obj.style.position=='fixed'){return obj;}
obj=obj.offsetParent;}
return false;};RGraph.register=RGraph.Register=function(obj)
{if(!obj.get('noregister')&&obj.get('register')!==false){RGraph.ObjectRegistry.add(obj);obj.set('register',false);}};RGraph.redraw=RGraph.Redraw=function()
{var objectRegistry=RGraph.ObjectRegistry.objects.byCanvasID;var tags=document.getElementsByTagName('canvas');for(var i=0,len=tags.length;i<len;++i){if(tags[i]&&tags[i].__object__&&tags[i].__object__.isRGraph){if(!tags[i].noclear){RGraph.clear(tags[i],arguments[0]?arguments[0]:null);}}}
for(var i=0,len=objectRegistry.length;i<len;++i){if(objectRegistry[i]){var id=objectRegistry[i][0];objectRegistry[i][1].draw();}}};RGraph.redrawCanvas=RGraph.RedrawCanvas=function(canvas)
{var objects=RGraph.ObjectRegistry.getObjectsByCanvasID(canvas.id);if(!arguments[1]||(typeof arguments[1]==='boolean'&&!arguments[1]==false)){var color=arguments[2]||canvas.__object__.get('clearto')||'transparent';RGraph.clear(canvas,color);}
for(var i=0,len=objects.length;i<len;++i){if(objects[i]){if(objects[i]&&objects[i].isRGraph){objects[i].draw();}}}};RGraph.Background.draw=RGraph.Background.Draw=RGraph.background.draw=RGraph.background.Draw=function(obj)
{var prop=obj.properties,height=0,marginLeft=obj.marginLeft,marginRight=obj.marginRight,marginTop=obj.marginTop,marginBottom=obj.marginBottom,variant=prop.variant
obj.context.fillStyle=prop.textColor;if(variant=='3d'){obj.context.save();obj.context.translate(prop.variantThreedOffsetx,-1*prop.variantThreedOffsety);}
if(typeof prop.xaxisTitle==='string'&&prop.xaxisTitle.length){var size=prop.textSize+2;var hpos=((obj.canvas.width-marginLeft-marginRight)/2)+marginLeft;var vpos=obj.canvas.height-marginBottom+25;if(typeof prop.xaxisTitlePos==='number'){vpos=obj.canvas.height-(marginBottom*prop.xaxisTitlePos);}
if(typeof prop.xaxisTitleX==='number'){hpos=prop.xaxisTitleX;}
if(typeof prop.xaxisTitleY==='number'){vpos=prop.xaxisTitleY;}
var textConf=RGraph.getTextConf({object:obj,prefix:'xaxisTitle'});RGraph.text({object:obj,font:textConf.font,size:textConf.size,color:textConf.color,bold:textConf.bold,italic:textConf.italic,x:hpos,y:vpos,text:prop.xaxisTitle,halign:'center',valign:'top',tag:'xaxis.title'});}
if(typeof(prop.yaxisTitle)==='string'&&prop.yaxisTitle.length){var size=prop.textSize+2;var font=prop.textFont;var italic=prop.textItalic;var angle=270;var bold=prop.yaxisTitleBold;var color=prop.yaxisTitleColor;if(typeof prop.yaxisTitlePos=='number'){var yaxis_title_pos=prop.yaxisTitlePos*marginLeft;}else if(obj.type==='hbar'&&RGraph.isNull(prop.yaxisTitlePos)){var yaxis_title_pos=prop.marginLeft-obj.yaxisLabelsSize;}else{if(obj&&obj.scale2){var yaxisTitleDimensions=RGraph.measureText({text:obj.scale2.labels[obj.scale2.labels.length-1],bold:typeof prop.yaxisScaleBold==='boolean'?prop.yaxisScaleBold:prop.textBold,font:prop.yaxisScaleFont||prop.textFont,size:typeof prop.yaxisScaleSize==='number'?prop.yaxisScaleSize:prop.textSize});}else{yaxisTitleDimensions=[0,0];}
var yaxis_title_pos=prop.marginLeft-yaxisTitleDimensions[0]-7;}
if(typeof prop.yaxisTitleSize==='number'){size=prop.yaxisTitleSize;}
if(typeof prop.yaxisTitleItalic==='boolean'){italic=prop.yaxisTitleItalic;}
if(typeof prop.yaxisTitleFont==='string'){font=prop.yaxisTitleFont;}
if(prop.yaxisTitleAlign=='right'||prop.yaxisTitlePosition=='right'||(obj.type==='hbar'&&prop.yaxisPosition==='right'&&typeof prop.yaxisTitleAlign==='undefined'&&typeof prop.yaxisTitlePosition==='undefined')){angle=90;yaxis_title_pos=typeof prop.yaxisTitlePos==='number'?(obj.canvas.width-marginRight)+(prop.yaxisTitlePos*marginRight):obj.canvas.width-marginRight+(prop.yaxisLabelsSize||prop.textSize)+10;}
var y=((obj.canvas.height-marginTop-marginBottom)/2)+marginTop;if(typeof prop.yaxisTitleX==='number'){yaxis_title_pos=prop.yaxisTitleX;}
if(typeof prop.yaxisTitleY==='number'){y=prop.yaxisTitleY;}
obj.context.fillStyle=color;var textConf=RGraph.getTextConf({object:obj,prefix:'yaxisTitle'});RGraph.text({object:obj,font:textConf.font,size:textConf.size,color:textConf.color,bold:textConf.bold,italic:textConf.italic,x:yaxis_title_pos,y:y,valign:'bottom',halign:'center',angle:angle,text:prop.yaxisTitle,tag:'yaxis.title',accessible:false});}
var bgcolor=prop.backgroundColor;if(bgcolor){obj.context.fillStyle=bgcolor;obj.context.fillRect(marginLeft+0.5,marginTop+0.5,obj.canvas.width-marginLeft-marginRight,obj.canvas.height-marginTop-marginBottom);}
var numbars=(prop.yaxisLabelsCount||5);if(typeof prop.backgroundBarsCount==='number'){numbars=prop.backgroundBarsCount;}
var barHeight=(obj.canvas.height-marginBottom-marginTop)/numbars;obj.context.beginPath();obj.context.fillStyle=prop.backgroundBarsColor1;obj.context.strokeStyle=obj.context.fillStyle;height=(obj.canvas.height-marginBottom);for(var i=0;i<numbars;i+=2){obj.context.rect(marginLeft,(i*barHeight)+marginTop,obj.canvas.width-marginLeft-marginRight,barHeight);}
obj.context.fill();obj.context.beginPath();obj.context.fillStyle=prop.backgroundBarsColor2;obj.context.strokeStyle=obj.context.fillStyle;for(var i=1;i<numbars;i+=2){obj.context.rect(marginLeft,(i*barHeight)+marginTop,obj.canvas.width-marginLeft-marginRight,barHeight);}
obj.context.fill();obj.context.beginPath();var func=function(obj,cacheCanvas,cacheContext)
{if(prop.backgroundGrid){prop.backgroundGridHlinesCount+=0.0001;if(prop.backgroundGridAutofit){if(prop.backgroundGridAutofitAlign){if(obj.type==='hbar'){obj.set('backgroundGridHlinesCount',obj.data.length);}
if(obj.type==='line'){if(typeof prop.backgroundGridVlinesCount==='number'){}else if(prop.xaxisLabels&&prop.xaxisLabels.length){obj.set('backgroundGridVlinesCount',prop.xaxisLabels.length-1);}else{obj.set('backgroundGridVlinesCount',obj.data[0].length-1);}}else if(obj.type==='waterfall'){obj.set('backgroundGridVlinesCount',obj.data.length+(prop.total?1:0));}else if(obj.type==='bar'){obj.set('backgroundGridVlinesCount',obj.data.length);}else if(obj.type==='scatter'){if(typeof prop.backgroundGridVlinesCount!=='number'){if(RGraph.isArray(prop.xaxisLabels)&&prop.xaxisLabels.length){obj.set('backgroundGridVlinesCount',prop.xaxisLabels.length);}else{obj.set('backgroundGridVlinesCount',10);}}}else if(obj.type==='gantt'){if(typeof obj.get('backgroundGridVlinesCount')==='number'){}else{obj.set('backgroundGridVlinesCount',prop.xaxisScaleMax);}
obj.set('backgroundGridHlinesCount',obj.data.length);}else if(obj.type==='hbar'&&RGraph.isNull(prop.backgroundGridHlinesCount)){obj.set('backgroundGridHlinesCount',obj.data.length);}}
var vsize=((cacheCanvas.width-marginLeft-marginRight))/prop.backgroundGridVlinesCount;var hsize=(cacheCanvas.height-marginTop-marginBottom)/prop.backgroundGridHlinesCount;obj.set('backgroundGridVsize',vsize);obj.set('backgroundGridHsize',hsize);}
obj.context.beginPath();cacheContext.lineWidth=prop.backgroundGridLinewidth?prop.backgroundGridLinewidth:1;cacheContext.strokeStyle=prop.backgroundGridColor;if(prop.backgroundGridDashed&&typeof cacheContext.setLineDash=='function'){cacheContext.setLineDash([3,5]);}
if(prop.backgroundGridDotted&&typeof cacheContext.setLineDash=='function'){cacheContext.setLineDash([1,3]);}
obj.context.beginPath();if(prop.backgroundGridHlines){height=(cacheCanvas.height-marginBottom)
var hsize=prop.backgroundGridHsize;for(y=marginTop;y<=height;y+=hsize){cacheContext.moveTo(marginLeft,Math.round(y));cacheContext.lineTo(obj.canvas.width-marginRight,Math.round(y));}}
if(prop.backgroundGridVlines){var width=(cacheCanvas.width-marginRight);var vsize=prop.backgroundGridVsize;for(var x=marginLeft;Math.round(x)<=width;x+=vsize){cacheContext.moveTo(Math.round(x),marginTop);cacheContext.lineTo(Math.round(x),obj.canvas.height-marginBottom);}}
if(prop.backgroundGridBorder){cacheContext.strokeStyle=prop.backgroundGridColor;cacheContext.strokeRect(Math.round(marginLeft),Math.round(marginTop),obj.canvas.width-marginLeft-marginRight,obj.canvas.height-marginTop-marginBottom);}}
cacheContext.stroke();cacheContext.beginPath();cacheContext.closePath();}
RGraph.cachedDraw(obj,obj.uid+'_background',func);if(variant=='3d'){obj.context.restore();}
if(typeof obj.context.setLineDash=='function'){obj.context.setLineDash([1,0]);}
obj.context.stroke();if(typeof(obj.properties.title)=='string'){var prop=obj.properties;RGraph.drawTitle(obj,prop.title,obj.marginTop,null,prop.titleSize?prop.titleSize:prop.textSize+2,obj);}};RGraph.numberFormat=RGraph.number_format=function(opt)
{var prop=opt.object.properties;var i;var prepend=opt.unitspre?String(opt.unitspre):'';var append=opt.unitspost?String(opt.unitspost):'';var output='';var decimal='';var decimal_seperator=typeof opt.point==='string'?opt.point:'.';var thousand_seperator=typeof opt.thousand==='string'?opt.thousand:',';RegExp.$1='';var i,j;if(typeof opt.formatter==='function'){return(opt.formatter)(opt);}
if(String(opt.number).indexOf('e')>0){return String(prepend+String(opt.number)+append);}
opt.number=String(opt.number);if(opt.number.indexOf('.')>0){var tmp=opt.number;opt.number=opt.number.replace(/\.(.*)/,'');decimal=tmp.replace(/(.*)\.(.*)/,'$2');}
var seperator=thousand_seperator;var foundPoint;for(i=(opt.number.length-1),j=0;i>=0;j++,i--){var character=opt.number.charAt(i);if(j%3==0&&j!=0){output+=seperator;}
output+=character;}
var rev=output;output='';for(i=(rev.length-1);i>=0;i--){output+=rev.charAt(i);}
if(output.indexOf('-'+opt.thousand)==0){output='-'+output.substr(('-'+opt.thousand).length);}
if(decimal.length){output=output+decimal_seperator+decimal;decimal='';RegExp.$1='';}
if(output.charAt(0)=='-'){output=output.replace(/-/,'');prepend='-'+prepend;}
output=output.replace(/^,+/,'');return prepend+output+append;};RGraph.drawBars=RGraph.DrawBars=function(obj)
{var prop=obj.properties;var hbars=prop.backgroundHbars;if(hbars===null){return;}
obj.context.beginPath();for(var i=0,len=hbars.length;i<len;++i){var start=hbars[i][0];var length=hbars[i][1];var color=hbars[i][2];if(RGraph.is_null(start))start=obj.scale2.max
if(start>obj.scale2.max)start=obj.scale2.max;if(RGraph.isNull(length))length=obj.scale2.max-start;if(start+length>obj.scale2.max)length=obj.scale2.max-start;if(start+length<(-1*obj.scale2.max))length=(-1*obj.scale2.max)-start;if(prop.xaxisPosition=='center'&&start==obj.scale2.max&&length<(obj.scale2.max* -2)){length=obj.scale2.max* -2;}
var x=prop.marginLeft;var y=obj.getYCoord(start);var w=obj.canvas.width-prop.marginLeft-prop.marginRight;var h=obj.getYCoord(start+length)-y;if(RGraph.ISOPERA!=-1&&prop.xaxisPosition=='center'&&h<0){h*=-1;y=y-h;}
if(prop.xaxisPosition=='top'){y=obj.canvas.height-y;h*=-1;}
obj.context.fillStyle=color;obj.context.fillRect(x,y,w,h);}};RGraph.drawInGraphLabels=RGraph.DrawInGraphLabels=function(obj)
{var prop=obj.properties,labels=prop.labelsIngraph,labels_processed=[];var fgcolor='black',bgcolor='white',direction=1;if(!labels){return;}
var textConf=RGraph.getTextConf({object:obj,prefix:'labelsIngraph'});for(var i=0,len=labels.length;i<len;i+=1){if(typeof labels[i]==='number'){for(var j=0;j<labels[i];++j){labels_processed.push(null);}}else if(typeof labels[i]==='string'||typeof labels[i]==='object'){labels_processed.push(labels[i]);}else{labels_processed.push('');}}
RGraph.noShadow(obj);if(labels_processed&&labels_processed.length>0){for(var i=0,len=labels_processed.length;i<len;i+=1){if(labels_processed[i]){var coords=obj.coords[i];if(coords&&coords.length>0){var x=(obj.type=='bar'?coords[0]+(coords[2]/2):coords[0]);var y=(obj.type=='bar'?coords[1]+(coords[3]/2):coords[1]);var length=typeof labels_processed[i][4]==='number'?labels_processed[i][4]:25;obj.context.beginPath();obj.context.fillStyle='black';obj.context.strokeStyle='black';if(obj.type==='bar'){if(obj.get('xaxisPosition')=='top'){length*=-1;}
if(prop.variant=='dot'){obj.context.moveTo(Math.round(x),obj.coords[i][1]-5);obj.context.lineTo(Math.round(x),obj.coords[i][1]-5-length);var text_x=Math.round(x);var text_y=obj.coords[i][1]-5-length;}else if(prop.variant=='arrow'){obj.context.moveTo(Math.round(x),obj.coords[i][1]-5);obj.context.lineTo(Math.round(x),obj.coords[i][1]-5-length);var text_x=Math.round(x);var text_y=obj.coords[i][1]-5-length;}else{obj.context.arc(Math.round(x),y,2.5,0,6.28,0);obj.context.moveTo(Math.round(x),y);obj.context.lineTo(Math.round(x),y-length);var text_x=Math.round(x);var text_y=y-length;}
obj.context.stroke();obj.context.fill();}else{if(typeof labels_processed[i]=='object'&&typeof labels_processed[i][3]=='number'&&labels_processed[i][3]==-1){drawUpArrow(x,y)
var valign='top';var text_x=x;var text_y=y+5+length;}else{var text_x=x;var text_y=y-5-length;if(text_y<5&&(typeof labels_processed[i]==='string'||typeof labels_processed[i][3]==='undefined')){text_y=y+5+length;var valign='top';}
if(valign==='top'){drawUpArrow(x,y);}else{drawDownArrow(x,y);}}
obj.context.fill();}
obj.context.beginPath();obj.context.fillStyle=(typeof labels_processed[i]==='object'&&typeof labels_processed[i][1]==='string')?labels_processed[i][1]:'black';RGraph.text({object:obj,font:textConf.font,size:textConf.size,color:textConf.color,bold:textConf.bold,italic:textConf.italic,x:text_x,y:text_y+(obj.properties.textAccessible?2:0),text:(typeof labels_processed[i]==='object'&&typeof labels_processed[i][0]==='string')?labels_processed[i][0]:labels_processed[i],valign:valign||'bottom',halign:'center',bounding:true,'bounding.fill':(typeof labels_processed[i]==='object'&&typeof labels_processed[i][2]==='string')?labels_processed[i][2]:'white',tag:'labels ingraph'});obj.context.fill();}
function drawUpArrow(x,y)
{obj.context.moveTo(Math.round(x),y+5);obj.context.lineTo(Math.round(x),y+5+length);obj.context.stroke();obj.context.beginPath();obj.context.moveTo(Math.round(x),y+5);obj.context.lineTo(Math.round(x)-3,y+10);obj.context.lineTo(Math.round(x)+3,y+10);obj.context.closePath();}
function drawDownArrow(x,y)
{obj.context.moveTo(Math.round(x),y-5);obj.context.lineTo(Math.round(x),y-5-length);obj.context.stroke();obj.context.beginPath();obj.context.moveTo(Math.round(x),y-5);obj.context.lineTo(Math.round(x)-3,y-10);obj.context.lineTo(Math.round(x)+3,y-10);obj.context.closePath();}
valign=undefined;}}}};RGraph.fixEventObject=RGraph.FixEventObject=function(e)
{if(RGraph.ISOLD){var e=event;e.pageX=(event.clientX+doc.body.scrollLeft);e.pageY=(event.clientY+doc.body.scrollTop);e.target=event.srcElement;if(!doc.body.scrollTop&&doc.documentElement.scrollTop){e.pageX+=parseInt(doc.documentElement.scrollLeft);e.pageY+=parseInt(doc.documentElement.scrollTop);}}
if(!e.stopPropagation){e.stopPropagation=function(){window.event.cancelBubble=true;}}
return e;};RGraph.hideCrosshairCoords=RGraph.HideCrosshairCoords=function()
{var div=RGraph.Registry.get('coordinates.coords.div');if(div&&div.style.opacity==1&&div.__object__.get('crosshairsCoordsFadeout')){var style=RGraph.Registry.get('coordinates.coords.div').style;setTimeout(function(){style.opacity=0.9;},25);setTimeout(function(){style.opacity=0.8;},50);setTimeout(function(){style.opacity=0.7;},75);setTimeout(function(){style.opacity=0.6;},100);setTimeout(function(){style.opacity=0.5;},125);setTimeout(function(){style.opacity=0.4;},150);setTimeout(function(){style.opacity=0.3;},175);setTimeout(function(){style.opacity=0.2;},200);setTimeout(function(){style.opacity=0.1;},225);setTimeout(function(){style.opacity=0;},250);setTimeout(function(){style.display='none';},275);}};RGraph.draw3DAxes=RGraph.Draw3DAxes=function(obj)
{var prop=obj.properties;var marginLeft=obj.marginLeft,marginRight=obj.marginRight,marginTop=obj.marginTop,marginBottom=obj.marginBottom,xaxispos=prop.xaxisPosition,graphArea=obj.canvas.height-marginTop-marginBottom,halfGraphArea=graphArea/2,offsetx=prop.variantThreedOffsetx,offsety=prop.variantThreedOffsety,xaxis=prop.variantThreedXaxis,yaxis=prop.variantThreedYaxis
if(yaxis){RGraph.draw3DYAxis(obj);}
if(xaxis){if(xaxispos==='center'){RGraph.path(obj.context,'b m % % l % % l % % l % % c s #aaa f #ddd',marginLeft,marginTop+halfGraphArea,marginLeft+offsetx,marginTop+halfGraphArea-offsety,obj.canvas.width-marginRight+offsetx,marginTop+halfGraphArea-offsety,obj.canvas.width-marginRight,marginTop+halfGraphArea);}else{if(obj.type==='hbar'){var xaxisYCoord=obj.canvas.height-obj.properties.marginBottom;}else{var xaxisYCoord=obj.getYCoord(0);}
RGraph.path(obj.context,'m % % l % % l % % l % % c s #aaa f #ddd',marginLeft,xaxisYCoord,marginLeft+offsetx,xaxisYCoord-offsety,obj.canvas.width-marginRight+offsetx,xaxisYCoord-offsety,obj.canvas.width-marginRight,xaxisYCoord);}}};RGraph.draw3DYAxis=function(obj)
{var prop=obj.properties;var marginLeft=obj.marginLeft,marginRight=obj.marginRight,marginTop=obj.marginTop,marginBottom=obj.marginBottom,xaxispos=prop.xaxisPosition,graphArea=obj.canvas.height-marginTop-marginBottom,halfGraphArea=graphArea/2,offsetx=prop.variantThreedOffsetx,offsety=prop.variantThreedOffsety;if((obj.type==='hbar'||obj.type==='bar')&&prop.yaxisPosition==='center'){var x=((obj.canvas.width-marginLeft-marginRight)/2)+marginLeft;}else if((obj.type==='hbar'||obj.type==='bar')&&prop.yaxisPosition==='right'){var x=obj.canvas.width-marginRight;}else{var x=marginLeft;}
RGraph.path(obj.context,'b m % % l % % l % % l % % s #aaa f #ddd',x,marginTop,x+offsetx,marginTop-offsety,x+offsetx,obj.canvas.height-marginBottom-offsety,x,obj.canvas.height-marginBottom);};RGraph.strokedCurvyRect=function(context,x,y,w,h)
{var r=arguments[5]?arguments[5]:3;var corner_tl=(arguments[6]||arguments[6]==null)?true:false;var corner_tr=(arguments[7]||arguments[7]==null)?true:false;var corner_br=(arguments[8]||arguments[8]==null)?true:false;var corner_bl=(arguments[9]||arguments[9]==null)?true:false;context.beginPath();context.moveTo(x+(corner_tl?r:0),y);context.lineTo(x+w-(corner_tr?r:0),y);if(corner_tr){context.arc(x+w-r,y+r,r,RGraph.PI+RGraph.HALFPI,RGraph.TWOPI,false);}
context.lineTo(x+w,y+h-(corner_br?r:0));if(corner_br){context.arc(x+w-r,y-r+h,r,RGraph.TWOPI,RGraph.HALFPI,false);}
context.lineTo(x+(corner_bl?r:0),y+h);if(corner_bl){context.arc(x+r,y-r+h,r,RGraph.HALFPI,RGraph.PI,false);}
context.lineTo(x,y+(corner_tl?r:0));if(corner_tl){context.arc(x+r,y+r,r,RGraph.PI,RGraph.PI+RGraph.HALFPI,false);}
context.stroke();};RGraph.filledCurvyRect=function(context,x,y,w,h)
{var r=arguments[5]?arguments[5]:3;var corner_tl=(arguments[6]||arguments[6]==null)?true:false;var corner_tr=(arguments[7]||arguments[7]==null)?true:false;var corner_br=(arguments[8]||arguments[8]==null)?true:false;var corner_bl=(arguments[9]||arguments[9]==null)?true:false;context.beginPath();if(corner_tl){context.moveTo(x+r,y+r);context.arc(x+r,y+r,r,RGraph.PI,RGraph.PI+RGraph.HALFPI,false);}else{context.fillRect(x,y,r,r);}
if(corner_tr){context.moveTo(x+w-r,y+r);context.arc(x+w-r,y+r,r,RGraph.PI+RGraph.HALFPI,0,false);}else{context.moveTo(x+w-r,y);context.fillRect(x+w-r,y,r,r);}
if(corner_br){context.moveTo(x+w-r,y+h-r);context.arc(x+w-r,y-r+h,r,0,RGraph.HALFPI,false);}else{context.moveTo(x+w-r,y+h-r);context.fillRect(x+w-r,y+h-r,r,r);}
if(corner_bl){context.moveTo(x+r,y+h-r);context.arc(x+r,y-r+h,r,RGraph.HALFPI,RGraph.PI,false);}else{context.moveTo(x,y+h-r);context.fillRect(x,y+h-r,r,r);}
context.fillRect(x+r,y,w-r-r,h);context.fillRect(x,y+r,r+1,h-r-r);context.fillRect(x+w-r-1,y+r,r+1,h-r-r);context.fill();};RGraph.hideZoomedCanvas=RGraph.HideZoomedCanvas=function()
{var interval=10;var frames=15;if(typeof RGraph.zoom_image==='object'){var obj=RGraph.zoom_image.obj;var prop=obj.properties;}else{return;}
if(prop.zoomFadeOut){for(var i=frames,j=1;i>=0;--i,++j){if(typeof RGraph.zoom_image==='object'){setTimeout("RGraph.zoom_image.style.opacity = "+String(i/10),j*interval);}}
if(typeof RGraph.zoom_background==='object'){setTimeout("RGraph.zoom_background.style.opacity = "+String(i/frames),j*interval);}}
if(typeof RGraph.zoom_image==='object'){setTimeout("RGraph.zoom_image.style.display = 'none'",prop.zoomFadeOut?(frames*interval)+10:0);}
if(typeof RGraph.zoom_background==='object'){setTimeout("RGraph.zoom_background.style.display = 'none'",prop.zoomFadeOut?(frames*interval)+10:0);}};RGraph.addCustomEventListener=RGraph.AddCustomEventListener=function(obj,name,func)
{if(typeof RGraph.events[obj.uid]==='undefined'){RGraph.events[obj.uid]=[];}
if(name.substr(0,2)!=='on'){name='on'+name;}
RGraph.events[obj.uid].push([obj,name,func]);return RGraph.events[obj.uid].length-1;};RGraph.fireCustomEvent=RGraph.FireCustomEvent=function(obj,name)
{if(obj&&obj.isRGraph){if(name.match(/(on)?mouseout/)&&typeof obj.properties.eventsMouseout==='function'){(obj.properties.eventsMouseout)(obj);}
if(obj[name]){(obj[name])(obj);}
var uid=obj.uid;if(typeof uid==='string'&&typeof RGraph.events==='object'&&typeof RGraph.events[uid]==='object'&&RGraph.events[uid].length>0){for(var j=0;j<RGraph.events[uid].length;++j){if(RGraph.events[uid][j]&&RGraph.events[uid][j][1]===name){RGraph.events[uid][j][2](obj);}}}}};RGraph.removeAllCustomEventListeners=RGraph.RemoveAllCustomEventListeners=function()
{var id=arguments[0];if(id&&RGraph.events[id]){RGraph.events[id]=[];}else{RGraph.events=[];}};RGraph.removeCustomEventListener=RGraph.RemoveCustomEventListener=function(obj,i)
{if(typeof RGraph.events==='object'&&typeof RGraph.events[obj.id]==='object'&&typeof RGraph.events[obj.id][i]==='object'){RGraph.events[obj.id][i]=null;}};RGraph.drawBackgroundImage=RGraph.DrawBackgroundImage=function(obj)
{var prop=obj.properties;if(typeof prop.backgroundImage==='string'){if(typeof obj.canvas.__rgraph_background_image__==='undefined'){var img=new Image();img.__object__=obj;img.__canvas__=obj.canvas;img.__context__=obj.context;img.src=obj.get('backgroundImage');obj.canvas.__rgraph_background_image__=img;}else{img=obj.canvas.__rgraph_background_image__;}
img.onload=function()
{obj.__rgraph_background_image_loaded__=true;RGraph.clear(obj.canvas);RGraph.redrawCanvas(obj.canvas);}
var marginLeft=obj.marginLeft;var marginRight=obj.marginRight;var marginTop=obj.marginTop;var marginBottom=obj.marginBottom;var stretch=prop.backgroundImageStretch;var align=prop.backgroundImageAlign;if(typeof align==='string'){if(align.indexOf('right')!=-1){var x=obj.canvas.width-(prop.backgroundImageW||img.width)-marginRight;}else{var x=marginLeft;}
if(align.indexOf('bottom')!=-1){var y=obj.canvas.height-(prop.backgroundImageH||img.height)-marginBottom;}else{var y=marginTop;}}else{var x=marginLeft||25;var y=marginTop||25;}
var x=typeof prop.backgroundImageX==='number'?prop.backgroundImageX:x;var y=typeof prop.backgroundImageY==='number'?prop.backgroundImageY:y;var w=stretch?obj.canvas.width-marginLeft-marginRight:img.width;var h=stretch?obj.canvas.height-marginTop-marginBottom:img.height;if(typeof prop.backgroundImageW==='number')w=prop.backgroundImageW;if(typeof prop.backgroundImageH==='number')h=prop.backgroundImageH;var oldAlpha=obj.context.globalAlpha;obj.context.globalAlpha=prop.backgroundImageAlpha;obj.context.drawImage(img,x,y,w,h);obj.context.globalAlpha=oldAlpha;}};RGraph.hasTooltips=function(obj)
{var prop=obj.properties;if(typeof prop.tooltips=='object'&&prop.tooltips){for(var i=0,len=prop.tooltips.length;i<len;++i){if(!RGraph.is_null(obj.get('tooltips')[i])){return true;}}}else if(typeof prop.tooltips==='function'){return true;}
return false;};RGraph.createUID=RGraph.CreateUID=function()
{return'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c)
{var r=Math.random()*16|0,v=c=='x'?r:(r&0x3|0x8);return v.toString(16);});};RGraph.OR.add=RGraph.OR.Add=function(obj)
{var uid=obj.uid;var id=obj.canvas.id;RGraph.ObjectRegistry.objects.byUID[RGraph.ObjectRegistry.objects.byUID.length]=[uid,obj];RGraph.ObjectRegistry.objects.byCanvasID.push([id,obj]);};RGraph.OR.remove=RGraph.OR.Remove=function(obj)
{var id=obj.id;var uid=obj.uid;for(var i=0;i<RGraph.ObjectRegistry.objects.byUID.length;++i){if(RGraph.ObjectRegistry.objects.byUID[i]&&RGraph.ObjectRegistry.objects.byUID[i][1].uid==uid){RGraph.ObjectRegistry.objects.byUID[i]=null;}}
for(var i=0;i<RGraph.ObjectRegistry.objects.byCanvasID.length;++i){if(RGraph.ObjectRegistry.objects.byCanvasID[i]&&RGraph.ObjectRegistry.objects.byCanvasID[i][1]&&RGraph.ObjectRegistry.objects.byCanvasID[i][1].uid==uid){RGraph.ObjectRegistry.objects.byCanvasID[i]=null;}}};RGraph.OR.clear=RGraph.OR.Clear=function()
{if(arguments[0]){var id=(typeof arguments[0]==='object'?arguments[0].id:arguments[0]);var objects=RGraph.ObjectRegistry.getObjectsByCanvasID(id);for(var i=0,len=objects.length;i<len;++i){RGraph.ObjectRegistry.remove(objects[i]);}}else{RGraph.ObjectRegistry.objects={};RGraph.ObjectRegistry.objects.byUID=[];RGraph.ObjectRegistry.objects.byCanvasID=[];}};RGraph.OR.list=RGraph.OR.List=function()
{var list=[];for(var i=0,len=RGraph.ObjectRegistry.objects.byUID.length;i<len;++i){if(RGraph.ObjectRegistry.objects.byUID[i]){list.push(RGraph.ObjectRegistry.objects.byUID[i][1].type);}}
if(arguments[0]){return list;}else{$p(list);}};RGraph.OR.clearByType=RGraph.OR.ClearByType=function(type)
{var objects=RGraph.ObjectRegistry.objects.byUID;for(var i=0,len=objects.length;i<len;++i){if(objects[i]){var uid=objects[i][0];var obj=objects[i][1];if(obj&&obj.type==type){RGraph.ObjectRegistry.remove(obj);}}}};RGraph.OR.iterate=RGraph.OR.Iterate=function(func)
{var objects=RGraph.ObjectRegistry.objects.byUID;for(var i=0,len=objects.length;i<len;++i){if(typeof arguments[1]==='string'){var types=arguments[1].split(/,/);for(var j=0,len2=types.length;j<len2;++j){if(types[j]==objects[i][1].type){func(objects[i][1]);}}}else{func(objects[i][1]);}}};RGraph.OR.getObjectsByCanvasID=function(id)
{var store=RGraph.ObjectRegistry.objects.byCanvasID;var ret=[];for(var i=0,len=store.length;i<len;++i){if(store[i]&&store[i][0]==id){ret.push(store[i][1]);}}
return ret;};RGraph.OR.firstbyxy=RGraph.OR.getFirstObjectByXY=RGraph.OR.getObjectByXY=function(e)
{var canvas=e.target;var ret=null;var objects=RGraph.ObjectRegistry.getObjectsByCanvasID(canvas.id);for(var i=(objects.length-1);i>=0;--i){var obj=objects[i].getObjectByXY(e);if(obj){return obj;}}};RGraph.OR.getObjectsByXY=function(e)
{var canvas=e.target,ret=[],objects=RGraph.ObjectRegistry.getObjectsByCanvasID(canvas.id);for(var i=(objects.length-1);i>=0;--i){var obj=objects[i].getObjectByXY(e);if(obj){ret.push(obj);}}
return ret;};RGraph.OR.get=RGraph.OR.getObjectByUID=function(uid)
{var objects=RGraph.ObjectRegistry.objects.byUID;for(var i=0,len=objects.length;i<len;++i){if(objects[i]&&objects[i][1].uid==uid){return objects[i][1];}}};RGraph.OR.bringToFront=function(obj)
{var redraw=typeof arguments[1]==='undefined'?true:arguments[1];RGraph.ObjectRegistry.remove(obj);RGraph.ObjectRegistry.add(obj);if(redraw){RGraph.redrawCanvas(obj.canvas);}};RGraph.OR.type=RGraph.OR.getObjectsByType=function(type)
{var objects=RGraph.ObjectRegistry.objects.byUID;var ret=[];for(i in objects){if(objects[i]&&objects[i][1]&&objects[i][1].type&&objects[i][1].type&&objects[i][1].type==type){ret.push(objects[i][1]);}}
return ret;};RGraph.OR.first=RGraph.OR.getFirstObjectByType=function(type)
{var objects=RGraph.ObjectRegistry.objects.byUID;for(var i in objects){if(objects[i]&&objects[i][1]&&objects[i][1].type==type){return objects[i][1];}}
return null;};RGraph.getAngleByXY=function(cx,cy,x,y)
{var angle=Math.atan((y-cy)/(x-cx));angle=Math.abs(angle)
if(x>=cx&&y>=cy){angle+=RGraph.TWOPI;}else if(x>=cx&&y<cy){angle=(RGraph.HALFPI-angle)+(RGraph.PI+RGraph.HALFPI);}else if(x<cx&&y<cy){angle+=RGraph.PI;}else{angle=RGraph.PI-angle;}
if(angle>RGraph.TWOPI){angle-=RGraph.TWOPI;}
return angle;};RGraph.getHypLength=function(x1,y1,x2,y2)
{var ret=Math.sqrt(((x2-x1)*(x2-x1))+((y2-y1)*(y2-y1)));return ret;};RGraph.getRadiusEndPoint=function(cx,cy,angle,radius)
{var x=cx+(Math.cos(angle)*radius);var y=cy+(Math.sin(angle)*radius);return[x,y];};RGraph.installEventListeners=RGraph.InstallEventListeners=function(obj)
{var prop=obj.properties;if(RGraph.ISOLD){return;}
if(RGraph.installCanvasClickListener){RGraph.installWindowMousedownListener(obj);RGraph.installWindowMouseupListener(obj);RGraph.installCanvasMousemoveListener(obj);RGraph.installCanvasMouseupListener(obj);RGraph.installCanvasMousedownListener(obj);RGraph.installCanvasClickListener(obj);}else if(RGraph.hasTooltips(obj)||prop.adjustable||prop.annotatable||prop.contextmenu||prop.resizable||prop.keyInteractive||prop.eventsClick||prop.eventsMousemove||typeof obj.onclick==='function'||typeof obj.onmousemove==='function'){alert('[RGRAPH] You appear to have used dynamic features but not included the file: RGraph.common.dynamic.js');}};RGraph.pr=function(obj)
{var indent=(arguments[2]?arguments[2]:'    ');var str='';var counter=typeof arguments[3]=='number'?arguments[3]:0;if(counter>=5){return'';}
switch(typeof obj){case'string':str+=obj+' ('+(typeof obj)+', '+obj.length+')';break;case'number':str+=obj+' ('+(typeof obj)+')';break;case'boolean':str+=obj+' ('+(typeof obj)+')';break;case'function':str+='function () {}';break;case'undefined':str+='undefined';break;case'null':str+='null';break;case'object':if(RGraph.isNull(obj)){str+=indent+'null\n';}else{str+=indent+'Object {'+'\n'
for(var j in obj){str+=indent+'    '+j+' => '+RGraph.pr(obj[j],true,indent+'    ',counter+1)+'\n';}
str+=indent+'}';}
break;default:str+='Unknown type: '+typeof obj+'';break;}
if(!arguments[1]){alert(str);}
return str;};RGraph.dashedLine=RGraph.DashedLine=function(context,x1,y1,x2,y2)
{var size=5;if(typeof arguments[5]==='number'){size=arguments[5];}
var dx=x2-x1;var dy=y2-y1;var num=Math.floor(Math.sqrt((dx*dx)+(dy*dy))/size);var xLen=dx/num;var yLen=dy/num;var count=0;do{(count%2==0&&count>0)?context.lineTo(x1,y1):context.moveTo(x1,y1);x1+=xLen;y1+=yLen;}while(count++<=num);};RGraph.AJAX=function(url,callback)
{if(window.XMLHttpRequest){var httpRequest=new XMLHttpRequest();}else if(window.ActiveXObject){var httpRequest=new ActiveXObject("Microsoft.XMLHTTP");}
httpRequest.onreadystatechange=function()
{if(this.readyState==4&&this.status==200){this.__user_callback__=callback;this.__user_callback__(this.responseText);}}
httpRequest.open('GET',url,true);httpRequest.send();};RGraph.AJAX.post=RGraph.AJAX.POST=function(url,data,callback)
{var crumbs=[];if(window.XMLHttpRequest){var httpRequest=new XMLHttpRequest();}else if(window.ActiveXObject){var httpRequest=new ActiveXObject("Microsoft.XMLHTTP");}
httpRequest.onreadystatechange=function()
{if(this.readyState==4&&this.status==200){this.__user_callback__=callback;this.__user_callback__(this.responseText);}}
httpRequest.open('POST',url,true);httpRequest.setRequestHeader("Content-type","application/x-www-form-urlencoded");for(i in data){if(typeof i=='string'){crumbs.push(i+'='+encodeURIComponent(data[i]));}}
httpRequest.send(crumbs.join('&'));};RGraph.AJAX.getNumber=function(url,callback)
{RGraph.AJAX(url,function()
{var num=parseFloat(this.responseText);callback(num);});};RGraph.AJAX.getString=function(url,callback)
{RGraph.AJAX(url,function()
{var str=String(this.responseText);callback(str);});};RGraph.AJAX.getJSON=function(url,callback)
{RGraph.AJAX(url,function()
{var json=eval('('+this.responseText+')');callback(json);});};RGraph.AJAX.getCSV=function(url,callback)
{var seperator=arguments[2]?arguments[2]:',';RGraph.AJAX(url,function()
{var regexp=new RegExp(seperator);var arr=this.responseText.split(regexp);for(var i=0,len=arr.length;i<len;++i){arr[i]=parseFloat(arr[i]);}
callback(arr);});};RGraph.rotateCanvas=RGraph.RotateCanvas=function(canvas,x,y,angle)
{var context=canvas.getContext('2d');context.translate(x,y);context.rotate(angle);context.translate(0-x,0-y);};RGraph.measureText=RGraph.MeasureText=function(opt)
{if(typeof opt==='object'){var text=opt.text,bold=opt.bold,font=opt.font,size=opt.size;}else{text=arguments[0];bold=arguments[1];font=arguments[2];size=arguments[3];}
if(typeof RGraph.measuretext_cache==='undefined'){RGraph.measuretext_cache=[];}
var str=text+':'+bold+':'+font+':'+size;if(typeof RGraph.measuretext_cache=='object'&&RGraph.measuretext_cache[str]){return RGraph.measuretext_cache[str];}
if(!RGraph.measuretext_cache['text-div']){var div=document.createElement('DIV');div.style.position='absolute';div.style.top='-100px';div.style.left='-100px';document.body.appendChild(div);RGraph.measuretext_cache['text-div']=div;}else if(RGraph.measuretext_cache['text-div']){var div=RGraph.measuretext_cache['text-div'];}
div.innerHTML=text.replace(/\r?\n/g,'<br />');div.style.fontFamily=font;div.style.fontWeight=bold?'bold':'normal';div.style.fontSize=(size||12)+'pt';var size=[div.offsetWidth,div.offsetHeight];RGraph.measuretext_cache[str]=size;return size;};RGraph.text=RGraph.text2=RGraph.Text2=function(opt)
{if(arguments[0]&&arguments[1]&&typeof arguments[1].text==='string'){var obj=arguments[0],opt=arguments[1];}else{var obj=opt.object;}
for(var i in RGraph.text.defaults){if(typeof i==='string'&&typeof opt[i]==='undefined'){opt[i]=RGraph.text.defaults[i];}}
function domtext()
{if(String(opt.size).toLowerCase().indexOf('italic')!==-1){opt.size=opt.size.replace(/ *italic +/,'');opt.italic=true;}
var cacheKey=Math.abs(parseInt(opt.x))+'_'+Math.abs(parseInt(opt.y))+'_'+String(opt.text).replace(/[^a-zA-Z0-9]+/g,'_')+'_'+obj.canvas.id;if(!obj.canvas.rgraph_domtext_wrapper){var wrapper=document.createElement('div');wrapper.id=obj.canvas.id+'_rgraph_domtext_wrapper';wrapper.className='rgraph_domtext_wrapper';wrapper.style.overflow=obj.properties.textAccessibleOverflow!=false&&obj.properties.textAccessibleOverflow!='hidden'?'visible':'hidden';wrapper.style.width=obj.canvas.offsetWidth+'px';wrapper.style.height=obj.canvas.offsetHeight+'px';wrapper.style.cssFloat=obj.canvas.style.cssFloat;wrapper.style.display=obj.canvas.style.display||'inline-block';wrapper.style.position=obj.canvas.style.position||'relative';wrapper.style.left=obj.canvas.style.left;wrapper.style.top=obj.canvas.style.top;wrapper.style.width=obj.canvas.width+'px';wrapper.style.height=obj.canvas.height+'px';wrapper.style.lineHeight='initial';obj.canvas.style.position='absolute';obj.canvas.style.left=0;obj.canvas.style.top=0;obj.canvas.style.display='inline';obj.canvas.style.cssFloat='none';if((obj.type==='bar'||obj.type==='bipolar'||obj.type==='hbar')&&obj.properties.variant==='3d'){wrapper.style.transform='skewY(5.7deg)';}
obj.canvas.parentNode.insertBefore(wrapper,obj.canvas);obj.canvas.parentNode.removeChild(obj.canvas);wrapper.appendChild(obj.canvas);obj.canvas.rgraph_domtext_wrapper=wrapper;}else{wrapper=obj.canvas.rgraph_domtext_wrapper;}
var defaults={size:12,font:'Arial',italic:'normal',bold:'normal',valign:'bottom',halign:'left',marker:true,color:context.fillStyle,bounding:{enabled:false,fill:'rgba(255,255,255,0.7)',stroke:'#666',linewidth:1}}
opt.text=String(opt.text).replace(/\r?\n/g,'[[RETURN]]');if(typeof RGraph.text.domNodeCache==='undefined'){RGraph.text.domNodeCache=new Array();}
if(typeof RGraph.text.domNodeCache[obj.id]==='undefined'){RGraph.text.domNodeCache[obj.id]=new Array();}
if(typeof RGraph.text.domNodeDimensionCache==='undefined'){RGraph.text.domNodeDimensionCache=new Array();}
if(typeof RGraph.text.domNodeDimensionCache[obj.id]==='undefined'){RGraph.text.domNodeDimensionCache[obj.id]=new Array();}
if(!RGraph.text.domNodeCache[obj.id]||!RGraph.text.domNodeCache[obj.id][cacheKey]){var span=document.createElement('span');span.style.position='absolute';span.style.display='inline';span.className=' rgraph_accessible_text'
+' rgraph_accessible_text_'+obj.id
+' rgraph_accessible_text_'+(opt.tag||'').replace(/\./,'_')
+' rgraph_accessible_text_'+obj.type;span.style.left=(opt.x*(parseInt(obj.canvas.offsetWidth)/parseInt(obj.canvas.width)))+'px';span.style.top=(opt.y*(parseInt(obj.canvas.offsetHeight)/parseInt(obj.canvas.height)))+'px';span.style.color=opt.color||defaults.color;span.style.fontFamily=opt.font||defaults.font;span.style.fontWeight=opt.bold?'bold':defaults.bold;span.style.fontStyle=opt.italic?'italic':defaults.italic;span.style.fontSize=(opt.size||defaults.size)+'pt';span.style.whiteSpace='nowrap';span.tag=opt.tag;if(typeof opt.angle==='number'&&opt.angle!==0){var coords=RGraph.measureText(opt.text,opt.bold,opt.font,opt.size);span.style.transformOrigin='100% 50%';span.style.transform='rotate('+opt.angle+'deg)';}
span.style.textShadow='{1}px {2}px {3}px {4}'.format(context.shadowOffsetX,context.shadowOffsetY,context.shadowBlur,context.shadowColor);if(opt.bounding){span.style.border='1px solid '+(opt['bounding.stroke']||defaults.bounding.stroke);span.style.backgroundColor=opt['bounding.fill']||defaults.bounding.fill;span.style.borderWidth=typeof opt['bounding.linewidth']==='number'?opt['bounding.linewidth']:defaults.bounding.linewidth;}
if((typeof obj.properties.textAccessiblePointerevents==='undefined'||obj.properties.textAccessiblePointerevents)&&obj.properties.textAccessiblePointerevents!=='none'){span.style.pointerEvents='auto';}else{span.style.pointerEvents='none';}
span.style.padding=opt.bounding?'2px':null;span.__text__=opt.text
span.innerHTML=opt.text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;');span.innerHTML=span.innerHTML.replace(/\[\[RETURN\]\]/g,'<br />');wrapper.appendChild(span);opt.halign=opt.halign||'left';opt.valign=opt.valign||'bottom';if(opt.halign==='right'){span.style.left=parseFloat(span.style.left)-span.offsetWidth+'px';span.style.textAlign='right';}else if(opt.halign==='center'){span.style.left=parseFloat(span.style.left)-(span.offsetWidth/2)+'px';span.style.textAlign='center';}
if(opt.valign==='top'){}else if(opt.valign==='center'){span.style.top=parseFloat(span.style.top)-(span.offsetHeight/2)+'px';}else{span.style.top=parseFloat(span.style.top)-span.offsetHeight+'px';}
var offsetWidth=parseFloat(span.offsetWidth),offsetHeight=parseFloat(span.offsetHeight),top=parseFloat(span.style.top),left=parseFloat(span.style.left);RGraph.text.domNodeCache[obj.id][cacheKey]=span;RGraph.text.domNodeDimensionCache[obj.id][cacheKey]={left:left,top:top,width:offsetWidth,height:offsetHeight};span.id=cacheKey;}else{span=RGraph.text.domNodeCache[obj.id][cacheKey];span.style.display='inline';var offsetWidth=RGraph.text.domNodeDimensionCache[obj.id][cacheKey].width,offsetHeight=RGraph.text.domNodeDimensionCache[obj.id][cacheKey].height,top=RGraph.text.domNodeDimensionCache[obj.id][cacheKey].top,left=RGraph.text.domNodeDimensionCache[obj.id][cacheKey].left;}
if(opt.marker){RGraph.path(context,'b m % % l % % m % % l % % s',opt.x-5,opt.y,opt.x+5,opt.y,opt.x,opt.y-5,opt.x,opt.y+5);}
if(obj.type==='drawing.text'){if(obj.properties.eventsMousemove){span.addEventListener('mousemove',function(e){(obj.properties.eventsMousemove)(e,obj);},false);}
if(obj.properties.eventsClick){span.addEventListener('click',function(e){(obj.properties.eventsClick)(e,obj);},false);}
if(obj.properties.tooltips){span.addEventListener(obj.properties.tooltipsEvent.indexOf('mousemove')!==-1?'mousemove':'click',function(e)
{if(!RGraph.Registry.get('tooltip')||RGraph.Registry.get('tooltip').__index__!==0||RGraph.Registry.get('tooltip').__object__.uid!=obj.uid){RGraph.hideTooltip();RGraph.redraw();RGraph.tooltip(obj,obj.properties.tooltips[0],opt.x,opt.y,0,e);}},false);}}
var ret={};ret.x=left;ret.y=top;ret.width=offsetWidth;ret.height=offsetHeight;ret.object=obj;ret.text=opt.text;ret.tag=opt.tag;RGraph.text.domNodeCache.reset=function()
{if(arguments[0]){if(typeof arguments[0]==='string'){var canvas=document.getElementById(arguments[0])}else{var canvas=arguments[0];}
var nodes=RGraph.text.domNodeCache[canvas.id];for(j in nodes){var node=RGraph.text.domNodeCache[canvas.id][j];if(node&&node.parentNode){node.parentNode.removeChild(node);}}
RGraph.text.domNodeCache[canvas.id]=[];RGraph.text.domNodeDimensionCache[canvas.id]=[];}else{for(i in RGraph.text.domNodeCache){for(j in RGraph.text.domNodeCache[i]){if(RGraph.text.domNodeCache[i][j]&&RGraph.text.domNodeCache[i][j].parentNode){RGraph.text.domNodeCache[i][j].parentNode.removeChild(RGraph.text.domNodeCache[i][j]);}}}
RGraph.text.domNodeCache=[];RGraph.text.domNodeDimensionCache=[];}};RGraph.text.find=function(opt)
{var span,nodes=[];if(opt.object&&opt.object.isRGraph){var id=opt.object.id;}else if(opt.id){var id=typeof opt.id==='string'?opt.id:opt.object.id;opt.object=document.getElementById(id).__object__;}else{alert('[RGRAPH] You Must give either an object or an ID to the RGraph.text.find() function');return false;}
for(i in RGraph.text.domNodeCache[id]){span=RGraph.text.domNodeCache[id][i];if(typeof opt.tag==='string'&&opt.tag===span.tag){nodes.push(span);continue;}
if(typeof opt.tag==='object'&&opt.tag.constructor.toString().indexOf('RegExp')){var regexp=new RegExp(opt.tag);if(regexp.test(span.tag)){nodes.push(span);continue;}}
if(typeof opt.text==='string'&&opt.text===span.__text__){nodes.push(span);continue;}
if(typeof opt.text==='object'&&opt.text.constructor.toString().indexOf('RegExp')){var regexp=new RegExp(opt.text);if(regexp.test(span.__text__)){nodes.push(span);continue;}}}
if(typeof opt.callback==='function'){(opt.callback)({nodes:nodes,object:opt.object});}
return nodes;};ret.node=span;if(obj&&obj.isRGraph&&obj.coordsText){obj.coordsText.push(ret);}
return ret;}
if(obj&&obj.isRGraph){var obj=obj;var canvas=obj.canvas;var context=obj.context;}else if(typeof obj=='string'){var canvas=document.getElementById(obj);var context=canvas.getContext('2d');var obj=canvas.__object__;}else if(typeof obj.getContext==='function'){var canvas=obj;var context=canvas.getContext('2d');var obj=canvas.__object__;}else if(obj.toString().indexOf('CanvasRenderingContext2D')!=-1||RGraph.ISIE8&&obj.moveTo){var context=obj;var canvas=obj.canvas;var obj=canvas.__object__;}else if(RGraph.ISOLD&&obj.fillText){var context=obj;var canvas=obj.canvas;var obj=canvas.__object__;}
if(typeof opt.boundingFill==='string')opt['bounding.fill']=opt.boundingFill;if(typeof opt.boundingStroke==='string')opt['bounding.stroke']=opt.boundingStroke;if(typeof opt.boundingLinewidth==='number')opt['bounding.linewidth']=opt.boundingLinewidth;if(typeof opt.accessible==='undefined'){if(obj&&obj.properties.textAccessible){return domtext();}}else if(typeof opt.accessible==='boolean'&&opt.accessible){return domtext();}
var x=opt.x,y=opt.y,originalX=x,originalY=y,text=opt.text,text_multiline=typeof text==='string'?text.split(/\r?\n/g):'',numlines=text_multiline.length,font=opt.font?opt.font:'Arial',size=opt.size?opt.size:10,size_pixels=size*1.5,bold=opt.bold,italic=opt.italic,halign=opt.halign?opt.halign:'left',valign=opt.valign?opt.valign:'bottom',tag=typeof opt.tag=='string'&&opt.tag.length>0?opt.tag:'',marker=opt.marker,angle=opt.angle||0;var bounding=opt.bounding,bounding_stroke=opt['bounding.stroke']?opt['bounding.stroke']:'black',bounding_fill=opt['bounding.fill']?opt['bounding.fill']:'rgba(255,255,255,0.7)',bounding_shadow=opt['bounding.shadow'],bounding_shadow_color=opt['bounding.shadow.color']||'#ccc',bounding_shadow_blur=opt['bounding.shadow.blur']||3,bounding_shadow_offsetx=opt['bounding.shadow.offsetx']||3,bounding_shadow_offsety=opt['bounding.shadow.offsety']||3,bounding_linewidth=typeof opt['bounding.linewidth']==='number'?opt['bounding.linewidth']:1;var ret={};if(typeof opt.color==='string'){var orig_fillstyle=context.fillStyle;context.fillStyle=opt.color;}
if(typeof text=='number'){text=String(text);}
if(typeof text!=='string'){return;}
if(angle!=0){context.save();context.translate(x,y);context.rotate((Math.PI/180)*angle)
x=0;y=0;}
context.font=(opt.italic?'italic ':'')+(opt.bold?'bold ':'')+size+'pt '+font;var width=0;for(var i=0;i<numlines;++i){width=Math.max(width,context.measureText(text_multiline[i]).width);}
var height=size_pixels*numlines;if(opt.marker){var marker_size=10;var strokestyle=context.strokeStyle;context.beginPath();context.strokeStyle='red';context.moveTo(x,y-marker_size);context.lineTo(x,y+marker_size);context.moveTo(x-marker_size,y);context.lineTo(x+marker_size,y);context.stroke();context.strokeStyle=strokestyle;}
if(halign=='center'){context.textAlign='center';var boundingX=x-2-(width/2);}else if(halign=='right'){context.textAlign='right';var boundingX=x-2-width;}else{context.textAlign='left';var boundingX=x-2;}
if(valign=='center'){context.textBaseline='middle';y-=1;y-=((numlines-1)/2)*size_pixels;var boundingY=y-(size_pixels/2)-2;}else if(valign=='top'){context.textBaseline='top';var boundingY=y-2;}else{context.textBaseline='bottom';if(numlines>1){y-=((numlines-1)*size_pixels);}
var boundingY=y-size_pixels-2;}
var boundingW=width+4;var boundingH=height+4;if(bounding){var pre_bounding_linewidth=context.lineWidth,pre_bounding_strokestyle=context.strokeStyle,pre_bounding_fillstyle=context.fillStyle,pre_bounding_shadowcolor=context.shadowColor,pre_bounding_shadowblur=context.shadowBlur,pre_bounding_shadowoffsetx=context.shadowOffsetX,pre_bounding_shadowoffsety=context.shadowOffsetY;context.lineWidth=bounding_linewidth?bounding_linewidth:0.001;context.strokeStyle=bounding_stroke;context.fillStyle=bounding_fill;if(bounding_shadow){context.shadowColor=bounding_shadow_color;context.shadowBlur=bounding_shadow_blur;context.shadowOffsetX=bounding_shadow_offsetx;context.shadowOffsetY=bounding_shadow_offsety;}
context.fillRect(boundingX,boundingY,boundingW,boundingH);context.strokeRect(boundingX,boundingY,boundingW,boundingH);context.lineWidth=pre_bounding_linewidth;context.strokeStyle=pre_bounding_strokestyle;context.fillStyle=pre_bounding_fillstyle;context.shadowColor=pre_bounding_shadowcolor
context.shadowBlur=pre_bounding_shadowblur
context.shadowOffsetX=pre_bounding_shadowoffsetx
context.shadowOffsetY=pre_bounding_shadowoffsety}
if(numlines>1){for(var i=0;i<numlines;++i){context.fillText(text_multiline[i],x,y+(size_pixels*i));}}else{context.fillText(text,x+0.5,y+0.5);}
if(angle!=0){if(angle==90){if(halign=='left'){if(valign=='bottom'){boundingX=originalX-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-height-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}}else if(halign=='center'){if(valign=='bottom'){boundingX=originalX-2;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-2;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-height-2;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}}else if(halign=='right'){if(valign=='bottom'){boundingX=originalX-2;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-2;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-height-2;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}}}else if(angle==180){if(halign=='left'){if(valign=='bottom'){boundingX=originalX-width-2;boundingY=originalY-2;boundingW=width+4;boundingH=height+4;}
if(valign=='center'){boundingX=originalX-width-2;boundingY=originalY-(height/2)-2;boundingW=width+4;boundingH=height+4;}
if(valign=='top'){boundingX=originalX-width-2;boundingY=originalY-height-2;boundingW=width+4;boundingH=height+4;}}else if(halign=='center'){if(valign=='bottom'){boundingX=originalX-(width/2)-2;boundingY=originalY-2;boundingW=width+4;boundingH=height+4;}
if(valign=='center'){boundingX=originalX-(width/2)-2;boundingY=originalY-(height/2)-2;boundingW=width+4;boundingH=height+4;}
if(valign=='top'){boundingX=originalX-(width/2)-2;boundingY=originalY-height-2;boundingW=width+4;boundingH=height+4;}}else if(halign=='right'){if(valign=='bottom'){boundingX=originalX-2;boundingY=originalY-2;boundingW=width+4;boundingH=height+4;}
if(valign=='center'){boundingX=originalX-2;boundingY=originalY-(height/2)-2;boundingW=width+4;boundingH=height+4;}
if(valign=='top'){boundingX=originalX-2;boundingY=originalY-height-2;boundingW=width+4;boundingH=height+4;}}}else if(angle==270){if(halign=='left'){if(valign=='bottom'){boundingX=originalX-height-2;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-4;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-2;boundingY=originalY-width-2;boundingW=height+4;boundingH=width+4;}}else if(halign=='center'){if(valign=='bottom'){boundingX=originalX-height-2;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-4;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-2;boundingY=originalY-(width/2)-2;boundingW=height+4;boundingH=width+4;}}else if(halign=='right'){if(valign=='bottom'){boundingX=originalX-height-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}
if(valign=='center'){boundingX=originalX-(height/2)-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}
if(valign=='top'){boundingX=originalX-2;boundingY=originalY-2;boundingW=height+4;boundingH=width+4;}}}
context.restore();}
context.textBaseline='alphabetic';context.textAlign='left';ret.x=boundingX;ret.y=boundingY;ret.width=boundingW;ret.height=boundingH
ret.object=obj;ret.text=text;ret.tag=tag;if(obj&&obj.isRGraph&&obj.coordsText){obj.coordsText.push(ret);}
if(typeof orig_fillstyle==='string'){context.fillStyle=orig_fillstyle;}
return ret;};RGraph.text.defaults={};RGraph.sequentialIndexToGrouped=function(index,data)
{var group=0;var grouped_index=0;while(--index>=0){if(RGraph.is_null(data[group])){group++;grouped_index=0;continue;}
if(typeof data[group]=='number'){group++
grouped_index=0;continue;}
grouped_index++;if(grouped_index>=data[group].length){group++;grouped_index=0;}}
return[group,grouped_index];};RGraph.Highlight.rect=RGraph.Highlight.Rect=function(obj,shape)
{var prop=obj.properties;if(prop.tooltipsHighlight){obj.context.lineWidth=1;obj.context.beginPath();obj.context.strokeStyle=prop.highlightStroke;obj.context.fillStyle=prop.highlightFill;obj.context.rect(shape['x'],shape['y'],shape['width'],shape['height']);obj.context.stroke();obj.context.fill();}};RGraph.Highlight.point=RGraph.Highlight.Point=function(obj,shape)
{var prop=obj.properties;if(prop.tooltipsHighlight){obj.context.beginPath();obj.context.strokeStyle=prop.highlightStroke;obj.context.fillStyle=prop.highlightFill;var radius=prop.highlightPointRadius||2;obj.context.arc(shape['x'],shape['y'],radius,0,RGraph.TWOPI,0);obj.context.stroke();obj.context.fill();}};RGraph.parseDate=function(str)
{if(str.match(/^\d\d\d\d-\d\d-\d\d(t|T)\d\d:\d\d(:\d\d)?$/)){str=str.toUpperCase().replace(/T/,' ');}
var d=new Date();var defaults={seconds:'00',minutes:'00',hours:'00',date:d.getDate(),month:d.getMonth()+1,year:d.getFullYear()};var months=['january','february','march','april','may','june','july','august','september','october','november','december'],months_regex=months.join('|');for(var i=0;i<months.length;++i){months[months[i]]=i;months[months[i].substring(0,3)]=i;months_regex=months_regex+'|'+months[i].substring(0,3);}
var sep='[-./_=+~#:;,]+';var tokens=str.split(/ +/);for(var i=0,len=tokens.length;i<len;++i){if(tokens[i]){if(tokens[i].match(/^\d\d\d\d$/)){defaults.year=tokens[i];}
var res=isMonth(tokens[i]);if(typeof res==='number'){defaults.month=res+1;}
if(tokens[i].match(/^\d?\d(?:st|nd|rd|th)?$/)){defaults.date=parseInt(tokens[i]);}
if(tokens[i].match(/^(\d\d):(\d\d):?(?:(\d\d))?$/)){defaults.hours=parseInt(RegExp.$1);defaults.minutes=parseInt(RegExp.$2);if(RegExp.$3){defaults.seconds=parseInt(RegExp.$3);}}
if(tokens[i].match(new RegExp('^(\\d\\d\\d\\d)'+sep+'(\\d\\d)'+sep+'(\\d\\d)$','i'))){defaults.date=parseInt(RegExp.$3);defaults.month=parseInt(RegExp.$2);defaults.year=parseInt(RegExp.$1);}
if(tokens[i].match(new RegExp('^(\\d\\d)'+sep+'(\\d\\d)'+sep+'(\\d\\d\\d\\d)$','i'))){defaults.date=parseInt(RegExp.$1);defaults.month=parseInt(RegExp.$2);defaults.year=parseInt(RegExp.$3);}}}
str='{1}/{2}/{3} {4}:{5}:{6}'.format(defaults.year,String(defaults.month).length===1?'0'+(defaults.month):defaults.month,String(defaults.date).length===1?'0'+(defaults.date):defaults.date,String(defaults.hours).length===1?'0'+(defaults.hours):defaults.hours,String(defaults.minutes).length===1?'0'+(defaults.minutes):defaults.minutes,String(defaults.seconds).length===1?'0'+(defaults.seconds):defaults.seconds);return Date.parse(str);function isMonth(str)
{var res=str.toLowerCase().match(months_regex);return res?months[res[0]]:false;}};RGraph.parseDateOld=function(str)
{str=RGraph.trim(str);if(str==='now'){str=(new Date()).toString();}
if(str.match(/^(\d\d)(?:-|\/)(\d\d)(?:-|\/)(\d\d\d\d)(.*)$/)){str='{1}/{2}/{3}{4}'.format(RegExp.$3,RegExp.$2,RegExp.$1,RegExp.$4);}
if(str.match(/^(\d\d\d\d)(-|\/)(\d\d)(-|\/)(\d\d)( |T)(\d\d):(\d\d):(\d\d)$/)){str=RegExp.$1+'-'+RegExp.$3+'-'+RegExp.$5+'T'+RegExp.$7+':'+RegExp.$8+':'+RegExp.$9;}
if(str.match(/^\d\d\d\d-\d\d-\d\d$/)){str=str.replace(/-/g,'/');}
if(str.match(/^\d\d:\d\d:\d\d$/)){var dateObj=new Date();var date=dateObj.getDate();var month=dateObj.getMonth()+1;var year=dateObj.getFullYear();if(String(month).length===1)month='0'+month;if(String(date).length===1)date='0'+date;str=(year+'/'+month+'/'+date)+' '+str;}
return Date.parse(str);};RGraph.resetColorsToOriginalValues=function(obj)
{if(obj.original_colors){for(var j in obj.original_colors){if(typeof j==='string'){obj.properties[j]=RGraph.arrayClone(obj.original_colors[j]);}}}
if(typeof obj.resetColorsToOriginalValues==='function'){obj.resetColorsToOriginalValues();}
obj.colorsParsed=false;};RGraph.linearGradient=RGraph.LinearGradient=function(obj,x1,y1,x2,y2,color1,color2)
{var gradient=obj.context.createLinearGradient(x1,y1,x2,y2);var numColors=arguments.length-5;for(var i=5;i<arguments.length;++i){var color=arguments[i];var stop=(i-5)/(numColors-1);gradient.addColorStop(stop,color);}
return gradient;};RGraph.radialGradient=RGraph.RadialGradient=function(obj,x1,y1,r1,x2,y2,r2,color1,color2)
{var gradient=obj.context.createRadialGradient(x1,y1,r1,x2,y2,r2);var numColors=arguments.length-7;for(var i=7;i<arguments.length;++i){var color=arguments[i];var stop=(i-7)/(numColors-1);gradient.addColorStop(stop,color);}
return gradient;};RGraph.addEventListener=RGraph.AddEventListener=function(id,e,func)
{var type=arguments[3]?arguments[3]:'unknown';RGraph.Registry.get('event.handlers').push([id,e,func,type]);};RGraph.clearEventListeners=RGraph.ClearEventListeners=function(id)
{if(id&&id=='window'){window.removeEventListener('mousedown',window.__rgraph_mousedown_event_listener_installed__,false);window.removeEventListener('mouseup',window.__rgraph_mouseup_event_listener_installed__,false);}else{var canvas=document.getElementById(id);canvas.removeEventListener('mouseup',canvas.__rgraph_mouseup_event_listener_installed__,false);canvas.removeEventListener('mousemove',canvas.__rgraph_mousemove_event_listener_installed__,false);canvas.removeEventListener('mousedown',canvas.__rgraph_mousedown_event_listener_installed__,false);canvas.removeEventListener('click',canvas.__rgraph_click_event_listener_installed__,false);}};RGraph.hidePalette=RGraph.HidePalette=function()
{var div=RGraph.Registry.get('palette');if(typeof div=='object'&&div){div.style.visibility='hidden';div.style.display='none';RGraph.Registry.set('palette',null);}};RGraph.random=function(min,max)
{var dp=arguments[2]?arguments[2]:0;var r=Math.random();return Number((((max-min)*r)+min).toFixed(dp));};RGraph.arrayRand=RGraph.arrayRandom=RGraph.random.array=function(num,min,max)
{for(var i=0,arr=[];i<num;i+=1){arr.push(RGraph.random(min,max,arguments[3]));}
return arr;};RGraph.noShadow=RGraph.NoShadow=function(obj)
{obj.context.shadowColor='rgba(0,0,0,0)';obj.context.shadowBlur=0;obj.context.shadowOffsetx=0;obj.context.shadowOffsety=0;};RGraph.setShadow=RGraph.SetShadow=function(opt)
{if(typeof opt==='object'&&typeof opt.object==='object'&&typeof opt.object.isRGraph&&typeof opt.prefix==='string'){var obj=opt.object;obj.context.shadowColor=obj.properties[opt.prefix+'Color'];obj.context.shadowOffsetX=obj.properties[opt.prefix+'Offsetx'];obj.context.shadowOffsetY=obj.properties[opt.prefix+'Offsety'];obj.context.shadowBlur=obj.properties[opt.prefix+'Blur'];}else if(arguments.length===1&&typeof arguments[0]==='object'&&typeof arguments[0].isRGraph){var obj=arguments[0];obj.context.shadowColor='rgba(0,0,0,0)';obj.context.shadowOffsetX=0;obj.context.shadowOffsetY=0;obj.context.shadowBlur=0;}else{var obj=arguments[0];obj.context.shadowColor=arguments[1];obj.context.shadowOffsetX=arguments[2];obj.context.shadowOffsetY=arguments[3];obj.context.shadowBlur=arguments[4];}};RGraph.Registry.set=RGraph.Registry.Set=function(name,value)
{name=name.replace(/([A-Z])/g,function(str)
{return'.'+String(RegExp.$1).toLowerCase();});RGraph.Registry.store[name]=value;return value;};RGraph.Registry.get=RGraph.Registry.Get=function(name)
{name=name.replace(/([A-Z])/g,function(str)
{return'.'+String(RegExp.$1).toLowerCase();});return RGraph.Registry.store[name];};RGraph.degrees2Radians=function(deg)
{return deg*(RGraph.PI/180);};RGraph.toRadians=function(degrees)
{return degrees*(RGraph.PI/180);};RGraph.toDegrees=function(radians)
{return radians*(180/Math.PI);};RGraph.log=function(n,base)
{return Math.log(n)/(base?Math.log(base):1);};RGraph.isArray=RGraph.is_array=function(obj)
{if(obj&&obj.constructor){var pos=obj.constructor.toString().indexOf('Array');}else{return false;}
return obj!=null&&typeof pos==='number'&&pos>0&&pos<20;};RGraph.trim=function(str)
{return RGraph.ltrim(RGraph.rtrim(str));};RGraph.ltrim=function(str)
{return str.replace(/^(\s|\0)+/,'');};RGraph.rtrim=function(str)
{return str.replace(/(\s|\0)+$/,'');};RGraph.isNull=RGraph.is_null=function(arg)
{if(arg==null||typeof arg==='object'&&!arg){return true;}
return false;};RGraph.async=RGraph.Async=function(func)
{return setTimeout(func,arguments[1]?arguments[1]:1);};RGraph.reset=RGraph.Reset=function(canvas)
{canvas.width=canvas.width;RGraph.ObjectRegistry.clear(canvas);canvas.__rgraph_aa_translated__=false;if(RGraph.text.domNodeCache&&RGraph.text.domNodeCache.reset){RGraph.text.domNodeCache.reset(canvas);}
if(!RGraph.text.domNodeCache){RGraph.text.domNodeCache=[];}
if(!RGraph.text.domNodeDimensionCache){RGraph.text.domNodeDimensionCache=[];}
RGraph.text.domNodeCache[canvas.id]=[];RGraph.text.domNodeDimensionCache[canvas.id]=[];};RGraph.getCanvasTag=function(id)
{id=typeof id==='object'?id.id:id;var canvas=doc.getElementById(id);return[id,canvas];};RGraph.Effects.updateCanvas=RGraph.Effects.UpdateCanvas=function(func)
{win.requestAnimationFrame=win.requestAnimationFrame||win.webkitRequestAnimationFrame||win.msRequestAnimationFrame||win.mozRequestAnimationFrame||(function(func){setTimeout(func,16.666);});win.requestAnimationFrame(func);};RGraph.Effects.getEasingMultiplier=function(frames,frame)
{return Math.pow(Math.sin((frame/frames)*RGraph.HALFPI),3);};RGraph.stringsToNumbers=function(str)
{var sep=arguments[1]||',';if(typeof str==='number'){return str;}
if(typeof str==='string'){if(str.indexOf(sep)!=-1){str=str.split(sep);}else{str=parseFloat(str);}}
if(typeof str==='object'&&!RGraph.isNull(str)){for(var i=0,len=str.length;i<len;i+=1){str[i]=parseFloat(str[i]);}}
return str;};RGraph.cachedDraw=function(obj,id,func)
{if(!RGraph.cache[id]){RGraph.cache[id]={};RGraph.cache[id].object=obj;RGraph.cache[id].canvas=document.createElement('canvas');RGraph.cache[id].canvas.setAttribute('width',obj.canvas.width);RGraph.cache[id].canvas.setAttribute('height',obj.canvas.height);RGraph.cache[id].canvas.setAttribute('id','background_cached_canvas'+obj.canvas.id);RGraph.cache[id].canvas.__object__=obj;RGraph.cache[id].context=RGraph.cache[id].canvas.getContext('2d');RGraph.cache[id].context.translate(0.5,0.5);func(obj,RGraph.cache[id].canvas,RGraph.cache[id].context);}
obj.context.drawImage(RGraph.cache[id].canvas,-0.5,-0.5);};RGraph.parseObjectStyleConfig=function(obj,config)
{for(var i in config){if(typeof i==='string'){obj.set(i,config[i]);}}};RGraph.path=RGraph.path2=function(opt)
{var arguments=Array.prototype.slice.call(arguments);if(arguments.length===1&&opt.object&&opt.path){var context=opt.object.context;var p=opt.path;var args=opt.args;}else if(arguments.length===1&&opt.context&&opt.path){var context=opt.context;var p=opt.path;var args=opt.args;}else if(arguments.length>=2&&arguments[0].isRGraph&&arguments[0].context){var context=arguments[0].context;var p=arguments[1];var args=arguments.length>2?arguments.slice(2):[];}else if(arguments.length>=2&&arguments[0].toString().indexOf('Context')){var context=arguments[0];var p=arguments[1];var args=arguments.length>2?arguments.slice(2):[];}
if(typeof p==='string'){p=splitstring(p);}
RGraph.path.last=RGraph.arrayClone(p);for(var i=0,len=p.length;i<len;i+=1){switch(p[i]){case'b':context.beginPath();break;case'c':context.closePath();break;case'm':context.moveTo(parseFloat(p[i+1]),parseFloat(p[i+2]));i+=2;break;case'l':context.lineTo(parseFloat(p[i+1]),parseFloat(p[i+2]));i+=2;break;case's':if(p[i+1])context.strokeStyle=p[i+1];context.stroke();i++;break;case'f':if(p[i+1]){context.fillStyle=p[i+1];}context.fill();i++;break;case'qc':context.quadraticCurveTo(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]));i+=4;break;case'bc':context.bezierCurveTo(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]),parseFloat(p[i+6]));i+=6;break;case'r':context.rect(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]));i+=4;break;case'a':context.arc(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]),p[i+6]==='true'||p[i+6]===true||p[i+6]===1||p[i+6]==='1'?true:false);i+=6;break;case'at':context.arcTo(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]));i+=5;break;case'lw':context.lineWidth=parseFloat(p[i+1]);i++;break;case'e':context.ellipse(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]),parseFloat(p[i+6]),parseFloat(p[i+7]),p[i+8]==='true'?true:false);i+=8;break;case'lj':context.lineJoin=p[i+1];i++;break;case'lc':context.lineCap=p[i+1];i++;break;case'sc':context.shadowColor=p[i+1];i++;break;case'sb':context.shadowBlur=parseFloat(p[i+1]);i++;break;case'sx':context.shadowOffsetX=parseFloat(p[i+1]);i++;break;case'sy':context.shadowOffsetY=parseFloat(p[i+1]);i++;break;case'fs':context.fillStyle=p[i+1];i++;break;case'ss':context.strokeStyle=p[i+1];i++;break;case'fr':context.fillRect(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]));i+=4;break;case'sr':context.strokeRect(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]));i+=4;break;case'cl':context.clip();break;case'sa':context.save();break;case'rs':context.restore();break;case'tr':context.translate(parseFloat(p[i+1]),parseFloat(p[i+2]));i+=2;break;case'sl':context.scale(parseFloat(p[i+1]),parseFloat(p[i+2]));i+=2;break;case'ro':context.rotate(parseFloat(p[i+1]));i++;break;case'tf':context.transform(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]),parseFloat(p[i+6]));i+=6;break;case'stf':context.setTransform(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]),parseFloat(p[i+5]),parseFloat(p[i+6]));i+=6;break;case'cr':context.clearRect(parseFloat(p[i+1]),parseFloat(p[i+2]),parseFloat(p[i+3]),parseFloat(p[i+4]));i+=4;break;case'ld':var parts=p[i+1];context.setLineDash(parts);i+=1;break;case'ldo':context.lineDashOffset=p[i+1];i++;break;case'fo':context.font=p[i+1];i++;break;case'ft':context.fillText(p[i+1],parseFloat(p[i+2]),parseFloat(p[i+3]));i+=3;break;case'st':context.strokeText(p[i+1],parseFloat(p[i+2]),parseFloat(p[i+3]));i+=3;break;case'ta':context.textAlign=p[i+1];i++;break;case'tbl':context.textBaseline=p[i+1];i++;break;case'ga':context.globalAlpha=parseFloat(p[i+1]);i++;break;case'gco':context.globalCompositeOperation=p[i+1];i++;break;case'fu':(p[i+1])(context.canvas.__object__);i++;break;case'':break;default:alert('[ERROR] Unknown option: '+p[i]);}}
function splitstring(p)
{var ret=[],buffer='',inquote=false,quote='',substitutionIndex=0;for(var i=0;i<p.length;i+=1){var chr=p[i],isWS=chr.match(/ /);if(isWS){if(!inquote){if(buffer[0]==='"'||buffer[0]==="'"){buffer=buffer.substr(1,buffer.length-2);}
if(buffer.trim()==='%'&&typeof args[substitutionIndex]!=='undefined'){buffer=args[substitutionIndex++];}
ret.push(buffer);buffer='';}else{buffer+=chr;}}else{if(chr==="'"||chr==='"'){inquote=!inquote;}
buffer+=chr;}}
if(buffer.trim()==='%'&&args[substitutionIndex]){buffer=args[substitutionIndex++];}
ret.push(buffer);return ret;}};RGraph.getTextConf=function(opt)
{var obj=opt.object,prop=obj.properties,prefix=opt.prefix;var font=typeof prop[prefix+'Font']==='string'?prop[prefix+'Font']:prop.textFont,size=typeof prop[prefix+'Size']==='number'?prop[prefix+'Size']:prop.textSize,color=typeof prop[prefix+'Color']==='string'?prop[prefix+'Color']:prop.textColor,bold=!RGraph.isNull(prop[prefix+'Bold'])?prop[prefix+'Bold']:prop.textBold,italic=!RGraph.isNull(prop[prefix+'Italic'])?prop[prefix+'Italic']:prop.textItalic;return{font:font,size:size,color:color,bold:bold,italic:italic};};RGraph.responsive=function(conf)
{var opt=arguments[1]||{},obj=this,func=null,timer=null;opt.delay=typeof opt.delay==='number'?opt.delay:200;var func=function()
{var matched=false;for(var i=0;i<conf.length;++i){if(!matched&&(document.documentElement.clientWidth<=conf[i].maxWidth||RGraph.isNull(conf[i].maxWidth))){matched=true;if(typeof conf[i].width==='number'){if(obj.get('textAccessible')){obj.canvas.parentNode.style.width=conf[i].width+'px';}
obj.canvas.width=conf[i].width;}
if(typeof conf[i].height==='number'){if(obj.get('textAccessible')){obj.canvas.parentNode.style.height=conf[i].height+'px';}
obj.canvas.height=conf[i].height;}
if(typeof conf[i].options==='object'&&typeof conf[i].options==='object'){for(var j in conf[i].options){if(typeof j==='string'){obj.set(j,conf[i].options[j]);}}}
var setCSS=function(el,name,value)
{var replacements=[['float','cssFloat']];for(var i=0;i<replacements.length;++i){if(name===replacements[i][0]){name=replacements[i][1];}}
el.style[name]=value;};if(typeof conf[i].css==='object'){for(var j in conf[i].css){if(typeof j==='string'){if(obj.get('textAccessible')){setCSS(obj.canvas.parentNode,j,conf[i].css[j]);}else{setCSS(obj.canvas,j,conf[i].css[j]);}}}}
if(typeof conf[i].parentCss==='object'){for(var j in conf[i].parentCss){if(typeof j==='string'){if(obj.get('textAccessible')){setCSS(obj.canvas.parentNode.parentNode,j,conf[i].parentCss[j]);}else{setCSS(obj.canvas.parentNode,j,conf[i].parentCss[j])}}}}
RGraph.cache=[];RGraph.resetColorsToOriginalValues(obj);if(obj.get('textAccessible')){RGraph.text.domNodeCache.reset(obj.canvas);}
RGraph.redraw();if(typeof conf[i].callback==='function'){(conf[i].callback)(obj);}}}}
RGraph.responsive.window_resize_event_listener=function()
{if(opt.delay>0){clearTimeout(timer);timer=setTimeout(func,opt.delay);}else{func();}};window.addEventListener('resize',RGraph.responsive.window_resize_event_listener,false);func();return obj;};RGraph.wrap=function(){};})(window,document);window.$p=function(v)
{RGraph.pr(arguments[0],arguments[1],arguments[3]);};window.$a=function(v)
{alert(v);};window.$cl=function(v)
{return console.log(v);};String.prototype.format=function()
{var args=arguments;var s=this.replace(/{(\d+)}/g,function(str,idx)
{return typeof args[idx-1]!=='undefined'?args[idx-1]:str;});s=s.replace(/(?:%|\\)%(\d)/g,'__PPEERRCCEENNTT__$1');s=s.replace(/%(\d+)/g,function(str,idx)
{return typeof args[idx-1]!=='undefined'?args[idx-1]:str;});return s.replace('__PPEERRCCEENNTT__','%');};