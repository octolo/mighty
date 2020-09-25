
RGraph=window.RGraph||{isrgraph:true,isRGraph:true,rgraph:true};RGraph.SVG=RGraph.SVG||{};(function(win,doc,undefined)
{RGraph.SVG.Line=function(conf)
{this.set=function(name,value)
{if(arguments.length===1&&typeof name==='object'){for(i in arguments[0]){if(typeof i==='string'){name=ret.name;value=ret.value;this.set(name,value);}}}else{var ret=RGraph.SVG.commonSetter({object:this,name:name,value:value});name=ret.name;value=ret.value;this.properties[name]=value;if(name==='colors'){this.originalColors=RGraph.SVG.arrayClone(value);this.colorsParsed=false;}}
return this;};this.get=function(name)
{return this.properties[name];};this.id=conf.id;this.uid=RGraph.SVG.createUID();this.container=document.getElementById(this.id);this.layers={};this.svg=RGraph.SVG.createSVG({object:this,container:this.container});this.isRGraph=true;this.isrgraph=true;this.rgraph=true;this.width=Number(this.svg.getAttribute('width'));this.height=Number(this.svg.getAttribute('height'));if(RGraph.SVG.isArray(conf.data)&&RGraph.SVG.isArray(conf.data[0])){this.data=RGraph.SVG.arrayClone(conf.data);}else if(RGraph.SVG.isArray(conf.data)){this.data=[RGraph.SVG.arrayClone(conf.data)];}else{this.data=[[]];}
this.type='line';this.coords=[];this.coords2=[];this.coordsSpline=[];this.hasMultipleDatasets=typeof this.data[0]==='object'&&typeof this.data[1]==='object'?true:false;this.colorsParsed=false;this.originalColors={};this.gradientCounter=1;this.originalData=RGraph.SVG.arrayClone(this.data);this.filledGroups=[];RGraph.SVG.OR.add(this);this.container.style.display='inline-block';this.properties={marginLeft:35,marginRight:35,marginTop:35,marginBottom:35,marginInner:0,backgroundColor:null,backgroundImage:null,backgroundImageStretch:true,backgroundImageAspect:'none',backgroundImageOpacity:null,backgroundImageX:null,backgroundImageY:null,backgroundImageW:null,backgroundImageH:null,backgroundGrid:true,backgroundGridColor:'#ddd',backgroundGridLinewidth:1,backgroundGridHlines:true,backgroundGridHlinesCount:null,backgroundGridVlines:true,backgroundGridVlinesCount:null,backgroundGridBorder:true,backgroundGridDashed:false,backgroundGridDotted:false,backgroundGridDashArray:null,colors:['red','#0f0','blue','#ff0','#0ff','green'],filled:false,filledColors:[],filledClick:null,filledOpacity:1,filledAccumulative:false,yaxis:true,yaxisTickmarks:true,yaxisTickmarksLength:3,yaxisColor:'black',yaxisScale:true,yaxisLabels:null,yaxisLabelsOffsetx:0,yaxisLabelsOffsety:0,yaxisLabelsCount:5,yaxisScaleUnitsPre:'',yaxisScaleUnitsPost:'',yaxisScaleStrict:false,yaxisScaleDecimals:0,yaxisScalePoint:'.',yaxisScaleThousand:',',yaxisScaleRound:false,yaxisScaleMax:null,yaxisScaleMin:0,yaxisScaleFormatter:null,yaxisLabelsFont:null,yaxisLabelsSize:null,yaxisLabelsColor:null,yaxisLabelsBold:null,yaxisLabelsItalic:null,xaxis:true,xaxisTickmarks:true,xaxisTickmarksLength:5,xaxisLabels:null,xaxisLabelsOffsetx:0,xaxisLabelsOffsety:0,xaxisLabelsPosition:'edge',xaxisLabelsPositionEdgeTickmarksCount:null,xaxisColor:'black',xaxisLabelsFont:null,xaxisLabelsSize:null,xaxisLabelsColor:null,xaxisLabelsBold:null,xaxisLabelsItalic:null,textColor:'black',textFont:'Arial, Verdana, sans-serif',textSize:12,textBold:false,textItalic:false,linewidth:1,tooltips:null,tooltipsOverride:null,tooltipsEffect:'fade',tooltipsCssClass:'RGraph_tooltip',tooltipsCss:null,tooltipsEvent:'mousemove',tooltipsFormattedThousand:',',tooltipsFormattedPoint:'.',tooltipsFormattedDecimals:0,tooltipsFormattedUnitsPre:'',tooltipsFormattedUnitsPost:'',tooltipsFormattedKeyColors:null,tooltipsFormattedKeyColorsShape:'square',tooltipsFormattedKeyLabels:[],tooltipsFormattedTableHeaders:null,tooltipsFormattedTableData:null,tooltipsPointer:true,tooltipsPositionStatic:true,tickmarksStyle:'none',tickmarksSize:5,tickmarksFill:'white',tickmarksLinewidth:1,labelsAbove:false,labelsAboveFont:null,labelsAboveSize:null,labelsAboveBold:null,labelsAboveItalic:null,labelsAboveColor:null,labelsAboveBackground:'rgba(255,255,255,0.7)',labelsAboveBackgroundPadding:2,labelsAboveUnitsPre:null,labelsAboveUnitsPost:null,labelsAbovePoint:null,labelsAboveThousand:null,labelsAboveFormatter:null,labelsAboveDecimals:null,labelsAboveOffsetx:0,labelsAboveOffsety:-10,labelsAboveHalign:'center',labelsAboveValign:'bottom',labelsAboveSpecific:null,shadow:false,shadowOffsetx:2,shadowOffsety:2,shadowBlur:2,shadowOpacity:0.25,spline:false,stepped:false,title:'',titleX:null,titleY:null,titleHalign:'center',titleValign:null,titleSize:null,titleColor:null,titleFont:null,titleBold:null,titleItalic:null,titleSubtitle:null,titleSubtitleSize:null,titleSubtitleColor:'#aaa',titleSubtitleFont:null,titleSubtitleBold:null,titleSubtitleItalic:null,errorbars:null,errorbarsColor:'black',errorbarsLinewidth:1,errorbarsCapwidth:10,key:null,keyColors:null,keyOffsetx:0,keyOffsety:0,keyLabelsOffsetx:0,keyLabelsOffsety:-1,keyLabelsSize:null,keyLabelsBold:null,keyLabelsItalic:null,keyLabelsFont:null,keyLabelsColor:null,dasharray:[1,0],dashed:false,dotted:false};RGraph.SVG.getGlobals(this);if(RGraph.SVG.FX&&typeof RGraph.SVG.FX.decorate==='function'){RGraph.SVG.FX.decorate(this);}
this.responsive=RGraph.SVG.responsive;var prop=this.properties;this.draw=function()
{RGraph.SVG.fireCustomEvent(this,'onbeforedraw');this.width=Number(this.svg.getAttribute('width'));this.height=Number(this.svg.getAttribute('height'));RGraph.SVG.createDefs(this);this.graphWidth=this.width-prop.marginLeft-prop.marginRight;this.graphHeight=this.height-prop.marginTop-prop.marginBottom;RGraph.SVG.resetColorsToOriginalValues({object:this});this.parseColors();this.coords=[];this.coords2=[];this.coordsSpline=[];this.data=RGraph.SVG.arrayClone(this.originalData);this.tooltipsSequentialIndex=0;if(prop.dashed){prop.dasharray=[5,5];}
if(prop.dotted){prop.dasharray=[1,4];}
this.data_seq=RGraph.SVG.arrayLinearize(this.data);if(prop.errorbars){for(var i=0;i<this.data_seq.length;++i){if(typeof prop.errorbars[i]==='undefined'||RGraph.SVG.isNull(prop.errorbars[i])){prop.errorbars[i]={max:null,min:null};}else if(typeof prop.errorbars[i]==='number'){prop.errorbars[i]={min:prop.errorbars[i],max:prop.errorbars[i]};}else if(typeof prop.errorbars[i]==='object'&&typeof prop.errorbars[i].max==='undefined'){prop.errorbars[i].max=null;}else if(typeof prop.errorbars[i]==='object'&&typeof prop.errorbars[i].min==='undefined'){prop.errorbars[i].min=null;}}}
for(var i=0,tmp=[];i<this.data.length;++i){for(var j=0;j<this.data[i].length;++j){if(typeof tmp[j]==='undefined'){tmp[j]=0;}
if(prop.filled&&prop.filledAccumulative){tmp[j]+=this.data[i][j];if(i===(this.data.length-1)){tmp[j]+=(prop.errorbars?prop.errorbars[RGraph.SVG.groupedIndexToSequential({object:this,dataset:i,index:j})].max:0)}}else{tmp[j]=Math.max(tmp[j],this.data[i][j]+(prop.errorbars?prop.errorbars[RGraph.SVG.groupedIndexToSequential({object:this,dataset:i,index:j})].max:0));}}}
var values=[];for(var i=0,max=0;i<this.data.length;++i){if(RGraph.SVG.isArray(this.data[i])&&!prop.filledAccumulative){values.push(RGraph.SVG.arrayMax(tmp));}else if(RGraph.SVG.isArray(this.data[i])&&prop.filled&&prop.filledAccumulative){for(var j=0;j<this.data[i].length;++j){values[j]=values[j]||0;values[j]=values[j]+this.data[i][j];this.data[i][j]=values[j];}}}
if(prop.filled&&prop.filledAccumulative){var max=RGraph.SVG.arrayMax(tmp)}else{var max=RGraph.SVG.arrayMax(values);}
if(typeof prop.yaxisScaleMax==='number'){max=prop.yaxisScaleMax;}
if(prop.yaxisScaleMin==='mirror'){this.mirrorScale=true;prop.yaxisScaleMin=0;}
this.scale=RGraph.SVG.getScale({object:this,numlabels:prop.yaxisLabelsCount,unitsPre:prop.yaxisScaleUnitsPre,unitsPost:prop.yaxisScaleUnitsPost,max:max,min:prop.yaxisScaleMin,point:prop.yaxisScalePoint,round:prop.yaxisScaleRound,thousand:prop.yaxisScaleThousand,decimals:prop.yaxisScaleDecimals,strict:typeof prop.yaxisScaleMax==='number',formatter:prop.yaxisScaleFormatter});if(this.mirrorScale){this.scale=RGraph.SVG.getScale({object:this,numlabels:prop.yaxisLabelsCount,unitsPre:prop.yaxisScaleUnitsPre,unitsPost:prop.yaxisScaleUnitsPost,max:this.scale.max,min:this.scale.max* -1,point:prop.yaxisScalePoint,round:false,thousand:prop.yaxisScaleThousand,decimals:prop.yaxisScaleDecimals,strict:typeof prop.yaxisScaleMax==='number',formatter:prop.yaxisScaleFormatter});}
this.max=this.scale.max;this.min=this.scale.min;RGraph.SVG.drawBackground(this);RGraph.SVG.drawXAxis(this);RGraph.SVG.drawYAxis(this);for(var i=0;i<this.data.length;++i){this.drawLine(this.data[i],i);}
this.redrawLines();if(typeof prop.key!==null&&RGraph.SVG.drawKey){RGraph.SVG.drawKey(this);}else if(!RGraph.SVG.isNull(prop.key)){alert('The drawKey() function does not exist - have you forgotten to include the key library?');}
this.drawLabelsAbove();var obj=this;document.body.addEventListener('mousedown',function(e)
{RGraph.SVG.removeHighlight(obj);},false);RGraph.SVG.fireCustomEvent(this,'ondraw');return this;};this.drawLine=function(data,index)
{var coords=[],path=[];for(var i=0,len=data.length;i<len;++i){var val=data[i],x=(((this.graphWidth-prop.marginInner-prop.marginInner)/(len-1))*i)+prop.marginLeft+prop.marginInner,y=this.getYCoord(val);coords.push([x,y]);}
for(var i=0;i<coords.length;++i){if(i===0||RGraph.SVG.isNull(data[i])||RGraph.SVG.isNull(data[i-1])){var action='M';}else{if(prop.stepped){path.push('L {1} {2}'.format(coords[i][0],coords[i-1][1]));}
var action='L';}
path.push(action+'{1} {2}'.format(coords[i][0],RGraph.SVG.isNull(data[i])?0:coords[i][1]));}
for(var k=0;k<coords.length;++k){this.coords.push(RGraph.SVG.arrayClone(coords[k]));this.coords[this.coords.length-1].x=coords[k][0];this.coords[this.coords.length-1].y=coords[k][1];this.coords[this.coords.length-1].object=this;this.coords[this.coords.length-1].value=data[k];this.coords[this.coords.length-1].index=k;this.coords[this.coords.length-1].path=path;}
this.coords2[index]=RGraph.SVG.arrayClone(coords);for(var k=0;k<coords.length;++k){var seq=RGraph.SVG.groupedIndexToSequential({object:this,dataset:index,index:k});this.coords2[index][k].x=coords[k][0];this.coords2[index][k].y=coords[k][1];this.coords2[index][k].object=this;this.coords2[index][k].value=data[k];this.coords2[index][k].index=k;this.coords2[index][k].path=path;this.coords2[index][k].sequential=seq;if(prop.errorbars){this.drawErrorbar({object:this,dataset:index,index:k,sequential:seq,x:x,y:y});}}
if(prop.spline){this.coordsSpline[index]=this.drawSpline(coords);}
if(prop.filled===true||(typeof prop.filled==='object'&&prop.filled[index])){if(prop.spline){var fillPath=['M{1} {2}'.format(this.coordsSpline[index][0][0],this.coordsSpline[index][0][1])];for(var i=1;i<this.coordsSpline[index].length;++i){fillPath.push('L{1} {2}'.format(this.coordsSpline[index][i][0]+((i===(this.coordsSpline[index].length)-1)?1:0),this.coordsSpline[index][i][1]));}}else{var fillPath=RGraph.SVG.arrayClone(path);}
fillPath.push('L{1} {2}'.format(this.coords2[index][this.coords2[index].length-1][0]+1,index>0&&prop.filledAccumulative?(prop.spline?this.coordsSpline[index-1][this.coordsSpline[index-1].length-1][1]:this.coords2[index-1][this.coords2[index-1].length-1][1]):this.getYCoord(prop.yaxisScaleMin>0?prop.yaxisScaleMin:0)+(prop.xaxis?0:1)));if(index>0&&prop.filledAccumulative){var path2=RGraph.SVG.arrayClone(path);if(index>0&&prop.filledAccumulative){if(prop.spline){for(var i=this.coordsSpline[index-1].length-1;i>=0;--i){fillPath.push('L{1} {2}'.format(this.coordsSpline[index-1][i][0],this.coordsSpline[index-1][i][1]));}}else{for(var i=this.coords2[index-1].length-1;i>=0;--i){fillPath.push('L{1} {2}'.format(this.coords2[index-1][i][0],this.coords2[index-1][i][1]));if(prop.stepped&&i>0){fillPath.push('L{1} {2}'.format(this.coords2[index-1][i][0],this.coords2[index-1][i-1][1]));}}}}}else{fillPath.push('L{1} {2}'.format(this.coords2[index][0][0]+(prop.yaxis?0:0),this.getYCoord(prop.yaxisScaleMin>0?prop.yaxisScaleMin:0)+(prop.xaxis?0:1)));}
fillPath.push('L{1} {2}'.format(this.coords2[index][0][0]+(prop.yaxis?1:0),this.coords2[index][0][1]));for(var i=0;i<this.data[index].length;++i){if(!RGraph.SVG.isNull(this.data[index][i])){fillPath.push('L{1} {2}'.format(this.coords2[index][i][0],this.getYCoord(0)));break;}}
this.filledGroups[index]=RGraph.SVG.create({svg:this.svg,type:'g',parent:this.svg.all,attr:{'class':'rgraph_filled_line_'+index}});var fillPathObject=RGraph.SVG.create({svg:this.svg,parent:this.filledGroups[index],type:'path',attr:{d:fillPath.join(' '),stroke:'rgba(0,0,0,0)','fill':prop.filledColors&&prop.filledColors[index]?prop.filledColors[index]:prop.colors[index],'fill-opacity':prop.filledOpacity,'stroke-width':1,'clip-path':this.isTrace?'url(#trace-effect-clip)':''}});if(prop.filledClick){var obj=this;fillPathObject.addEventListener('click',function(e)
{prop.filledClick(e,obj,index);},false);fillPathObject.addEventListener('mousemove',function(e)
{e.target.style.cursor='pointer';},false);}}
if(prop.shadow){RGraph.SVG.setShadow({object:this,offsetx:prop.shadowOffsetx,offsety:prop.shadowOffsety,blur:prop.shadowBlur,opacity:prop.shadowOpacity,id:'dropShadow'});}
if(prop.spline){var str=['M{1} {2}'.format(this.coordsSpline[index][0][0],this.coordsSpline[index][0][1])];for(var i=1;i<this.coordsSpline[index].length;++i){str.push('L{1} {2}'.format(this.coordsSpline[index][i][0],this.coordsSpline[index][i][1]));}
str=str.join(' ');var line=RGraph.SVG.create({svg:this.svg,parent:prop.filled?this.filledGroups[index]:this.svg.all,type:'path',attr:{d:str,stroke:prop['colors'][index],'fill':'none','stroke-width':this.hasMultipleDatasets&&prop.filled&&prop.filledAccumulative?0.1:(RGraph.SVG.isArray(prop.linewidth)?prop.linewidth[index]:prop.linewidth+0.01),'stroke-dasharray':prop.dasharray,'stroke-linecap':'round','stroke-linejoin':'round',filter:prop.shadow?'url(#dropShadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}else{var path2=RGraph.SVG.arrayClone(path);if(prop.filled&&prop.filledAccumulative&&index>0){for(var i=this.coords2[index-1].length-1;i>=0;--i){path2.push('L{1} {2}'.format(this.coords2[index-1][i][0],this.coords2[index-1][i][1]));}}
path2=path2.join(' ');var line=RGraph.SVG.create({svg:this.svg,parent:prop.filled?this.filledGroups[index]:this.svg.all,type:'path',attr:{d:path2,stroke:prop.colors[index],'fill':'none','stroke-dasharray':prop.dasharray,'stroke-width':this.hasMultipleDatasets&&prop.filled&&prop.filledAccumulative?0.1:(RGraph.SVG.isArray(prop.linewidth)?prop.linewidth[index]:prop.linewidth+0.01),'stroke-linecap':'round','stroke-linejoin':'round',filter:prop.shadow?'url(#dropShadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}
if(prop.tooltips&&prop.tooltips.length){if(!this.svg.all.line_tooltip_hotspots){var group=RGraph.SVG.create({svg:this.svg,type:'g',attr:{'fill':'transparent',className:"rgraph_hotspots"},style:{cursor:'pointer'}});this.svg.all.line_tooltip_hotspots=group;}else{group=this.svg.all.line_tooltip_hotspots;}
for(var i=0;i<this.coords2[index].length&&(typeof prop.tooltips==='string'?true:this.tooltipsSequentialIndex<prop.tooltips.length);++i,++this.tooltipsSequentialIndex){if(!RGraph.SVG.isNull(this.originalData[index][i])&&(prop.tooltips[this.tooltipsSequentialIndex]||typeof prop.tooltips==='string')&&this.coords2[index][i][0]&&this.coords2[index][i][1]){var hotspot=RGraph.SVG.create({svg:this.svg,parent:group,type:'circle',attr:{cx:this.coords2[index][i][0],cy:this.coords2[index][i][1],r:10,fill:'transparent','data-dataset':index,'data-index':i},style:{cursor:'pointer'}});var obj=this;(function(sequentialIndex)
{hotspot.addEventListener(prop.tooltipsEvent,function(e)
{var indexes=RGraph.SVG.sequentialIndexToGrouped(sequentialIndex,obj.data),index=indexes[1],dataset=indexes[0];if(RGraph.SVG.REG.get('tooltip')&&RGraph.SVG.REG.get('tooltip').__index__===index&&RGraph.SVG.REG.get('tooltip').__dataset__===dataset&&RGraph.SVG.REG.get('tooltip').__object__.uid===obj.uid){return;}
obj.removeHighlight();RGraph.SVG.hideTooltip();RGraph.SVG.tooltip({object:obj,index:index,dataset:dataset,sequentialIndex:sequentialIndex,text:typeof prop.tooltips==='string'?prop.tooltips:prop.tooltips[sequentialIndex],event:e});var outer_highlight1=RGraph.SVG.create({svg:obj.svg,parent:obj.svg.all,type:'circle',attr:{cx:obj.coords2[dataset][index][0],cy:obj.coords2[dataset][index][1],r:5,fill:obj.properties.colors[dataset],'fill-opacity':0.5},style:{cursor:'pointer'}});var outer_highlight2=RGraph.SVG.create({svg:obj.svg,parent:obj.svg.all,type:'circle',attr:{cx:obj.coords2[dataset][index][0],cy:obj.coords2[dataset][index][1],r:14,fill:'white','fill-opacity':0.75},style:{cursor:'pointer'}});var inner_highlight1=RGraph.SVG.create({svg:obj.svg,parent:obj.svg.all,type:'circle',attr:{cx:obj.coords2[dataset][index][0],cy:obj.coords2[dataset][index][1],r:6,fill:'white'},style:{cursor:'pointer'}});var inner_highlight2=RGraph.SVG.create({svg:obj.svg,parent:obj.svg.all,type:'circle',attr:{cx:obj.coords2[dataset][index][0],cy:obj.coords2[dataset][index][1],r:5,fill:obj.properties.colors[dataset]},style:{cursor:'pointer'}});RGraph.SVG.REG.set('highlight',[outer_highlight1,outer_highlight2,inner_highlight1,inner_highlight2]);},false);})(this.tooltipsSequentialIndex);}}}};this.drawTickmarks=function(index,data,coords)
{var style=typeof prop.tickmarksStyle==='object'?prop.tickmarksStyle[index]:prop.tickmarksStyle,size=typeof prop.tickmarksSize==='object'?prop.tickmarksSize[index]:prop.tickmarksSize,fill=typeof prop.tickmarksFill==='object'?prop.tickmarksFill[index]:prop.tickmarksFill,linewidth=typeof prop.tickmarksLinewidth==='object'?prop.tickmarksLinewidth[index]:prop.tickmarksLinewidth;for(var i=0;i<data.length;++i){if(typeof data[i]==='number'){switch(style){case'filledcircle':case'filledendcircle':if(style==='filledcircle'||(i===0||i===data.length-1)){var circle=RGraph.SVG.create({svg:this.svg,parent:this.svg.all,type:'circle',attr:{cx:coords[index][i][0],cy:coords[index][i][1],r:size,'fill':prop.colors[index],filter:prop.shadow?'url(#dropShadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}
break;case'circle':case'endcircle':if(style==='circle'||(style==='endcircle'&&(i===0||i===data.length-1))){var outerCircle=RGraph.SVG.create({svg:this.svg,parent:this.svg.all,type:'circle',attr:{cx:coords[index][i][0],cy:coords[index][i][1],r:size+this.get('linewidth'),'fill':prop.colors[index],filter:prop.shadow?'url(#dropShadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});var innerCircle=RGraph.SVG.create({svg:this.svg,parent:this.svg.all,type:'circle',attr:{cx:coords[index][i][0],cy:coords[index][i][1],r:size,'fill':fill,'clip-path':this.isTrace?'url(#trace-effect-clip)':''}});break;}
break;case'endrect':case'rect':if(style==='rect'||(style==='endrect'&&(i===0||i===data.length-1))){var fill=typeof fill==='object'&&typeof fill[index]==='string'?fill[index]:fill;var rect=RGraph.SVG.create({svg:this.svg,parent:this.svg.all,type:'rect',attr:{x:coords[index][i][0]-size,y:coords[index][i][1]-size,width:size+size+linewidth,height:size+size+linewidth,'stroke-width':this.get('linewidth'),'stroke':prop.colors[index],'fill':fill,'clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}
break;case'filledendrect':case'filledrect':if(style==='filledrect'||(style==='filledendrect'&&(i===0||i===data.length-1))){var fill=prop.colors[index];var rect=RGraph.SVG.create({svg:this.svg,parent:this.svg.all,type:'rect',attr:{x:coords[index][i][0]-size,y:coords[index][i][1]-size,width:size+size+linewidth,height:size+size+linewidth,'fill':fill,'clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}}}}};this.redrawLines=function()
{if(prop.spline){for(var i=0;i<this.coordsSpline.length;++i){var linewidth=RGraph.SVG.isArray(prop.linewidth)?prop.linewidth[i]:prop.linewidth,color=prop['colors'][i],path='';for(var j=0;j<this.coordsSpline[i].length;++j){if(j===0){path+='M{1} {2} '.format(this.coordsSpline[i][j][0],this.coordsSpline[i][j][1]);}else{path+='L{1} {2} '.format(this.coordsSpline[i][j][0],this.coordsSpline[i][j][1]);}}
RGraph.SVG.create({svg:this.svg,parent:prop.filled?this.filledGroups[i]:this.svg.all,type:'path',attr:{d:path,stroke:color,'fill':'none','stroke-dasharray':prop.dasharray,'stroke-width':linewidth+0.01,'stroke-linecap':'round','stroke-linejoin':'round',filter:prop.shadow?'url(#dropShadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}
for(var dataset=0;dataset<this.coords2.length;++dataset){this.drawTickmarks(dataset,this.data[dataset],this.coords2);}}else{for(var i=0;i<this.coords2.length;++i){var linewidth=RGraph.SVG.isArray(prop.linewidth)?prop.linewidth[i]:prop.linewidth,color=prop['colors'][i],path='';for(var j=0;j<this.coords2[i].length;++j){if(j===0||RGraph.SVG.isNull(this.data[i][j])||RGraph.SVG.isNull(this.data[i][j-1])){path+='M{1} {2} '.format(this.coords2[i][j][0],RGraph.SVG.isNull(this.data[i][j])?0:this.coords2[i][j][1]);}else{if(prop.stepped){path+='L{1} {2} '.format(this.coords2[i][j][0],this.coords2[i][j-1][1]);}
path+='L{1} {2} '.format(this.coords2[i][j][0],this.coords2[i][j][1]);}}
RGraph.SVG.create({svg:this.svg,parent:prop.filled?this.filledGroups[i]:this.svg.all,type:'path',attr:{d:path,stroke:color,'fill':'none','stroke-dasharray':prop.dasharray,'stroke-width':linewidth+0.01,'stroke-linecap':'round','stroke-linejoin':'round',filter:prop.shadow?'url(#dropshadow)':'','clip-path':this.isTrace?'url(#trace-effect-clip)':''}});}
for(var dataset=0;dataset<this.coords2.length;++dataset){this.drawTickmarks(dataset,this.data[dataset],this.coords2);}}};this.getYCoord=function(value)
{var prop=this.properties,y;if(value>this.scale.max){return null;}
if(value<this.scale.min){return null;}
y=((value-this.scale.min)/(this.scale.max-this.scale.min));y*=(this.height-prop.marginTop-prop.marginBottom);y=this.height-prop.marginBottom-y;return y;};this.highlight=function(rect)
{var x=rect.getAttribute('x'),y=rect.getAttribute('y');};this.removeHighlight=function()
{var highlight=RGraph.SVG.REG.get('highlight');if(highlight&&highlight.parentNode){highlight.parentNode.removeChild(highlight);}else if(highlight){for(var i=0;i<highlight.length;++i){if(highlight[i]&&highlight[i].parentNode){highlight[i].parentNode.removeChild(highlight[i]);}}}
RGraph.SVG.REG.set('highlight',null);};this.drawSpline=function(coords)
{var xCoords=[];marginLeft=prop.marginLeft,marginRight=prop.marginRight,hmargin=prop.marginInner,interval=(this.graphWidth-(2*hmargin))/(coords.length-1),coordsSpline=[];for(var i=0,len=coords.length;i<len;i+=1){if(typeof coords[i]=='object'&&coords[i]&&coords[i].length==2){coords[i]=Number(coords[i][1]);}}
var P=[coords[0]];for(var i=0;i<coords.length;++i){P.push(coords[i]);}
P.push(coords[coords.length-1]+(coords[coords.length-1]-coords[coords.length-2]));for(var j=1;j<P.length-2;++j){for(var t=0;t<10;++t){var yCoord=spline(t/10,P[j-1],P[j],P[j+1],P[j+2]);xCoords.push(((j-1)*interval)+(t*(interval/10))+marginLeft+hmargin);coordsSpline.push([xCoords[xCoords.length-1],yCoord]);if(typeof index==='number'){coordsSpline[index].push([xCoords[xCoords.length-1],yCoord]);}}}
coordsSpline.push([((j-1)*interval)+marginLeft+hmargin,P[j]]);if(typeof index==='number'){coordsSpline.push([((j-1)*interval)+marginLeft+hmargin,P[j]]);}
function spline(t,P0,P1,P2,P3)
{return 0.5*((2*P1)+
((0-P0)+P2)*t+
((2*P0-(5*P1)+(4*P2)-P3)*(t*t)+
((0-P0)+(3*P1)-(3*P2)+P3)*(t*t*t)));}
for(var i=0;i<coordsSpline.length;++i){coordsSpline[i].object=this;coordsSpline[i].x=this;coordsSpline[i].y=this;}
return coordsSpline;};this.parseColors=function()
{if(!Object.keys(this.originalColors).length){this.originalColors={colors:RGraph.SVG.arrayClone(prop.colors),filledColors:RGraph.SVG.arrayClone(prop.filledColors),backgroundGridColor:RGraph.SVG.arrayClone(prop.backgroundGridColor),backgroundColor:RGraph.SVG.arrayClone(prop.backgroundColor)}}
var colors=prop.colors;if(colors){for(var i=0;i<colors.length;++i){colors[i]=RGraph.SVG.parseColorLinear({object:this,color:colors[i]});}}
var filledColors=prop.filledColors;if(filledColors){for(var i=0;i<filledColors.length;++i){filledColors[i]=RGraph.SVG.parseColorLinear({object:this,color:filledColors[i]});}}
prop.backgroundGridColor=RGraph.SVG.parseColorLinear({object:this,color:prop.backgroundGridColor});prop.backgroundColor=RGraph.SVG.parseColorLinear({object:this,color:prop.backgroundColor});};this.drawLabelsAbove=function()
{if(prop.labelsAbove){var data_seq=RGraph.SVG.arrayLinearize(this.data),seq=0;for(var dataset=0;dataset<this.coords2.length;++dataset,seq++){for(var i=0;i<this.coords2[dataset].length;++i,seq++){var str=RGraph.SVG.numberFormat({object:this,num:this.data[dataset][i].toFixed(prop.labelsAboveDecimals),prepend:typeof prop.labelsAboveUnitsPre==='string'?prop.labelsAboveUnitsPre:null,append:typeof prop.labelsAboveUnitsPost==='string'?prop.labelsAboveUnitsPost:null,point:typeof prop.labelsAbovePoint==='string'?prop.labelsAbovePoint:null,thousand:typeof prop.labelsAboveThousand==='string'?prop.labelsAboveThousand:null,formatter:typeof prop.labelsAboveFormatter==='function'?prop.labelsAboveFormatter:null});if(prop.labelsAboveSpecific&&prop.labelsAboveSpecific.length&&(typeof prop.labelsAboveSpecific[seq]==='string'||typeof prop.labelsAboveSpecific[seq]==='number')){str=prop.labelsAboveSpecific[seq];}else if(prop.labelsAboveSpecific&&prop.labelsAboveSpecific.length&&typeof prop.labelsAboveSpecific[seq]!=='string'&&typeof prop.labelsAboveSpecific[seq]!=='number'){continue;}
RGraph.SVG.text({object:this,parent:this.svg.all,tag:'labels.above',text:str,x:parseFloat(this.coords2[dataset][i][0])+prop.labelsAboveOffsetx,y:parseFloat(this.coords2[dataset][i][1])+prop.labelsAboveOffsety,halign:prop.labelsAboveHalign,valign:prop.labelsAboveValign,font:prop.labelsAboveFont||prop.textFont,size:typeof prop.labelsAboveSize==='number'?prop.labelsAboveSize:prop.textSize,bold:typeof prop.labelsAboveBold==='boolean'?prop.labelsAboveBold:prop.textBold,italic:typeof prop.labelsAboveItalic==='boolean'?prop.labelsAboveItalic:prop.textItalic,color:prop.labelsAboveColor||prop.textColor,background:prop.labelsAboveBackground||null,padding:prop.labelsAboveBackgroundPadding||0});}
seq--;}}};this.on=function(type,func)
{if(type.substr(0,2)!=='on'){type='on'+type;}
RGraph.SVG.addCustomEventListener(this,type,func);return this;};this.exec=function(func)
{func(this);return this;};this.drawErrorbar=function(opt)
{var linewidth=RGraph.SVG.getErrorbarsLinewidth({object:this,index:opt.index}),color=RGraph.SVG.getErrorbarsColor({object:this,index:opt.sequential}),capwidth=RGraph.SVG.getErrorbarsCapWidth({object:this,index:opt.index}),index=opt.index,dataset=opt.dataset,x=opt.x,y=opt.y,value=this.data[dataset][index];var y=this.getYCoord(y);var max=RGraph.SVG.getErrorbarsMaxValue({object:this,index:opt.sequential});var min=RGraph.SVG.getErrorbarsMinValue({object:this,index:opt.sequential});if(!max&&!min){return;}
var x=this.coords2[dataset][index].x,y=this.coords2[dataset][index].y,halfCapWidth=capwidth/2,y1=this.getYCoord(value+max),y3=this.getYCoord(value-min)===null?y:this.getYCoord(value-min);if(max>0){var errorbarLine=RGraph.SVG.create({svg:this.svg,type:'line',parent:this.svg.all,attr:{x1:x,y1:y,x2:x,y2:y1,stroke:color,'stroke-width':linewidth}});var errorbarCap=RGraph.SVG.create({svg:this.svg,type:'line',parent:this.svg.all,attr:{x1:x-halfCapWidth,y1:y1,x2:x+halfCapWidth,y2:y1,stroke:color,'stroke-width':linewidth}});}
if(typeof min==='number'){var errorbarLine=RGraph.SVG.create({svg:this.svg,type:'line',parent:this.svg.all,attr:{x1:x,y1:y,x2:x,y2:y3,stroke:color,'stroke-width':linewidth}});var errorbarCap=RGraph.SVG.create({svg:this.svg,type:'line',parent:this.svg.all,attr:{x1:x-halfCapWidth,y1:y3,x2:x+halfCapWidth,y2:y3,stroke:color,'stroke-width':linewidth}});}};this.trace=function()
{var opt=arguments[0]||{},frame=1,frames=opt.frames||60,obj=this;this.isTrace=true;this.draw();var clippath=RGraph.SVG.create({svg:this.svg,parent:this.svg.defs,type:'clipPath',attr:{id:'trace-effect-clip'}});var clippathrect=RGraph.SVG.create({svg:this.svg,parent:clippath,type:'rect',attr:{x:0,y:0,width:0,height:this.height}});var iterator=function()
{var width=(frame++)/frames*obj.width;clippathrect.setAttribute("width",width);if(frame<=frames){RGraph.SVG.FX.update(iterator);}else{clippath.parentNode.removeChild(clippath);if(opt.callback){(opt.callback)(obj);}}};iterator();return this;};this.tooltipSubstitutions=function(opt)
{var indexes=RGraph.SVG.sequentialIndexToGrouped(opt.index,this.data);for(var i=0,values=[];i<this.originalData.length;++i){values.push(this.originalData[i][indexes[1]]);}
return{index:indexes[1],dataset:indexes[0],sequentialIndex:opt.index,value:typeof this.data[indexes[0]]==='number'?this.data[indexes[0]]:this.data[indexes[0]][indexes[1]],values:values};};this.positionTooltipStatic=function(args)
{var obj=args.object,e=args.event,tooltip=args.tooltip,index=args.index,svgXY=RGraph.SVG.getSVGXY(obj.svg),coords=this.coords[args.index];args.tooltip.style.left=(svgXY[0]
+coords[0]
-(tooltip.offsetWidth/2))+'px';args.tooltip.style.top=(svgXY[1]
+coords[1]
-tooltip.offsetHeight
-15)+'px';};for(i in conf.options){if(typeof i==='string'){this.set(i,conf.options[i]);}}}
return this;})(window,document);