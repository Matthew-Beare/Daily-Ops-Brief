"use strict";

(() => {
  let stagedSnapshot = null;

  function apiReady() { try { return Boolean(apiBase()); } catch (_) { return false; } }
  function text(tag, className, value) { const node=document.createElement(tag); if(className) node.className=className; node.textContent=value; return node; }

  function summaryPlan(plan) {
    const safe = plan?.safe_rows?.length ?? plan?.safe_count ?? 0;
    const review = plan?.needs_review?.length ?? plan?.review_count ?? 0;
    const unknown = plan?.unknown_sheets?.length ?? 0;
    return `Ready to import ${safe} safe row${safe===1?"":"s"}. ${review+unknown ? `${review+unknown} item${review+unknown===1?"":"s"} will wait for review.` : "Nothing ambiguous was found."}`;
  }

  async function previewMagic(snapshotId) {
    const result=await apiJson(`/v1/migrations/${encodeURIComponent(snapshotId)}/magic`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({apply:false})});
    const summary=document.getElementById("migrationPlanSummary"); if(summary) summary.textContent=summaryPlan(result.plan||{});
    const technical=document.getElementById("migrationMagicResult"); if(technical) technical.textContent=JSON.stringify(result.plan,null,2);
    const apply=document.getElementById("migrationMagicApply"); if(apply){apply.disabled=!result.plan?.safe_to_apply;apply.textContent=result.plan?.fully_automatic?"Import now":"Import safe items";}
    markStep(4,result.plan?.safe_to_apply?"ready":"locked");
    return result;
  }

  async function applyMagic() {
    if(!stagedSnapshot) throw new Error("Preview a spreadsheet first.");
    const result=await apiJson(`/v1/migrations/${encodeURIComponent(stagedSnapshot)}/magic`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({apply:true})});
    const needs=(result.result?.needs_review?.length||0)+(result.result?.unknown_sheets?.length||0);
    const summary=document.getElementById("migrationPlanSummary"); if(summary) summary.textContent=needs?`Imported everything MIRA could verify. ${needs} item${needs===1?"":"s"} need your review.`:"Import complete. Everything was verified and applied safely.";
    const technical=document.getElementById("migrationMagicResult"); if(technical) technical.textContent=JSON.stringify(result,null,2);
    setStatus(needs?`Import complete. ${needs} item(s) need review; MIRA did not guess.`:"Import complete and verified.");
    markStep(4,"done");
  }

  function markStep(number,state){const card=document.querySelector(`[data-migration-step='${number}']`);if(card)card.dataset.state=state;document.querySelectorAll("#migrationProgress span").forEach((bar,index)=>bar.classList.toggle("active",index<number&&(state!=="locked"||index<number-1)));}

  function waitForSnapshot(stageButton) {
    if(stageButton.dataset.guidedHook)return; stageButton.dataset.guidedHook="true";
    stageButton.addEventListener("click",()=>{
      let tries=0;const timer=setInterval(()=>{tries+=1;try{const raw=document.getElementById("migrationResult")?.textContent||"{}";const payload=JSON.parse(raw);if(payload.snapshot_uuid){clearInterval(timer);stagedSnapshot=payload.snapshot_uuid;markStep(3,"done");previewMagic(stagedSnapshot).catch(showError);}}catch(_){/* waiting */}if(tries>50)clearInterval(timer);},200);
    });
  }

  function improve() {
    const panel=document.getElementById("panel-migration"); if(!panel||panel.dataset.progressive==="true")return;
    const select=document.getElementById("googleSheetSelect"); const stage=select?.nextElementSibling; const toolbar=select?.previousElementSibling;
    if(!select||!stage||!toolbar)return;
    const google=select.closest(".card"); if(!google)return;
    const buttons=[...toolbar.querySelectorAll("button")]; if(buttons.length<2)return;
    const connect=buttons[0],discover=buttons[1];
    panel.dataset.progressive="true"; waitForSnapshot(stage);

    const heading=google.querySelector("h2"); if(heading) heading.textContent="Bring in your Google data";
    const warning=google.querySelector(".mira-warning"); if(warning) warning.textContent="MIRA previews first and changes nothing until you press Import.";

    const progress=document.createElement("div"); progress.id="migrationProgress"; progress.className="mira-progress"; for(let i=0;i<4;i++)progress.append(document.createElement("span"));
    const makeStep=(number,title,copy)=>{const card=document.createElement("div");card.className="mira-step-card";card.dataset.migrationStep=String(number);card.append(text("div","mira-eyebrow",`Step ${number}`),text("h3","",title),text("p","muted",copy));return card;};
    const one=makeStep(1,"Connect Google",apiReady()?"Give MIRA read-only access for migration.":"Finish setup first. This test app is not connected yet.");
    connect.textContent=apiReady()?"Continue with Google":"Finish setup to connect Google"; connect.classList.add("primary-action"); one.append(connect);
    const two=makeStep(2,"Find your spreadsheets","MIRA will list the Google Sheets you can import."); discover.textContent="Find spreadsheets"; discover.disabled=!apiReady(); two.append(discover);
    const three=makeStep(3,"Choose and preview","Pick a spreadsheet. Previewing still does not import anything."); stage.textContent="Preview spreadsheet"; stage.classList.add("primary-action"); stage.disabled=true; three.append(select,stage);
    const four=makeStep(4,"Import","Only verified rows are applied. Anything ambiguous waits for review."); four.dataset.state="locked"; const plan=text("div","mira-callout","Preview a spreadsheet to see what MIRA can import safely."); plan.id="migrationPlanSummary"; const apply=document.createElement("button");apply.id="migrationMagicApply";apply.className="primary-action";apply.disabled=true;apply.textContent="Import";apply.addEventListener("click",()=>applyMagic().catch(showError));four.append(plan,apply);

    toolbar.remove();
    const warningNode=warning||null; google.replaceChildren(); if(heading)google.append(heading);else google.append(text("h2","","Bring in your Google data")); if(warningNode)google.append(warningNode); google.append(progress,one,two,three,four);
    const technical=document.createElement("details");technical.className="mira-advanced";technical.append(text("summary","","Advanced migration details"));const pre=document.createElement("pre");pre.id="migrationMagicResult";pre.className="mira-code";pre.textContent="No preview yet.";technical.append(pre);google.append(technical);

    select.addEventListener("change",()=>{stage.disabled=!select.value;markStep(3,select.value?"ready":"locked");});
    const optionObserver=new MutationObserver(()=>{if(select.options.length>1){markStep(2,"done");select.disabled=false;}});optionObserver.observe(select,{childList:true});
    markStep(1,apiReady()?"ready":"locked"); markStep(2,apiReady()?"ready":"locked"); markStep(3,"locked");

    [...panel.querySelectorAll(".card")].forEach((card)=>{
      const title=card.querySelector("h2")?.textContent||"";
      if(title.includes("JSON")||title.includes("legacy export")){const details=document.createElement("details");details.className="mira-advanced";details.append(text("summary","","Advanced: import a technical export"));[...card.children].slice(1).forEach(child=>details.append(child));card.replaceChildren(details);}
      if(title==="Migration result"){card.style.display="none";}
    });
  }

  const observer=new MutationObserver(improve);observer.observe(document.documentElement,{childList:true,subtree:true});improve();
})();
