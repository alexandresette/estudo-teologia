#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica direto no index.html ja implantado o mesmo conjunto de mudancas
que foram feitas em build6.py nesta rodada (sem depender dos /tmp
assets que o build6.py completo normalmente precisa pra rodar do
zero -- mesma tecnica ja usada pra adicionar livros novos):

  1. Renomeia o corredor "Livros" -> "Resumo de Livros" (placard + JS).
  2. Remove o auto-close das NOTAS ao clicar fora (inclusive ao virar
     pagina).
  3. Insere o portao de entrada (video em loop + senha) logo no
     <body>, mais o CSS dele antes do </style>.
  4. Acrescenta o roteamento por URL (hash) + os pushState/replaceState
     nas funcoes de navegacao existentes.

Cada substituicao verifica que o texto-ancora aparece exatamente uma
vez antes de trocar, pra nunca aplicar em lugar errado nem silenciosamente
deixar de aplicar.
"""
import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
INDEX_PATH = os.path.join(REPO_ROOT, "index.html")
GATE_DIR = os.path.join(HERE, "gate")


def b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def replace_once(data, old, new, label):
    n = data.count(old)
    if n != 1:
        raise SystemExit("ANCORA '%s': esperava 1 ocorrencia, achei %d" % (label, n))
    return data.replace(old, new, 1)


def main():
    data = open(INDEX_PATH, encoding="utf-8").read()
    before_len = len(data)

    # ---- 1) renomear corredor ----
    data = replace_once(
        data,
        '<div class="corridor-zone" data-corridor="livros" tabindex="0" role="button" aria-label="Entrar no corredor Livros" onclick="enterCorridor(\'livros\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();enterCorridor(\'livros\')}">\n              <div class="placard-hang"><span class="n">3</span>Livros</div>',
        '<div class="corridor-zone" data-corridor="livros" tabindex="0" role="button" aria-label="Entrar no corredor Resumo de Livros" onclick="enterCorridor(\'livros\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();enterCorridor(\'livros\')}">\n              <div class="placard-hang"><span class="n">3</span>Resumo de Livros</div>',
        "placard Livros",
    )
    data = replace_once(
        data,
        "livros:{num:3,title:'Livros',items:LIVROS}",
        "livros:{num:3,title:'Resumo de Livros',items:LIVROS}",
        "CORRIDORS.livros.title",
    )

    # ---- 2) notas nao fecham mais ao clicar fora / virar pagina ----
    data = replace_once(
        data,
        "  document.addEventListener('click', e=>{\n"
        "    const panel=document.getElementById('notesPanel');\n"
        "    if(panel.classList.contains('open') && !panel.contains(e.target) && e.target!==notesBtn){\n"
        "      closeNotes();\n"
        "    }\n"
        "  }, true);\n"
        "\n"
        "  /* ============================================================",
        "  /* Antes havia aqui um listener global de \"clique fora fecha o painel\",\n"
        "     mas ele fechava as NOTAS sempre que o usuário clicava nos botões de\n"
        "     flip ou na borda da página pra virar -- ou seja, escrever uma\n"
        "     anotação e virar a página perdia o painel aberto sem nenhuma\n"
        "     intenção de fechar. As notas agora só fecham por ação explícita: o\n"
        "     X do painel, o toggle do botão NOTAS, ou Esc -- assim dá pra ir\n"
        "     anotando enquanto lê e passa as páginas. */\n"
        "\n"
        "  /* ============================================================",
        "listener global de notas",
    )

    # ---- 3) portao (gate): CSS ----
    gate_css = """
/* ============ portão de entrada (fora da biblioteca, no alto do monte) ============ */
#gate{position:fixed;inset:0;z-index:500;background:#0a0703;overflow:hidden;opacity:1;transition:opacity .85s ease}
#gate.leaving{opacity:0;pointer-events:none}
#gateVideo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#0a0703}
.gate-veil{position:absolute;inset:0;z-index:1;pointer-events:none;
  background:
    radial-gradient(120% 90% at 50% 82%, rgba(8,5,2,.1) 0%, rgba(8,5,2,.7) 68%, rgba(6,4,2,.94) 100%),
    linear-gradient(180deg, rgba(6,4,2,.6) 0%, rgba(6,4,2,.05) 32%, rgba(6,4,2,.08) 55%, rgba(6,4,2,.55) 100%);
}
.gate-scroll{position:relative;z-index:2;height:100%;display:flex;align-items:flex-end;justify-content:center;padding:0 22px calc(8vh + 18px);text-align:center}
.gate-content{max-width:580px}
.gate-kicker{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--gold-soft);opacity:.9;margin-bottom:16px}
.gate-title{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-size:clamp(30px,5vw,50px);font-weight:700;color:#f6ecd6;text-shadow:0 10px 34px rgba(0,0,0,.75);margin-bottom:16px;letter-spacing:-.01em}
.gate-verse{font-family:"Iowan Old Style",Georgia,serif;font-style:italic;font-size:clamp(13px,1.5vw,16px);line-height:1.65;color:#e7d9b6;opacity:.92;margin-bottom:32px;text-shadow:0 4px 18px rgba(0,0,0,.65)}
#gateKnockBtn{background:rgba(243,231,201,.1);border:1px solid rgba(217,185,104,.45);color:#f6ecd6;border-radius:999px;padding:15px 36px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:12.5px;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;backdrop-filter:blur(6px);transition:.2s}
#gateKnockBtn:hover{background:rgba(217,185,104,.24);border-color:var(--gold-soft)}
#gateForm{display:none;gap:10px;justify-content:center;flex-wrap:wrap}
#gateForm.show{display:flex}
#gatePass{background:rgba(6,4,2,.45);border:1px solid rgba(217,185,104,.4);color:#f6ecd6;border-radius:999px;padding:14px 22px;font-size:14px;min-width:230px;text-align:center;letter-spacing:.05em;font-family:"Helvetica Neue",Arial,sans-serif}
#gatePass::placeholder{color:rgba(246,236,214,.4)}
#gatePass:focus{outline:none;border-color:var(--gold-soft)}
#gateForm button[type=submit]{background:var(--gold);border:1px solid var(--gold-soft);color:#1a1204;border-radius:999px;padding:14px 26px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;font-weight:700}
#gateForm button[type=submit]:hover{background:var(--gold-soft)}
#gateError{min-height:20px;margin-top:16px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:12.5px;color:#e79a86;letter-spacing:.03em;opacity:0;transition:opacity .2s}
#gateError.show{opacity:1}
#gate.shake .gate-content{animation:gateShake .4s ease}
@keyframes gateShake{0%,100%{transform:translateX(0)}20%{transform:translateX(-9px)}40%{transform:translateX(9px)}60%{transform:translateX(-6px)}80%{transform:translateX(6px)}}
@media(max-width:600px){.gate-scroll{padding-bottom:9vh}#gatePass{min-width:180px}}
"""
    data = replace_once(
        data,
        "@media(max-width:600px){\n  #counter{top:14px;right:14px;font-size:11px}\n}\n</style>",
        "@media(max-width:600px){\n  #counter{top:14px;right:14px;font-size:11px}\n}\n" + gate_css + "</style>",
        "fim do CSS (antes de </style>)",
    )

    # ---- 3b) portao (gate): HTML + video/poster embutidos ----
    gate_video_b64 = b64_of(os.path.join(GATE_DIR, "gate-loop.mp4"))
    gate_poster_b64 = b64_of(os.path.join(GATE_DIR, "gate-poster.jpg"))
    gate_html = (
        "<div id=\"gate\">\n"
        "  <video id=\"gateVideo\" autoplay muted loop playsinline preload=\"auto\" poster=\"data:image/jpeg;base64,%s\">\n"
        "    <source src=\"data:video/mp4;base64,%s\" type=\"video/mp4\">\n"
        "  </video>\n"
        "  <div class=\"gate-veil\"></div>\n"
        "  <div class=\"gate-scroll\">\n"
        "    <div class=\"gate-content\">\n"
        "      <div class=\"gate-kicker\">Êxodo 24:15–ureter18</div>\n"
    ) % (gate_poster_b64, gate_video_b64)
    # (placeholder text above gets replaced below with the real verse block --
    # built separately to avoid Python %-escaping headaches with braces/quotes)
    gate_html = (
        "<div id=\"gate\">\n"
        "  <video id=\"gateVideo\" autoplay muted loop playsinline preload=\"auto\" poster=\"data:image/jpeg;base64,"
        + gate_poster_b64 + "\">\n"
        "    <source src=\"data:video/mp4;base64," + gate_video_b64 + "\" type=\"video/mp4\">\n"
        "  </video>\n"
        "  <div class=\"gate-veil\"></div>\n"
        "  <div class=\"gate-scroll\">\n"
        "    <div class=\"gate-content\">\n"
        "      <div class=\"gate-kicker\">Êxodo 24:15&ndash;18</div>\n"
        "      <h1 class=\"gate-title\">Sobe ao monte</h1>\n"
        "      <p class=\"gate-verse\">&ldquo;Então Moisés subiu ao monte, e a nuvem cobriu o monte... "
        "e a aparência da glória do Senhor era como um fogo consumidor no cume do monte, "
        "aos olhos dos filhos de Israel. E entrou Moisés no meio da nuvem, depois que subiu ao monte.&rdquo;</p>\n"
        "      <button id=\"gateKnockBtn\" type=\"button\" onclick=\"gateReveal()\">Bater à porta</button>\n"
        "      <form id=\"gateForm\" onsubmit=\"return gateSubmit(event)\" autocomplete=\"off\">\n"
        "        <input type=\"password\" id=\"gatePass\" name=\"gatePass\" placeholder=\"a senha para entrar\" "
        "autocomplete=\"off\" autocapitalize=\"off\" autocorrect=\"off\" spellcheck=\"false\">\n"
        "        <button type=\"submit\">Entrar</button>\n"
        "      </form>\n"
        "      <div id=\"gateError\"></div>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
    )
    gate_precheck = (
        "<script>(function(){try{if(sessionStorage.getItem('estudoGateUnlocked')==='1'){"
        "document.write('<style>#gate{display:none!important}</style>');}}catch(e){}})();</script>\n"
    )
    old_body_open = data.count("<body>\n<script>")
    if old_body_open != 1:
        raise SystemExit("ANCORA '<body>' + script: esperava 1 ocorrencia, achei %d" % old_body_open)
    data = data.replace("<body>\n<script>", "<body>\n" + gate_precheck + gate_html + "<script>", 1)

    # ---- 4) roteamento por URL + pushState nas funcoes de navegacao ----
    data = replace_once(
        data,
        "function enterCorridor(corId){\n    if(curCorridor) return;\n    curCorridor=corId;\n    sfxWhoosh();",
        "function enterCorridor(corId){\n    if(curCorridor) return;\n    curCorridor=corId;\n    history.pushState(null,'','#/corredor/'+corId);\n    sfxWhoosh();",
        "enterCorridor",
    )
    data = replace_once(
        data,
        "function exitCorridor(){\n    if(!curCorridor) return;\n    curCorridor=null;\n    sfxWhoosh();",
        "function exitCorridor(){\n    if(!curCorridor) return;\n    curCorridor=null;\n    history.pushState(null,'','#/');\n    sfxWhoosh();",
        "exitCorridor",
    )
    data = replace_once(
        data,
        'function openBook(id){\n    if(curDeck) return;\n    const originEl=document.querySelector(\'.bcover[data-id="\'+id+\'"]\');\n    if(!originEl) return;\n    sfxOpen();',
        'function openBook(id){\n    if(curDeck) return;\n    const originEl=document.querySelector(\'.bcover[data-id="\'+id+\'"]\');\n    if(!originEl) return;\n    history.pushState(null,\'\',\'#/livro/\'+id);\n    sfxOpen();',
        "openBook",
    )
    data = replace_once(
        data,
        "    if(!curDeck||!flips[curDeck]) return;\n"
        "    const pf=flips[curDeck];\n"
        "    pf.turnToPage(0);\n"
        "    setTimeout(()=>{ if(curDeck&&flips[curDeck]===pf) pf.turnToPage(0); }, 700);\n"
        "  }\n"
        "\n"
        "  function goShelf(){\n"
        "    if(!curDeck) return;\n"
        "    const id=curDeck;",
        "    if(!curDeck||!flips[curDeck]) return;\n"
        "    const pf=flips[curDeck];\n"
        "    pf.turnToPage(0);\n"
        "    history.replaceState(null,'','#/livro/'+curDeck+'/1');\n"
        "    setTimeout(()=>{ if(curDeck&&flips[curDeck]===pf) pf.turnToPage(0); }, 700);\n"
        "  }\n"
        "\n"
        "  function goShelf(){\n"
        "    if(!curDeck) return;\n"
        "    const id=curDeck;\n"
        "    const backCorridor=corridorOf(id);\n"
        "    history.pushState(null,'', backCorridor?('#/corredor/'+backCorridor):'#/');",
        "goBookStart+goShelf",
    )
    data = replace_once(
        data,
        "pf.on('flip',(e)=>{ if(curDeck===id){ updateCounter(id); sfxPage(); } });",
        "pf.on('flip',(e)=>{\n"
        "      if(curDeck===id){\n"
        "        updateCounter(id); sfxPage();\n"
        "        history.replaceState(null,'','#/livro/'+id+'/'+(pf.getCurrentPageIndex()+1));\n"
        "      }\n"
        "    });",
        "pf.on(flip)",
    )

    # ---- 4b) setas do teclado continuam virando página com as NOTAS
    # abertas (só ficam bloqueadas se o foco estiver dentro do próprio
    # campo de anotação, senão dá pra usar o teclado pra virar página e
    # ir anotando ao mesmo tempo) ----
    data = replace_once(
        data,
        "  document.addEventListener('keydown',e=>{\n"
        "    if(document.getElementById('notesPanel').classList.contains('open')){ if(e.key==='Escape')closeNotes(); return; }\n"
        "    if(document.getElementById('idx').classList.contains('open')){ if(e.key==='Escape')closeIdx(); return; }",
        "  document.addEventListener('keydown',e=>{\n"
        "    if(document.getElementById('notesPanel').classList.contains('open')){\n"
        "      if(e.key==='Escape'){ closeNotes(); return; }\n"
        "      const typingInNotes=document.activeElement===document.getElementById('notesBody');\n"
        "      if(!typingInNotes && curDeck){\n"
        "        if(e.key==='ArrowRight'){flipNext();return;}\n"
        "        if(e.key==='ArrowLeft'){flipPrev();return;}\n"
        "      }\n"
        "      return;\n"
        "    }\n"
        "    if(document.getElementById('idx').classList.contains('open')){ if(e.key==='Escape')closeIdx(); return; }",
        "keydown com notas abertas",
    )

    routing_js = """
  /* ============================================================
     Portão de entrada -- a área de fora da biblioteca, uma porta no
     topo de um monte (referência a Moisés subindo o monte Sinai pra
     entrar na presença de Deus). Fica por cima de tudo (z-index alto)
     até a senha certa ser digitada; o que existe por baixo (a rota
     certa, veja mais abaixo) já é montado normalmente, só fica
     escondido atrás da cortina do portão até o desbloqueio.
     ============================================================ */
  const GATE_PASSWORD='Jesus';
  const gateEl=document.getElementById('gate');
  function gateReveal(){
    document.getElementById('gateKnockBtn').style.display='none';
    document.getElementById('gateForm').classList.add('show');
    document.getElementById('gatePass').focus();
  }
  function gateSubmit(e){
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
  }
  (function gateInit(){
    let unlocked=false;
    try{ unlocked=sessionStorage.getItem('estudoGateUnlocked')==='1'; }catch(ex){}
    if(unlocked){
      gateEl.style.display='none';
      const video=document.getElementById('gateVideo');
      try{ video.pause(); }catch(ex){}
    }
  })();

  /* ============================================================
     Roteamento por URL (hash) -- cada view tem seu próprio endereço,
     então dá pra recarregar, voltar/avançar no navegador ou mandar um
     link direto pra um corredor ou um livro (com página, opcional):
       #/                          -> página inicial (corredores)
       #/corredor/<id>             -> estante daquele corredor
       #/livro/<id>                -> livro aberto (primeira página)
       #/livro/<id>/<pagina>        -> livro aberto numa página específica
     As funções normais (enterCorridor, openBook, goShelf...) continuam
     fazendo a animação de sempre E empurram a URL nova via
     history.pushState. Carregar a página direto num link, ou usar
     voltar/avançar do navegador, cai em applyRoute(), que monta o
     mesmo estado só que instantâneo (sem replay de animação de voo de
     capa nem de whoosh de corredor). */
  function corridorOf(id){
    for(const key in CORRIDORS){ if(CORRIDORS[key].items.some(it=>it.id===id)) return key; }
    return null;
  }
  function routeParse(hash){
    const h=(hash||'').replace(/^#\\/?/,'');
    if(!h) return {view:'landing'};
    const parts=h.split('/').filter(Boolean);
    if(parts[0]==='corredor' && parts[1]) return {view:'corredor', corId:parts[1]};
    if(parts[0]==='livro' && parts[1]) return {view:'livro', id:parts[1], page:parts[2]?parseInt(parts[2],10):null};
    return {view:'landing'};
  }
  function instantShowLanding(){
    curCorridor=null;
    viewCorridor.classList.remove('show','leaving','entering-from');
    viewLanding.classList.remove('leaving','entering-from');
    viewLanding.classList.add('show');
  }
  function instantShowCorridor(corId){
    curCorridor=corId;
    populateCorridor(corId);
    viewLanding.classList.remove('show','leaving','entering-from');
    viewCorridor.classList.remove('leaving','entering-from');
    viewCorridor.classList.add('show');
  }
  function instantLeaveReader(){
    if(!curDeck) return;
    closeIdx(); closeNotes();
    reader.classList.remove('shown','show');
    showChrome(false);
    curDeck=null;
  }
  function applyRoute(){
    const r=routeParse(location.hash);
    if(r.view==='livro' && containers[r.id]){
      const cid=corridorOf(r.id);
      if(curDeck && curDeck!==r.id) instantLeaveReader();
      if(cid) instantShowCorridor(cid); else instantShowLanding();
      shelf.classList.add('show');
      if(curDeck!==r.id){ enterReader(r.id); }
      if(r.page){
        requestAnimationFrame(()=>requestAnimationFrame(()=>{
          if(flips[r.id]) flips[r.id].turnToPage(Math.max(0,r.page-1));
        }));
      }
      return;
    }
    if(curDeck) instantLeaveReader();
    shelf.classList.add('show');
    if(r.view==='corredor' && CORRIDORS[r.corId]){
      instantShowCorridor(r.corId);
      return;
    }
    instantShowLanding();
    if(!location.hash) history.replaceState(null,'','#/');
  }
  window.addEventListener('popstate', applyRoute);
  window.addEventListener('hashchange', applyRoute);
  applyRoute();
"""
    # NOTA: o index.html implantado ainda não tem o player de música
    # (esse trecho existe em build6.py mas nunca foi aplicado aqui via
    # patch), então a âncora do fim do script é o bloco de seleção de
    # texto (guardTextSelection), que é o que realmente precede
    # </script> no arquivo real.
    data = replace_once(
        data,
        "  readerStageEl.addEventListener('mousedown', guardTextSelection, true);\n"
        "  readerStageEl.addEventListener('touchstart', guardTextSelection, true);\n"
        "</script>",
        "  readerStageEl.addEventListener('mousedown', guardTextSelection, true);\n"
        "  readerStageEl.addEventListener('touchstart', guardTextSelection, true);\n"
        + routing_js + "</script>",
        "fim do script (antes de </script>)",
    )

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(data)
    print("index.html: %d -> %d chars" % (before_len, len(data)))
    print("OK.")


if __name__ == "__main__":
    main()
