/* ============================================================
   Biblioteca de Estudos -- engine compartilhado entre as páginas
   (landing, corredor/*.html, livro/*.html). Cada página é um
   arquivo HTML de verdade agora, então este script não faz mais
   roteamento por hash nem troca de "view" dentro de um só
   documento -- cada coisa que antes era enterCorridor/openBook/
   goShelf virou navegação real (<a href>), e o que sobra aqui é só
   o que continua sendo comportamento DENTRO de uma página: portão
   de entrada, efeitos sonoros, anotações, e o motor do flipbook
   (quando a página é a leitura de um livro).
   ============================================================ */
(function(){
  "use strict";
  const REL = document.body.dataset.rel || '';

  /* ============================================================
     Efeitos sonoros -- sintetizados na hora via Web Audio, sem
     nenhum arquivo de áudio externo. Ligar/desligar persiste em
     localStorage (por origem, então vale pro site inteiro,
     qualquer página).
     ============================================================ */
  let sfxCtx=null, sfxOn=true;
  try{ sfxOn = localStorage.getItem('bibliotecaSfxOn')!=='0'; }catch(err){}

  function sfxEnsureCtx(){
    if(!sfxCtx){
      try{ sfxCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(err){ return null; }
    }
    if(sfxCtx.state==='suspended'){ sfxCtx.resume(); }
    return sfxCtx;
  }
  function sfxTone(freqStart,freqEnd,dur,peak,type,delay){
    if(!sfxOn) return;
    const ctx=sfxEnsureCtx(); if(!ctx) return;
    const t0=ctx.currentTime+(delay||0);
    const osc=ctx.createOscillator(), gain=ctx.createGain();
    osc.type=type||'sine';
    osc.frequency.setValueAtTime(freqStart,t0);
    osc.frequency.exponentialRampToValueAtTime(Math.max(freqEnd,1),t0+dur);
    gain.gain.setValueAtTime(0.0001,t0);
    gain.gain.exponentialRampToValueAtTime(peak,t0+dur*0.18);
    gain.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    osc.connect(gain); gain.connect(ctx.destination);
    osc.start(t0); osc.stop(t0+dur+0.03);
  }
  function sfxNoise(dur,peak,filterFreq,delay){
    if(!sfxOn) return;
    const ctx=sfxEnsureCtx(); if(!ctx) return;
    const t0=ctx.currentTime+(delay||0);
    const len=Math.max(1,Math.floor(ctx.sampleRate*dur));
    const buf=ctx.createBuffer(1,len,ctx.sampleRate);
    const data=buf.getChannelData(0);
    for(let i=0;i<len;i++){ data[i]=(Math.random()*2-1)*(1-i/len); }
    const src=ctx.createBufferSource(); src.buffer=buf;
    const filter=ctx.createBiquadFilter(); filter.type='bandpass'; filter.frequency.value=filterFreq||1800; filter.Q.value=0.7;
    const gain=ctx.createGain();
    gain.gain.setValueAtTime(0.0001,t0);
    gain.gain.exponentialRampToValueAtTime(peak,t0+dur*0.12);
    gain.gain.exponentialRampToValueAtTime(0.0001,t0+dur);
    src.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
    src.start(t0);
  }
  function sfxHover(){ sfxTone(1050,1400,0.05,0.02,'sine'); }
  function sfxClick(){ sfxTone(720,300,0.09,0.06,'triangle'); }
  function sfxPage(){ sfxNoise(0.26,0.05,2200); }
  function sfxOpen(){ sfxTone(220,440,0.22,0.045,'sine'); sfxNoise(0.3,0.03,2600,0.05); }
  function sfxClose(){ sfxTone(440,180,0.2,0.045,'sine'); }
  function sfxWhoosh(){ sfxNoise(0.35,0.035,1400); }

  function setSfxOn(on){
    sfxOn=on;
    try{ localStorage.setItem('bibliotecaSfxOn', on?'1':'0'); }catch(err){}
    const btn=document.getElementById('sfxBtn');
    if(btn) btn.classList.toggle('off', !on);
  }
  window.toggleSfx=function(){ setSfxOn(!sfxOn); if(sfxOn) sfxClick(); };
  setSfxOn(sfxOn);

  const SFX_SELECTOR='.bcover,.corridor-zone,.flipbtn,#backBtn,#homeBtn,#menuBtn,.corridorExitBtn,#idx .item,#idx .close,#sfxBtn,#notesBtn,#notesPanel .toolbtn,#notesPanel .notes-close,.gateExitBtn';
  let sfxLastHoverEl=null;
  document.addEventListener('mouseover',e=>{
    const el=e.target.closest(SFX_SELECTOR);
    if(el && el!==sfxLastHoverEl){ sfxLastHoverEl=el; sfxHover(); }
    else if(!el){ sfxLastHoverEl=null; }
  },true);
  document.addEventListener('click',e=>{
    if(e.target.closest(SFX_SELECTOR)) sfxClick();
  },true);
  /* navegação de corredor/livro passou a ser <a href> de verdade --
     o whoosh/open continuam tocando no instante do clique, antes do
     navegador trocar de página. */
  document.addEventListener('click',e=>{
    if(e.target.closest('.corridor-zone')) sfxWhoosh();
    if(e.target.closest('.bcover:not(.placeholder)')) sfxOpen();
    if(e.target.closest('#backBtn')) sfxClose();
  },true);

  /* ============================================================
     Portão de entrada -- mesma mecânica de antes, só que "Sair"
     agora é navegação real de volta pra index.html (cada página
     confere sessionStorage no carregamento, igual antes).
     ============================================================ */
  const GATE_PASSWORD='Jesus';
  const gateEl=document.getElementById('gate');
  if(gateEl){
    window.gateReveal=function(){
      document.getElementById('gateKnockBtn').style.display='none';
      document.getElementById('gateForm').classList.add('show');
      document.getElementById('gatePass').focus();
    };
    window.gateSubmit=function(e){
      e.preventDefault();
      const input=document.getElementById('gatePass');
      const err=document.getElementById('gateError');
      if(input.value===GATE_PASSWORD){
        try{ sessionStorage.setItem('estudoGateUnlocked','1'); }catch(ex){}
        err.classList.remove('show');
        sfxOpen();
        gateEl.classList.add('leaving');
        const video=document.getElementById('gateVideo');
        setTimeout(()=>{
          gateEl.style.display='none';
          try{ video.pause(); }catch(ex){}
        }, 900);
      } else {
        err.textContent='Essa não é a senha para entrar.';
        err.classList.add('show');
        gateEl.classList.remove('shake');
        void gateEl.offsetWidth;
        gateEl.classList.add('shake');
        input.value='';
        input.focus();
      }
      return false;
    };
    (function gateInit(){
      let unlocked=false;
      try{ unlocked=sessionStorage.getItem('estudoGateUnlocked')==='1'; }catch(ex){}
      if(unlocked){
        gateEl.style.display='none';
        const video=document.getElementById('gateVideo');
        try{ video.pause(); }catch(ex){}
      }
    })();
  }
  window.exitToGate=function(){
    try{ sessionStorage.removeItem('estudoGateUnlocked'); }catch(ex){}
    location.href = REL + 'index.html';
  };

  /* ============================================================
     Motor do flipbook -- só roda em páginas de livro (existe
     #reader com data-book-id). Cada página de livro contém só o
     próprio livro, então não tem mais curDeck/containers/troca
     entre livros: BOOK_ID é fixo pra vida da página.
     ============================================================ */
  const reader=document.getElementById('reader');
  if(reader){
    const BOOK_ID = reader.dataset.bookId;
    const container = document.getElementById('book-'+BOOK_ID);
    const readerStageEl=document.querySelector('.reader-stage');
    const bar=document.getElementById('bar');
    const counter=document.getElementById('counter');
    const notesBtn=document.getElementById('notesBtn');
    let pf=null;

    function updateCounter(){
      if(!pf) return;
      const cur=pf.getCurrentPageIndex()+1;
      const total=pf.getPageCount();
      if(counter) counter.textContent=String(cur).padStart(2,'0')+' / '+String(total).padStart(2,'0');
      if(bar) bar.style.width=(cur/total*100)+'%';
    }

    function ensureFlip(){
      if(pf) return pf;
      pf=new St.PageFlip(container, {
        width:460, height:640, size:'stretch',
        minWidth:260, maxWidth:760, minHeight:360, maxHeight:920,
        showCover:true, usePortrait:true, maxShadowOpacity:0.45,
        mobileScrollSupport:false, flippingTime:650,
        showPageCorners:false
      });
      container.querySelectorAll('.page.cover-page, .page.devo-cover')
        .forEach(p=>{ p.dataset.density='hard'; });
      pf.loadFromHTML(container.querySelectorAll('.page'));
      pf.on('flip',()=>{
        updateCounter(); sfxPage();
        history.replaceState(null,'','#'+(pf.getCurrentPageIndex()+1));
      });
      let hardWatch=null;
      pf.on('changeState',(e)=>{
        if(hardWatch){ cancelAnimationFrame(hardWatch); hardWatch=null; }
        if(e.data==='read'){ readerStageEl.classList.remove('flip-live'); return; }
        const tick=()=>{
          const widths=[...container.querySelectorAll('.stf__item')]
            .filter(el=>getComputedStyle(el).display!=='none')
            .map(el=>el.getBoundingClientRect().width);
          const minW=widths.length?Math.min(...widths):999;
          readerStageEl.classList.toggle('flip-live', minW<12);
          hardWatch=requestAnimationFrame(tick);
        };
        tick();
      });
      return pf;
    }

    window.flipNext=function(){ if(pf) pf.flipNext(); };
    window.flipPrev=function(){ if(pf) pf.flipPrev(); };
    window.goBookStart=function(){
      if(!pf) return;
      pf.turnToPage(0);
      history.replaceState(null,'','#1');
      setTimeout(()=>{ if(pf) pf.turnToPage(0); }, 700);
    };
    window.openIdx=function(){
      const idx=document.getElementById('idx');
      if(idx) idx.classList.add('open');
    };
    window.closeIdx=function(){
      const idx=document.getElementById('idx');
      if(idx) idx.classList.remove('open');
    };
    window.jumpTo=function(folio){
      if(pf) pf.flip(folio-1);
      window.closeIdx();
    };

    /* ---- notas (por livro, contenteditable, persistidas por navegador) ---- */
    function notesKey(){ return 'estudoNotas_'+BOOK_ID; }
    function notesHasContent(){
      const v=localStorage.getItem(notesKey());
      return !!(v && v.replace(/<[^>]*>/g,'').trim().length);
    }
    function notesRefreshDot(){
      if(notesBtn) notesBtn.classList.toggle('has-note', notesHasContent());
    }
    let notesSaveTimer=null;
    function notesStatus(msg,show){
      const el=document.getElementById('notesStatus');
      if(!el) return;
      el.textContent=msg;
      el.classList.toggle('show',!!show);
    }
    window.openNotes=function(){
      const body=document.getElementById('notesBody');
      body.innerHTML=localStorage.getItem(notesKey())||'';
      document.getElementById('notesPanel').classList.add('open');
      document.body.classList.add('notes-open');
      notesStatus('',false);
      setTimeout(()=>body.focus(),260);
    };
    window.closeNotes=function(){
      const p=document.getElementById('notesPanel');
      if(p) p.classList.remove('open');
      document.body.classList.remove('notes-open');
    };
    window.toggleNotes=function(){
      document.getElementById('notesPanel').classList.contains('open') ? window.closeNotes() : window.openNotes();
    };
    function notesSave(){
      const body=document.getElementById('notesBody');
      localStorage.setItem(notesKey(), body.innerHTML);
      notesRefreshDot();
      notesStatus('salvo',true);
      clearTimeout(notesSaveTimer);
      notesSaveTimer=setTimeout(()=>notesStatus('',false),1400);
    }
    function notesUpdateToolbarState(){
      ['bold','italic','underline'].forEach(cmd=>{
        const btn=document.querySelector('#notesPanel .toolbtn[data-cmd="'+cmd+'"]');
        if(btn) btn.classList.toggle('active', document.queryCommandState(cmd));
      });
    }
    const notesBodyEl=document.getElementById('notesBody');
    if(notesBodyEl){
      notesBodyEl.addEventListener('input', ()=>{ clearTimeout(notesSaveTimer); notesSaveTimer=setTimeout(notesSave,500); });
      document.querySelectorAll('#notesPanel .toolbtn[data-cmd]').forEach(btn=>{
        btn.addEventListener('mousedown', e=>e.preventDefault());
        btn.addEventListener('click', ()=>{ document.execCommand(btn.dataset.cmd); notesBodyEl.focus(); notesUpdateToolbarState(); notesSave(); });
      });
      document.querySelectorAll('#notesPanel .toolbtn[data-block]').forEach(btn=>{
        btn.addEventListener('mousedown', e=>e.preventDefault());
        btn.addEventListener('click', ()=>{ document.execCommand('formatBlock', false, '<'+btn.dataset.block+'>'); notesBodyEl.focus(); notesSave(); });
      });
      const copyBtn=document.getElementById('notesCopyBtn');
      if(copyBtn) copyBtn.addEventListener('click', ()=>{
        const text=notesBodyEl.innerText.trim();
        if(!text) return;
        if(navigator.clipboard) navigator.clipboard.writeText(text).then(()=>notesStatus('copiado',true)).catch(()=>{});
      });
      document.addEventListener('selectionchange', ()=>{
        if(document.getElementById('notesPanel').classList.contains('open') && document.activeElement===notesBodyEl){
          notesUpdateToolbarState();
        }
      });
    }
    notesRefreshDot();

    /* ---- seleção de texto dentro do livro, sem perder o "arrastar pra virar" ---- */
    function isFlipZoneTarget(t){
      if(!t || t.nodeType!==1) return true;
      if(t.tagName==='IMG') return true;
      if(t.classList && (t.classList.contains('page') || t.classList.contains('page-inner'))) return true;
      if(t.closest && t.closest('.folio,.pagehead')) return true;
      return false;
    }
    function guardTextSelection(e){
      if(!isFlipZoneTarget(e.target)) e.stopPropagation();
    }
    readerStageEl.addEventListener('mousedown', guardTextSelection, true);
    readerStageEl.addEventListener('touchstart', guardTextSelection, true);

    document.addEventListener('keydown',e=>{
      if(document.getElementById('notesPanel') && document.getElementById('notesPanel').classList.contains('open')){
        if(e.key==='Escape'){ window.closeNotes(); return; }
        const typingInNotes=document.activeElement===document.getElementById('notesBody');
        if(!typingInNotes){
          if(e.key==='ArrowRight'){window.flipNext();return;}
          if(e.key==='ArrowLeft'){window.flipPrev();return;}
        }
        return;
      }
      if(document.getElementById('idx') && document.getElementById('idx').classList.contains('open')){
        if(e.key==='Escape') window.closeIdx();
        return;
      }
      if(e.key==='Escape'){ const b=document.getElementById('backBtn'); if(b) location.href=b.getAttribute('href'); return; }
      if(e.key==='ArrowRight'){window.flipNext();}
      if(e.key==='ArrowLeft'){window.flipPrev();}
      if(e.key.toLowerCase()==='m') window.openIdx();
      if(e.key.toLowerCase()==='n') window.openNotes();
    });

    ensureFlip();
    updateCounter();
    const hashPage=parseInt((location.hash||'').replace('#',''),10);
    if(hashPage && hashPage>1){
      requestAnimationFrame(()=>requestAnimationFrame(()=>{ pf.turnToPage(Math.max(0,hashPage-1)); }));
    }
  }
})();
