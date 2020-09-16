
RGraph=window.RGraph||{isRGraph:true,isrgraph:true,rgraph:true};RGraph.Drawing=RGraph.Drawing||{};RGraph.Drawing.YAxis=function(conf)
{var id=conf.id
var x=conf.x;this.id=id;this.canvas=document.getElementById(this.id);this.context=this.canvas.getContext("2d");this.canvas.__object__=this;this.x=x;this.coords=[];this.coordsText=[];this.original_colors=[];this.maxLabelLength=0;this.firstDraw=true;this.type='drawing.yaxis';this.isRGraph=true;this.isrgraph=true;this.rgraph=true;this.uid=RGraph.createUID();this.canvas.uid=this.canvas.uid?this.canvas.uid:RGraph.createUID();this.properties={marginLeft:35,marginRight:35,marginTop:35,marginBottom:35,colors:['black'],title:'',titleColor:null,titleFont:null,titleSize:null,titleBold:null,titleItalic:null,textFont:'Arial, Verdana, sans-serif',textSize:12,textColor:'black',textBold:false,textItalic:false,textAccessible:true,textAccessibleOverflow:'visible',textAccessiblePointerevents:false,yaxis:true,yaxisLinewidth:1,yaxisColor:'black',yaxisTickmarks:true,yaxisTickmarksCount:null,yaxisTickmarksLastTop:null,yaxisTickmarksLastBottom:null,yaxisTickmarksLength:3,yaxisScale:true,yaxisScaleMin:0,yaxisScaleMax:null,yaxisScaleUnitsPre:'',yaxisScaleUnitsPost:'',yaxisScaleDecimals:0,yaxisScalePoint:'.',yaxisScaleThousand:',',yaxisScaleRound:false,yaxisScaleFormatter:null,yaxisLabelsSpecific:null,yaxisLabelsCount:5,yaxisLabels:null,yaxisLabelsOffsetx:0,yaxisLabelsOffsety:0,yaxisLabelsHalign:null,yaxisLabelsValign:null,yaxisLabelsFont:null,yaxisLabelsSize:null,yaxisLabelsColor:null,yaxisLabelsBold:null,yaxisLabelsItalic:null,yaxisLabelsPosition:'edge',yaxisPosition:'left',yaxisTitle:'',yaxisTitleBold:null,yaxisTitleSize:null,yaxisTitleFont:null,yaxisTitleColor:null,yaxisTitleItalic:null,yaxisTitlePos:null,yaxisTitleX:null,yaxisTitleY:null,yaxisTitleOffsetx:0,yaxisTitleOffsety:0,yaxisTitleHalign:null,yaxisTitleValign:null,yaxisTitleAccessible:null,xaxisPosition:'bottom',linewidth:1,tooltips:null,tooltipsEffect:'fade',tooltipsCssClass:'RGraph_tooltip',tooltipsCss:null,tooltipsEvent:'onclick',tooltipsFormattedPoint:'.',tooltipsFormattedThousand:',',tooltipsFormattedDecimals:0,tooltipsFormattedUnitsPre:'',tooltipsFormattedUnitsPost:'',tooltipsFormattedTableHeaders:null,tooltipsFormattedTableData:null,tooltipsPointer:true,tooltipsPositionStatic:true,xaxisPosition:'bottom',clearto:'rgba(0,0,0,0)'}
if(!this.canvas){alert('[DRAWING.YAXIS] No canvas support');return;}
this.$0={};if(!this.canvas.__rgraph_aa_translated__){this.context.translate(0.5,0.5);this.canvas.__rgraph_aa_translated__=true;}
var prop=this.properties;this.path=RGraph.pathObjectFunction;if(RGraph.Effects&&typeof RGraph.Effects.decorate==='function'){RGraph.Effects.decorate(this);}
this.set=function(name)
{var value=typeof arguments[1]==='undefined'?null:arguments[1];if(arguments.length===1&&typeof arguments[0]==='object'){for(i in arguments[0]){if(typeof i==='string'){this.set(i,arguments[0][i]);}}
return this;}
prop[name]=value;return this;};this.get=function(name)
{return prop[name];};this.draw=function()
{RGraph.fireCustomEvent(this,'onbeforedraw');this.marginTop=prop.marginTop;this.marginBottom=prop.marginBottom;this.coordsText=[];if(!prop.textColor)prop.textColor=prop.colors[0];if(!prop.titleColor)prop.titleColor=prop.textColor;if(!this.colorsParsed){this.parseColors();this.colorsParsed=true;}
this.drawYAxis();RGraph.installEventListeners(this);if(this.firstDraw){this.firstDraw=false;RGraph.fireCustomEvent(this,'onfirstdraw');this.firstDrawFunc();}
RGraph.fireCustomEvent(this,'ondraw');return this;};this.exec=function(func)
{func(this);return this;};this.getObjectByXY=function(e)
{if(this.getShape(e)){return this;}};this.getShape=function(e)
{var mouseXY=RGraph.getMouseXY(e);var mouseX=mouseXY[0];var mouseY=mouseXY[1];if(mouseX>=this.x-(prop.tickmarksAlign=='right'?0:this.getWidth())&&mouseX<=this.x+(prop.tickmarksAlign=='right'?this.getWidth():0)&&mouseY>=this.marginTop&&mouseY<=(this.canvas.height-this.marginBottom)){var x=this.x;var y=this.marginTop;var w=15;;var h=this.canvas.height-this.marginTop-this.marginBottom;if(RGraph.parseTooltipText&&prop.tooltips){var tooltip=RGraph.parseTooltipText(prop.tooltips,0);}
return{object:this,x:x,y:y,width:w,height:h,dataset:0,index:0,sequentialIndex:0,tooltip:typeof tooltip==='string'?tooltip:null};}
return null;};this.highlight=function(shape)
{if(typeof prop.highlightStyle==='function'){(prop.highlightStyle)(shape);}};this.parseColors=function()
{if(this.original_colors.length===0){this.original_colors.yaxisLabelsColor=RGraph.arrayClone(prop.yaxisLabelsColor);this.original_colors.titleColor=RGraph.arrayClone(prop.titleColor);this.original_colors.textColor=RGraph.arrayClone(prop.textColor);this.original_colors.colors=RGraph.arrayClone(prop.colors);}
prop.yaxisLabelsColor=this.parseSingleColorForGradient(prop.yaxisLabelsColor);prop.titleColor=this.parseSingleColorForGradient(prop.titleColor);prop.textColor=this.parseSingleColorForGradient(prop.textColor);prop.colors[0]=this.parseSingleColorForGradient(prop.colors[0]);};this.reset=function()
{};this.parseSingleColorForGradient=function(color)
{if(!color){return color;}
if(typeof color==='string'&&color.match(/^gradient\((.*)\)$/i)){if(color.match(/^gradient\(({.*})\)$/i)){return RGraph.parseJSONGradient({object:this,def:RegExp.$1});}
var parts=RegExp.$1.split(':');var grad=this.context.createLinearGradient(0,prop.marginTop,0,this.canvas.height-this.marginBottom);var diff=1/(parts.length-1);grad.addColorStop(0,RGraph.trim(parts[0]));for(var j=1;j<parts.length;++j){grad.addColorStop(j*diff,RGraph.trim(parts[j]));}}
return grad?grad:color;};this.drawYAxis=function()
{RGraph.drawYAxis(this);};this.getWidth=function()
{var width=this.maxLabelLength;if(prop.yaxisTitle&&prop.yaxisTitle.length){width+=(prop.textSize*1.5);}
this.width=width;return width;};this.on=function(type,func)
{if(type.substr(0,2)!=='on'){type='on'+type;}
if(typeof this[type]!=='function'){this[type]=func;}else{RGraph.addCustomEventListener(this,type,func);}
return this;};this.firstDrawFunc=function()
{};this.tooltipSubstitutions=function(opt)
{return{index:0,dataset:0,sequentialIndex:0,value:null};};this.positionTooltipStatic=function(args)
{var obj=args.object,e=args.event,tooltip=args.tooltip,index=args.index,canvasXY=RGraph.getCanvasXY(obj.canvas);args.tooltip.style.left=(canvasXY[0]
-(tooltip.offsetWidth/2)
+obj.properties.tooltipsOffsetx
+this.x
-(this.getWidth()/2))+'px';args.tooltip.style.top=(canvasXY[1]
-tooltip.offsetHeight
+obj.properties.tooltipsOffsety
+prop.marginTop
-((prop.textSize*1.5)/2)
-10)+'px';};RGraph.register(this);RGraph.parseObjectStyleConfig(this,conf.options);};