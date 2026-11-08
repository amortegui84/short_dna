// Full dump of an After Effects template project: every comp, every layer (source, timing, blend mode, track matte, parent,
// switches) and every property that is modified, keyed or driven by an expression (values, keyframes with their ease,
// expressions, effect settings, text fonts and sizes). Use it before rebuilding a brand's template in a builder: names alone
// are not enough (see docs/LEARNINGS.md, "Read the template project in full").
// Usage (via the Motion DNA bridge): set AEP_DUMP_IN and AEP_DUMP_OUT, then $.evalFile this file. It opens the project:
// work on a copy, and save or close the current project first.
(function(){
var OUT = (typeof AEP_DUMP_OUT !== "undefined") ? AEP_DUMP_OUT : Folder.temp.fsName + "/";
app.beginSuppressDialogs();
app.open(new File(AEP_DUMP_IN));
function v2s(v){ if (v===null||v===undefined) return "null"; if (v instanceof Array){var a=[];for(var i=0;i<v.length;i++)a.push(typeof v[i]==="number"?Math.round(v[i]*1000)/1000:v2s(v[i]));return "["+a.join(",")+"]";} if (typeof v==="number") return String(Math.round(v*1000)/1000); if (v instanceof TextDocument){ var s="TEXT{"; try{s+="font="+v.font+";size="+v.fontSize+";fill="+v2s(v.fillColor)+";stroke="+(v.applyStroke?v2s(v.strokeColor)+"/"+v.strokeWidth:"no")+";track="+v.tracking+";lead="+v.leading+";just="+v.justification+";caps="+v.allCaps+";txt="+String(v.text).replace(/[\r\n]+/g," | ").substr(0,120);}catch(e){} return s+"}"; } try { return String(v).substr(0,200);} catch(e){return "?";} }
function easeS(p,k){ try{ var i=p.keyInTemporalEase(k)[0], o=p.keyOutTemporalEase(k)[0]; var it=p.keyInInterpolationType(k), ot=p.keyOutInterpolationType(k); var m={6612:"L",6613:"B",6614:"H"}; return "("+(m[it]||it)+(m[ot]||ot)+" in"+Math.round(i.influence)+"/"+Math.round(i.speed)+" out"+Math.round(o.influence)+"/"+Math.round(o.speed)+")"; }catch(e){return "";} }
function walk(g, path, lines, depth){
  if (depth>12) return;
  for (var i=1;i<=g.numProperties;i++){
    var p=g.property(i); if(!p) continue;
    var nm = path + "/" + p.name;
    if (p.propertyType===PropertyType.PROPERTY){
      var exp=""; try{ if(p.canSetExpression && p.expressionEnabled && p.expression) exp=p.expression; }catch(e){}
      var nk=0; try{nk=p.numKeys;}catch(e){}
      var mod=false; try{mod=p.isModified;}catch(e){}
      if (!(mod||nk||exp)) continue;
      if (p.propertyValueType===PropertyValueType.NO_VALUE) continue;
      var s = nm + " = ";
      if (nk){ var ks=[]; for(var k=1;k<=Math.min(nk,40);k++){ ks.push(Math.round(p.keyTime(k)*1000)/1000+":"+v2s(p.keyValue(k))+easeS(p,k)); } s += "KEYS["+nk+"] "+ks.join(" ; "); }
      else { try{ s += v2s(p.value); }catch(e){ s+="?"; } }
      if (exp) s += "  EXPR{ " + exp.replace(/\r?\n/g," \n ").substr(0,1500) + " }";
      lines.push(s);
    } else {
      var mod2=true; try{ if (p.isModified===false && p.propertyType!==PropertyType.INDEXED_GROUP) {} }catch(e){}
      walk(p, nm, lines, depth+1);
    }
  }
}
var out=[];
for (var ii=1; ii<=app.project.numItems; ii++){
  var it=app.project.item(ii);
  if (it instanceof CompItem){
    out.push("\n######## COMP \""+it.name+"\" "+it.width+"x"+it.height+" "+Math.round(it.duration*1000)/1000+"s fps="+it.frameRate+" bg="+v2s(it.bgColor)+" mb="+it.motionBlur+(it.motionBlur?" shutter="+it.shutterAngle+"/"+it.shutterPhase:""));
    for (var li=1; li<=it.numLayers; li++){
      var L=it.layer(li); var src="";
      try{ if(L.source){ src = (L.source instanceof CompItem?"COMP:":(L.source.mainSource instanceof SolidSource?"SOLID:":"FILE:")) + L.source.name + (L.source.mainSource instanceof SolidSource? " "+v2s(L.source.mainSource.color)+" "+L.source.width+"x"+L.source.height : (L.source.width?" "+L.source.width+"x"+L.source.height:"")); } }catch(e){}
      var kind = L.property("ADBE Text Properties") ? "TEXT" : L.property("ADBE Root Vectors Group") ? "SHAPE" : (L.nullLayer ? "NULL" : (L.source ? "AV" : "CAMERA/LIGHT"));
      var hdr = "\n  ["+li+"] "+kind+" \""+L.name+"\" "+src+" in="+Math.round(L.inPoint*1000)/1000+" out="+Math.round(L.outPoint*1000)/1000+" start="+Math.round(L.startTime*1000)/1000;
      try{ if(L.stretch!==100) hdr+=" stretch="+L.stretch; }catch(e){}
      try{ hdr+=" blend="+L.blendingMode; }catch(e){}
      try{ if(L.trackMatteType && L.trackMatteType!==TrackMatteType.NO_TRACK_MATTE) hdr+=" matte="+L.trackMatteType; if(L.isTrackMatte) hdr+=" IS_MATTE"; }catch(e){}
      try{ if(L.parent) hdr+=" parent="+L.parent.name; }catch(e){}
      try{ if(L.threeDLayer) hdr+=" 3D"; if(!L.enabled) hdr+=" DISABLED"; if(L.adjustmentLayer) hdr+=" ADJ"; if(L.motionBlur) hdr+=" MB"; if(L.timeRemapEnabled) hdr+=" TIMEREMAP"; if (L.guideLayer) hdr+=" GUIDE"; }catch(e){}
      out.push(hdr);
      var lines=[]; walk(L, "", lines, 0);
      for (var q=0;q<lines.length;q++) out.push("     "+lines[q]);
    }
  }
}
var f=new File(OUT+"aep_dump.txt"); f.encoding="UTF-8"; f.open("w"); f.write(out.join("\n")); f.close();
app.endSuppressDialogs(false);
return "ok "+out.length;
})();
